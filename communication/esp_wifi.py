"""
Comunicação com ESP32 via Wi-Fi (HTTP).

Envia o tipo de lixo detectado ao ESP32 através de
requisições HTTP POST. O ESP32 deve rodar um servidor
web simples que receba as requisições.
"""

import logging

from config import settings

logger = logging.getLogger(__name__)

# Tenta importar requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests nao instalado. Execute: pip install requests")


class ESPWifi:
    """
    Classe para comunicação Wi-Fi (HTTP) com o ESP32.
    
    Envia o tipo de lixo via requisição HTTP POST para o
    servidor web rodando no ESP32.
    
    O ESP32 deve estar na mesma rede Wi-Fi e rodando
    um servidor HTTP que aceite POST no endpoint configurado.
    """

    def __init__(
        self,
        url: str = None,
        timeout: int = None,
    ):
        """
        Inicializa a comunicação Wi-Fi.

        Args:
            url: URL completa do ESP32 (ex: 'http://192.168.1.100:80/lixo')
            timeout: Timeout para requisições HTTP em segundos
        """
        self.url = url or settings.ESP32_URL
        self.timeout = timeout or settings.HTTP_TIMEOUT
        self._connected = False

    def connect(self) -> bool:
        """
        Testa a conexão com o ESP32 via HTTP.

        Faz um GET simples para verificar se o ESP32 está acessível.

        Returns:
            True se o ESP32 respondeu, False caso contrário.
        """
        if not REQUESTS_AVAILABLE:
            logger.error(
                "Biblioteca 'requests' não instalada. "
                "Instale com: pip install requests"
            )
            return False

        try:
            # Tenta um GET simples para verificar conectividade
            base_url = self.url.rsplit("/", 1)[0]
            response = requests.get(base_url, timeout=self.timeout)

            if response.status_code == 200:
                logger.info(f"ESP32 acessivel em: {self.url}")
                self._connected = True
                return True
            else:
                logger.warning(
                    f"ESP32 respondeu com status {response.status_code}"
                )
                # Mesmo com status diferente, consideramos conectado
                self._connected = True
                return True

        except requests.ConnectionError:
            logger.error(
                f"Nao foi possivel conectar ao ESP32 em: {self.url}. "
                f"Verifique se o ESP32 esta ligado e na mesma rede."
            )
            return False

        except requests.Timeout:
            logger.error(
                f"Timeout ao conectar ao ESP32. "
                f"Verifique o IP ({settings.ESP32_IP}) e a rede."
            )
            return False

        except Exception as e:
            logger.error(f"Erro inesperado ao conectar via Wi-Fi: {e}")
            return False

    def send(self, trash_type: str) -> bool:
        """
        Envia o tipo de lixo para o ESP32 via HTTP POST.

        O corpo da requisição contém apenas a string do tipo de lixo.
        Headers incluem Content-Type: text/plain.

        Args:
            trash_type: Tipo de lixo ('plastico', 'papel', 'metal' ou 'nenhum')

        Returns:
            True se enviou com sucesso, False caso contrário.
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests nao esta instalado")
            return False

        try:
            # Envia POST com o tipo de lixo no corpo
            response = requests.post(
                self.url,
                data=trash_type,
                headers={"Content-Type": "text/plain"},
                timeout=self.timeout,
            )

            if response.status_code == 200:
                logger.info(f"[WIFI] Enviado → '{trash_type}' (HTTP 200 OK)")
                return True
            else:
                logger.warning(
                    f"[WIFI] Enviado '{trash_type}', "
                    f"mas ESP32 respondeu com status {response.status_code}"
                )
                return True  # Enviou, mesmo com status diferente

        except requests.ConnectionError:
            logger.error(
                f"[WIFI] Falha ao enviar '{trash_type}': "
                f"ESP32 nao acessivel"
            )
            return False

        except requests.Timeout:
            logger.error(
                f"[WIFI] Timeout ao enviar '{trash_type}'"
            )
            return False

        except Exception as e:
            logger.error(f"[WIFI] Erro inesperado: {e}")
            return False

    def disconnect(self):
        """Encerra a conexão (no HTTP não há estado persistente)."""
        self._connected = False
        logger.info("Sessão Wi-Fi encerrada")

    def is_connected(self) -> bool:
        """Verifica se a conexão Wi-Fi foi estabelecida."""
        return self._connected

    def __enter__(self):
        """Suporte a context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Libera recursos ao sair do context manager."""
        self.disconnect()
