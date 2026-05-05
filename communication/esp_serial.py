"""
Comunicação com ESP32 via porta Serial (USB).

Usa a biblioteca pyserial para enviar o tipo de lixo
detectado ao ESP32 conectado por cabo USB.
"""

import logging
import time

from config import settings

logger = logging.getLogger(__name__)

# Tenta importar pyserial
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    logger.warning("pyserial nao instalado. Execute: pip install pyserial")


class ESPSerial:
    """
    Classe para comunicação serial com o ESP32.
    
    Envia strings simples pela porta serial USB.
    O ESP32 deve estar programado para ler essas strings
    e acionar o mecanismo de separação correspondente.
    """

    def __init__(
        self,
        port: str = None,
        baudrate: int = None,
        timeout: float = None,
    ):
        """
        Inicializa a comunicação serial.

        Args:
            port: Porta serial (ex: 'COM3' no Windows, '/dev/ttyUSB0' no Linux)
            baudrate: Taxa de transmissão (deve corresponder à do ESP32)
            timeout: Timeout de leitura em segundos
        """
        self.port = port or settings.SERIAL_PORT
        self.baudrate = baudrate or settings.SERIAL_BAUDRATE
        self.timeout = timeout or settings.SERIAL_TIMEOUT
        self.connection = None

    def connect(self) -> bool:
        """
        Abre a conexão serial com o ESP32.

        Returns:
            True se conectou com sucesso, False caso contrário.
        """
        if not SERIAL_AVAILABLE:
            logger.error(
                "pyserial nao esta instalado. "
                "Instale com: pip install pyserial"
            )
            return False

        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )

            # Aguarda o ESP32 resetar apos conexao serial
            time.sleep(2)

            logger.info(
                f"Conectado ao ESP32 via Serial: "
                f"{self.port} @ {self.baudrate} baud"
            )
            return True

        except serial.SerialException as e:
            logger.error(f"Erro ao conectar na porta {self.port}: {e}")
            return False

        except Exception as e:
            logger.error(f"Erro inesperado na conexão serial: {e}")
            return False

    def send(self, trash_type: str) -> bool:
        """
        Envia o tipo de lixo para o ESP32 via Serial.

        A string e enviada codificada em UTF-8, seguida de um
        caractere de nova linha (\\n) como delimitador.

        Args:
            trash_type: Tipo de lixo ('plastico', 'papel', 'metal' ou 'nenhum')

        Returns:
            True se enviou com sucesso, False caso contrário.
        """
        if self.connection is None or not self.connection.is_open:
            logger.error("Conexão serial não está aberta")
            return False

        try:
            # Envia a string com terminador de linha
            message = f"{trash_type}\n"
            self.connection.write(message.encode("utf-8"))
            self.connection.flush()

            logger.info(f"[SERIAL] Enviado → '{trash_type}'")

            # Tenta ler resposta do ESP32 (opcional)
            if self.connection.in_waiting > 0:
                response = self.connection.readline().decode("utf-8").strip()
                logger.debug(f"[SERIAL] Resposta do ESP32: '{response}'")

            return True

        except serial.SerialException as e:
            logger.error(f"Erro ao enviar dados via serial: {e}")
            return False

        except Exception as e:
            logger.error(f"Erro inesperado ao enviar serial: {e}")
            return False

    def disconnect(self):
        """Fecha a conexão serial."""
        if self.connection is not None and self.connection.is_open:
            self.connection.close()
            logger.info("Conexão serial encerrada")

    def is_connected(self) -> bool:
        """Verifica se a conexão serial está ativa."""
        return (
            self.connection is not None
            and self.connection.is_open
        )

    def __enter__(self):
        """Suporte a context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Libera recursos ao sair do context manager."""
        self.disconnect()
