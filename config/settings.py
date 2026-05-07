"""
Configurações centralizadas do sistema Separador de Lixo.

Todas as constantes e parâmetros configuráveis ficam aqui,
facilitando ajustes sem modificar a lógica do código.
"""

import os

# ============================================================
# MODELO YOLO
# ============================================================

# Caminho para o arquivo de pesos do modelo treinado (.pt)
# Altere para o caminho real do seu modelo treinado
YOLO_MODEL_PATH = os.environ.get(
    "YOLO_MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "..", "models", "best.pt"),
)

# Limiar de confiança mínima para aceitar uma detecção
YOLO_CONFIDENCE_THRESHOLD = float(os.environ.get("YOLO_CONFIDENCE", "0.5"))

# Se True, usa detecções simuladas (mock) em vez do modelo real
# Útil para testes sem GPU ou sem modelo treinado
USE_MOCK_DETECTION = os.environ.get("USE_MOCK_DETECTION", "true").lower() == "true"

# ============================================================
# CLASSES DE LIXO
# ============================================================

# Mapeamento de índice → nome da classe
# Ajuste conforme o treinamento do seu modelo YOLO
CLASSES = {
    0: "plastico",
    1: "papel",
    2: "metal",
}

# Lista de tipos válidos (usada para validação)
VALID_TRASH_TYPES = ["plastico", "papel", "metal"]

# ============================================================
# CÂMERA
# ============================================================

# Índice da câmera (0 = webcam padrão) ou URL de stream do ESP32-CAM
# Exemplos: 0  |  "http://192.168.1.75:81/stream"
_cam_env = os.environ.get("CAMERA_INDEX", "0")
CAMERA_INDEX = int(_cam_env) if _cam_env.isdigit() else _cam_env

# Resolução desejada (largura x altura)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# ============================================================
# COMUNICAÇÃO COM ESP32
# ============================================================

# Tipo de comunicação: "serial" ou "wifi"
COMM_TYPE = os.environ.get("COMM_TYPE", "serial").lower()

# --- Configurações Serial (USB) ---
SERIAL_PORT = os.environ.get("SERIAL_PORT", "COM3")  # Porta serial do ESP32
SERIAL_BAUDRATE = int(os.environ.get("SERIAL_BAUDRATE", "115200"))
SERIAL_TIMEOUT = 2  # Timeout em segundos para leitura serial

# --- Configurações Wi-Fi (HTTP) ---
ESP32_IP = os.environ.get("ESP32_IP", "192.168.1.100")
ESP32_PORT = int(os.environ.get("ESP32_PORT", "80"))
ESP32_ENDPOINT = "/lixo"  # Endpoint HTTP no ESP32

# URL completa montada automaticamente
ESP32_URL = f"http://{ESP32_IP}:{ESP32_PORT}{ESP32_ENDPOINT}"

# Timeout para requisições HTTP (segundos)
HTTP_TIMEOUT = 5

# ============================================================
# SISTEMA
# ============================================================

# Intervalo entre cada ciclo de detecção (segundos)
DETECTION_INTERVAL = float(os.environ.get("DETECTION_INTERVAL", "1.0"))

# Se True, exibe a imagem capturada em uma janela OpenCV
SHOW_PREVIEW = os.environ.get("SHOW_PREVIEW", "false").lower() == "true"

# Nível de log: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
