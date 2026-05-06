import cv2
import glob
import time
import threading
from ultralytics import YOLO

class VideoGet:
    """
    Classe que lê frames da câmera em uma thread separada para reduzir o delay.
    Sempre mantém o frame mais recente disponível, descartando o buffer antigo.
    """
    def __init__(self, src):
        self.stream = cv2.VideoCapture(src)
        # Tenta ler o primeiro frame
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):    
        t = threading.Thread(target=self.get, args=(), daemon=True)
        t.start()
        return self

    def get(self):
        while not self.stopped:
            grabbed, frame = self.stream.read()
            if not grabbed:
                self.stopped = True
            else:
                with self.lock:
                    self.grabbed = grabbed
                    self.frame = frame

    def read(self):
        with self.lock:
            return self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()

def encontrar_webcam_usb():
    """
    Tenta encontrar a webcam USB varrendo os índices de 1 a 4.
    Pula o índice 0 (geralmente a câmera nativa do notebook).
    Retorna o índice da primeira câmera USB encontrada, ou 0 se nenhuma for encontrada.
    """
    print("Procurando webcam USB nos índices 1, 2, 3, 4...")
    for i in range(1, 5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # CAP_DSHOW é mais estável no Windows
        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            if ret:
                print(f"  -> Webcam USB encontrada no índice {i}!")
                return i
        else:
            cap.release()
    print("  -> Nenhuma webcam USB encontrada nos índices 1-4. Usando índice 0 (câmera nativa).")
    return 0

def main():
    # Busca automaticamente qualquer arquivo de modelo (.pt) na pasta atual
    arquivos_pt = glob.glob('*.pt')
    
    if not arquivos_pt:
        print("Erro: Nenhum arquivo de modelo (terminado em .pt) foi encontrado na pasta atual.")
        return

    modelo_path = arquivos_pt[0]
    print(f"Carregando o modelo '{modelo_path}'...")
    try:
        model = YOLO(modelo_path)
        # Otimização Torch para CPU
        import torch
        torch.set_num_threads(4)
        # Aquece o modelo para evitar lentidão no primeiro frame
        model.predict(source=None, imgsz=320, verbose=False)
        print("Modelo carregado com sucesso!")
    except Exception as e:
        print(f"Erro ao carregar o modelo: {e}")
        return

    # Detecta automaticamente a webcam USB (índice 1+), evitando a câmera nativa (índice 0)
    indice_cam = encontrar_webcam_usb()
    print(f"Conectando à câmera no índice {indice_cam}...")
    
    # Inicia a captura em thread separada com CAP_DSHOW para melhor compatibilidade no Windows
    video_getter = VideoGet(indice_cam).start()
    time.sleep(1.0) # Pequena pausa para estabilizar o stream

    if not video_getter.grabbed:
        print("Erro: Não foi possível acessar a câmera.")
        video_getter.stop()
        return

    print("Sistema Otimizado! Pressione 'q' para sair.")

    # ── Configurações de performance ──────────────────────────────────────────
    # Reduza SKIP_FRAMES para mais detecções (mais lento)
    # Aumente SKIP_FRAMES para mais FPS (menos detecções)
    SKIP_FRAMES   = 2   # processa 1 a cada N frames
    # Reduza INFER_SIZE para mais FPS (menos precisão)
    # Aumente INFER_SIZE para mais precisão (mais lento)
    INFER_SIZE    = 320 # tamanho da imagem enviada ao modelo (320 = rápido, 640 = preciso)
    # ─────────────────────────────────────────────────────────────────────────

    prev_time   = 0
    frame_count = 0
    annotated_frame = None

    while True:
        if video_getter.stopped:
            break

        frame = video_getter.read()
        if frame is None:
            continue

        frame_count += 1

        # Cálculo de FPS real do processamento
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
        prev_time = curr_time

        # Apenas processa a IA a cada SKIP_FRAMES frames
        if frame_count % SKIP_FRAMES == 0:
            # Reduz resolução antes de enviar para a IA (muito mais rápido)
            h, w = frame.shape[:2]
            scale = INFER_SIZE / max(h, w)
            if scale < 1.0:
                small = cv2.resize(frame, (int(w * scale), int(h * scale)),
                                   interpolation=cv2.INTER_LINEAR)
            else:
                small = frame

            # predict é mais leve que track; use verbose=False para não poluir o console
            results = model.predict(
                source=small,
                conf=0.25,
                iou=0.45,
                imgsz=INFER_SIZE,
                stream=True,
                verbose=False
            )

            for result in results:
                # Redimensiona o frame anotado de volta ao tamanho original
                ann = result.plot()
                if scale < 1.0:
                    ann = cv2.resize(ann, (w, h), interpolation=cv2.INTER_LINEAR)
                annotated_frame = ann

        # Exibe o último frame anotado disponível (sem travar esperando a IA)
        display = annotated_frame if annotated_frame is not None else frame

        cv2.putText(display, f"FPS: {int(fps)}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(display, f"Skip: 1/{SKIP_FRAMES}  Infer: {INFER_SIZE}px", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)

        cv2.imshow('Monitoramento de Residuos - IA', display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_getter.stop()
            break

    video_getter.stop()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

