"""
Separador de Lixo Inteligente - Ponto de entrada principal.

Este sistema captura imagens de uma câmera, detecta o tipo de lixo
usando YOLO e envia o resultado para um ESP32 que controla o
mecanismo de separação.

Uso:
    python main.py                  # Modo mock (simulação)
    python main.py --real           # Usa modelo YOLO real
    python main.py --comm wifi      # Comunicação via Wi-Fi
    python main.py --comm serial    # Comunicação via Serial (padrão)
    python main.py --preview        # Exibe preview da câmera
"""

import argparse
import logging
import signal
import sys
import time

from config import settings
from detection.yolo_model import create_model
from detection.predictor import get_predominant_trash, format_result
from communication.esp_serial import ESPSerial
from communication.esp_wifi import ESPWifi
from utils.image_utils import CameraCapture
from utils.logger import setup_logger

# Flag global para controlar o loop principal
running = True


def signal_handler(sig, frame):
    """Trata Ctrl+C para encerramento gracioso."""
    global running
    print("\n")
    logging.getLogger(__name__).info("Encerrando sistema (Ctrl+C)...")
    running = False


def parse_arguments() -> argparse.Namespace:
    """
    Processa os argumentos da linha de comando.

    Returns:
        Namespace com os argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description="Separador de Lixo Inteligente - YOLO + ESP32",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py                        Modo simulação (mock)
  python main.py --real                 Usa modelo YOLO real
  python main.py --comm wifi --ip 192.168.1.50   Envia via Wi-Fi
  python main.py --comm serial --port COM5        Envia via Serial
  python main.py --preview --interval 2.0         Com preview, 2s entre ciclos
        """,
    )

    parser.add_argument(
        "--real",
        action="store_true",
        help="Usar modelo YOLO real em vez do mock (requer modelo .pt)",
    )
    parser.add_argument(
        "--comm",
        choices=["serial", "wifi"],
        default=settings.COMM_TYPE,
        help=f"Tipo de comunicação com ESP32 (padrão: {settings.COMM_TYPE})",
    )
    parser.add_argument(
        "--port",
        default=settings.SERIAL_PORT,
        help=f"Porta serial do ESP32 (padrão: {settings.SERIAL_PORT})",
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=settings.SERIAL_BAUDRATE,
        help=f"Baudrate serial (padrão: {settings.SERIAL_BAUDRATE})",
    )
    parser.add_argument(
        "--ip",
        default=settings.ESP32_IP,
        help=f"IP do ESP32 para Wi-Fi (padrão: {settings.ESP32_IP})",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Exibir preview da câmera em janela",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=settings.DETECTION_INTERVAL,
        help=f"Intervalo entre detecções em segundos (padrão: {settings.DETECTION_INTERVAL})",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=settings.CAMERA_INDEX,
        help=f"Índice da câmera (padrão: {settings.CAMERA_INDEX})",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=settings.LOG_LEVEL,
        help=f"Nível de log (padrão: {settings.LOG_LEVEL})",
    )
    parser.add_argument(
        "--no-esp",
        action="store_true",
        help="Rodar sem comunicação com ESP32 (apenas detecção)",
    )

    return parser.parse_args()


def create_communicator(args: argparse.Namespace):
    """
    Factory function para criar o comunicador correto.

    Args:
        args: Argumentos da linha de comando

    Returns:
        Instância de ESPSerial ou ESPWifi
    """
    if args.comm == "serial":
        return ESPSerial(port=args.port, baudrate=args.baudrate)
    else:
        # Atualiza URL com o IP fornecido
        url = f"http://{args.ip}:{settings.ESP32_PORT}{settings.ESP32_ENDPOINT}"
        return ESPWifi(url=url)


def print_banner():
    """Exibe o banner do sistema no terminal."""
    banner = """
    +-------------------------------------------------------+
    |                                                       |
    |    SEPARADOR DE LIXO INTELIGENTE                      |
    |    -------------------------------------              |
    |    YOLO + ESP32                                       |
    |                                                       |
    |    Tipos detectados: plastico | papel | metal         |
    |                                                       |
    +-------------------------------------------------------+
    """
    print(banner)


def main():
    """
    Loop principal do sistema.

    Fluxo:
    1. Inicializa câmera, modelo e comunicação
    2. Em loop contínuo:
       a. Captura frame da câmera
       b. Executa detecção YOLO
       c. Interpreta resultado (tipo predominante)
       d. Envia resultado ao ESP32
    3. Encerra graciosamente com Ctrl+C
    """
    global running

    # Processa argumentos
    args = parse_arguments()

    # Configura logging
    logger = setup_logger(args.log_level)

    # Banner
    print_banner()

    # Registra handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # ── 1. Inicializa o modelo YOLO ──────────────────────────
    use_mock = not args.real
    model = create_model(use_mock=use_mock)

    if not model.load():
        logger.error("Falha ao carregar o modelo. Encerrando.")
        sys.exit(1)

    # ── 2. Inicializa a câmera ───────────────────────────────
    camera = CameraCapture(
        camera_index=args.camera,
        width=settings.CAMERA_WIDTH,
        height=settings.CAMERA_HEIGHT,
    )

    if not camera.open():
        logger.error("Falha ao abrir a câmera. Encerrando.")
        sys.exit(1)

    # ── 3. Inicializa a comunicação com ESP32 ────────────────
    communicator = None
    if not args.no_esp:
        communicator = create_communicator(args)
        if not communicator.connect():
            logger.warning(
                "Não foi possível conectar ao ESP32. "
                "Continuando apenas com detecção..."
            )
            communicator = None

    # ── 4. Loop principal ────────────────────────────────────
    logger.info("=" * 50)
    logger.info("Sistema iniciado! Pressione Ctrl+C para encerrar.")
    logger.info(f"Modo: {'REAL' if args.real else 'MOCK (simulação)'}")
    logger.info(f"Comunicação: {args.comm.upper()}")
    logger.info(f"Intervalo: {args.interval}s")
    logger.info("=" * 50)

    cycle_count = 0

    try:
        while running:
            cycle_count += 1
            logger.info(f"-- Ciclo #{cycle_count} --")

            # 4a. Captura frame
            frame = camera.capture_frame()
            if frame is None:
                logger.warning("Frame vazio. Tentando novamente...")
                time.sleep(args.interval)
                continue

            # 4b. Exibe preview (se habilitado)
            if args.preview:
                camera.show_frame(frame)

            # 4c. Executa detecção YOLO
            detections = model.predict(frame)
            logger.info(f"Detecções encontradas: {len(detections)}")

            for i, det in enumerate(detections):
                logger.debug(
                    f"  [{i+1}] {det['class_name']} "
                    f"(confiança: {det['confidence']:.2f})"
                )

            # 4d. Interpreta resultado
            predominant = get_predominant_trash(detections)
            result = format_result(predominant)

            logger.info(f">>> Resultado: {result.upper()}")

            # 4e. Envia ao ESP32
            if communicator is not None:
                success = communicator.send(result)
                if not success:
                    logger.warning("Falha ao enviar para ESP32")
            else:
                logger.debug("ESP32 nao conectado. Resultado nao enviado.")

            # 4f. Aguarda intervalo
            logger.info(f"Aguardando {args.interval}s...")
            time.sleep(args.interval)

    except KeyboardInterrupt:
        pass

    finally:
        # ── 5. Limpeza ──────────────────────────────────────
        logger.info("Encerrando sistema...")

        camera.close()

        if communicator is not None:
            communicator.disconnect()

        logger.info(f"Total de ciclos executados: {cycle_count}")
        logger.info("Sistema encerrado com sucesso. Ate logo!")


if __name__ == "__main__":
    main()
