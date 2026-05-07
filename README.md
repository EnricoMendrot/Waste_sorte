# 🗑️ Separador de Lixo Inteligente

Sistema de visão computacional com YOLO para detecção automática de tipos de lixo (plástico, papel, metal) e comunicação com ESP32 para acionamento do mecanismo de separação.

> 📷 **Suporta ESP32-CAM** como fonte de vídeo via stream Wi-Fi, além de webcams USB convencionais.

## 📁 Estrutura do Projeto

```
Separador_lixo/
├── main.py                     # Ponto de entrada principal
├── iniciar_espcam.bat          # Atalho para rodar com ESP32-CAM (Windows)
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Configurações centralizadas
│
├── detection/
│   ├── __init__.py
│   ├── yolo_model.py           # Carregamento e inferência YOLO
│   └── predictor.py            # Interpretação dos resultados
│
├── communication/
│   ├── __init__.py
│   ├── esp_serial.py           # Comunicação Serial (USB)
│   └── esp_wifi.py             # Comunicação Wi-Fi (HTTP)
│
├── utils/
│   ├── __init__.py
│   ├── image_utils.py          # Captura de imagem (câmera)
│   └── logger.py               # Configuração de logs
│
├── esp32/
│   ├── separador_lixo_serial.ino   # Código ESP32 (Serial)
│   └── separador_lixo_wifi.ino     # Código ESP32 (Wi-Fi)
│
└── models/
    └── (coloque aqui o arquivo best.pt)
```

## 🚀 Como Rodar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Executar em modo simulação (sem ESP32 e sem modelo real)

```bash
python main.py --no-esp
```

### 3. Executar com ESP32 via Serial (USB)

```bash
# Verifique a porta COM no Gerenciador de Dispositivos do Windows
python main.py --comm serial --port COM3
```

### 4. Executar com ESP32 via Wi-Fi

```bash
python main.py --comm wifi --ip 192.168.1.100
```

### 5. Executar com câmera ESP32-CAM (stream Wi-Fi)

```bash
# Usando o script atalho (recomendado no Windows)
.\iniciar_espcam.bat 192.168.1.75

# Ou diretamente
python main.py --camera http://192.168.1.75:81/stream --real --preview
```

### 6. Executar com modelo YOLO real

```bash
# Coloque o arquivo best.pt na pasta models/
python main.py --real --comm serial --port COM3
```

### 7. Todos os argumentos disponíveis

```bash
python main.py --help
```

| Argumento     | Descrição                          | Padrão        |
| ------------- | ---------------------------------- | ------------- |
| `--real`      | Usar modelo YOLO real              | Falso (mock)  |
| `--comm`      | Tipo de comunicação (serial/wifi)  | serial        |
| `--port`      | Porta serial do ESP32              | COM3          |
| `--baudrate`  | Baudrate serial                    | 115200        |
| `--ip`        | IP do ESP32 (modo Wi-Fi)           | 192.168.1.100 |
| `--preview`   | Exibir preview da câmera           | Falso         |
| `--interval`  | Segundos entre cada detecção       | 1.0           |
| `--camera`    | Índice da câmera (int) **ou URL do stream ESP32-CAM** | 0 |
| `--log-level` | Nível de log                       | INFO          |
| `--no-esp`    | Rodar sem ESP32 (só detecção)      | Falso         |

## ⚡ Configuração do ESP32

### Opção 1: Serial (USB)

1. Abra o Arduino IDE
2. Abra o arquivo `esp32/separador_lixo_serial.ino`
3. Selecione a placa **ESP32 Dev Module**
4. Selecione a porta COM correta
5. Faça upload do código
6. A comunicação é via USB — basta manter o cabo conectado

### Opção 2: Wi-Fi — ESP32 separador (HTTP)

1. Abra o arquivo `esp32/separador_lixo_wifi.ino`
2. **Altere** `ssid` e `password` para sua rede Wi-Fi
3. Faça upload do código
4. Abra o Monitor Serial para ver o IP atribuído ao ESP32
5. Use esse IP no argumento `--ip`

### Opção 3: ESP32-CAM (câmera via Wi-Fi)

1. Abra o Arduino IDE
2. Instale o suporte ESP32 pelo Board Manager
3. Acesse `File → Examples → ESP32 → Camera → CameraWebServer`
4. Selecione o modelo da placa (geralmente `CAMERA_MODEL_AI_THINKER`)
5. Configure `ssid` e `password` para sua rede Wi-Fi
6. Faça upload e abra o **Monitor Serial** (115200 baud)
7. Anote o IP exibido e use com o script ou argumento `--camera`:

```bash
.\iniciar_espcam.bat <IP_EXIBIDO>
```

## 🔄 Fluxo do Sistema

```
[Webcam USB]  ──┐
                ├──► Captura Frame ──► YOLO (detecção) ──► Interpretação ──► ESP32 ──► Separação
[ESP32-CAM] ───┘
```

1. A câmera captura um frame
2. O modelo YOLO detecta objetos na imagem
3. O sistema identifica o tipo predominante (plástico/papel/metal)
4. O resultado é enviado ao ESP32 como string simples
5. O ESP32 aciona o mecanismo de separação correspondente

## 🧪 Variáveis de Ambiente

Você pode configurar o sistema via variáveis de ambiente em vez de argumentos:

```bash
set YOLO_MODEL_PATH=C:\caminho\para\best.pt
set USE_MOCK_DETECTION=false
set COMM_TYPE=serial
set SERIAL_PORT=COM5
set ESP32_IP=192.168.1.50
set CAMERA_INDEX=1
# Ou para ESP32-CAM:
set CAMERA_INDEX=http://192.168.1.75:81/stream
```

## 📝 Notas

- O modo **mock** gera detecções aleatórias e não precisa de câmera nem modelo
- O sistema funciona em **loop contínuo** — pressione `Ctrl+C` para parar
- Os **logs** mostram todo o fluxo no terminal em tempo real
- A troca entre Serial e Wi-Fi é feita apenas mudando o argumento `--comm`
- O **ESP32-CAM** envia vídeo via Wi-Fi e pode ser combinado com outro ESP32 para o mecanismo de separação
- O script `iniciar_espcam.bat <IP>` é um atalho para facilitar o uso no Windows
