"""
Utilitários para captura e manipulação de imagens.

Responsável por interfacear com a câmera usando OpenCV
e fornecer imagens prontas para inferência.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

# Tentamos importar OpenCV; se não estiver instalado, usaremos imagens simuladas
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV não encontrado. Usando imagens simuladas.")


class CameraCapture:
    """
    Classe para captura de imagens via webcam ou stream de rede com OpenCV.

    Suporta:
    - Webcam local: camera_index=0 (ou outro inteiro)
    - ESP32-CAM via Wi-Fi: camera_index="http://192.168.1.75:81/stream"

    Se o OpenCV não estiver disponível, gera imagens simuladas (numpy array).
    """

    def __init__(self, camera_index: int | str = 0, width: int = 640, height: int = 480):
        """
        Inicializa a câmera.

        Args:
            camera_index: Índice da câmera (int, ex: 0) ou URL do stream
                          do ESP32-CAM (str, ex: "http://192.168.1.75:81/stream")
            width: Largura da imagem capturada
            height: Altura da imagem capturada
        """
        # Converte para int se for string numérica (ex: argparse sem type=int)
        if isinstance(camera_index, str) and camera_index.isdigit():
            camera_index = int(camera_index)
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None

    def open(self) -> bool:
        """
        Abre a conexão com a câmera.

        Returns:
            True se a câmera foi aberta com sucesso, False caso contrário.
        """
        if not OPENCV_AVAILABLE:
            logger.info("OpenCV indisponível. Modo de simulação ativado.")
            return True

        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                logger.error(f"Não foi possível abrir a câmera {self.camera_index}")
                return False

            # Configura resolução
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

            logger.info(
                f"Câmera {self.camera_index} aberta com sucesso "
                f"({self.width}x{self.height})"
            )
            return True

        except Exception as e:
            logger.error(f"Erro ao abrir câmera: {e}")
            return False

    def capture_frame(self) -> np.ndarray | None:
        """
        Captura um frame da câmera.

        Returns:
            numpy array com a imagem (BGR) ou None em caso de erro.
        """
        if not OPENCV_AVAILABLE or self.cap is None:
            # Gera uma imagem simulada (640x480, 3 canais, valores aleatórios)
            logger.debug("Gerando frame simulado")
            return np.random.randint(0, 255, (self.height, self.width, 3), dtype=np.uint8)

        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                logger.warning("Falha ao capturar frame da câmera")
                return None

            logger.debug(f"Frame capturado: {frame.shape}")
            return frame

        except Exception as e:
            logger.error(f"Erro ao capturar frame: {e}")
            return None

    def show_frame(self, frame: np.ndarray, window_name: str = "Separador de Lixo"):
        """
        Exibe um frame em uma janela OpenCV.

        Args:
            frame: Imagem a ser exibida
            window_name: Nome da janela
        """
        if OPENCV_AVAILABLE and frame is not None:
            cv2.imshow(window_name, frame)
            cv2.waitKey(1)  # Necessário para atualizar a janela

    def close(self):
        """Libera os recursos da câmera."""
        if self.cap is not None:
            self.cap.release()
            logger.info("Câmera liberada")

        if OPENCV_AVAILABLE:
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass

    def __enter__(self):
        """Suporte a context manager (with statement)."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Libera recursos ao sair do context manager."""
        self.close()
