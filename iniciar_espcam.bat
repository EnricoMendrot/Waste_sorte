@echo off
REM ============================================================
REM  Separador de Lixo Inteligente - Iniciar com ESP32-CAM
REM
REM  USO:
REM    iniciar_espcam.bat <IP_DA_CAM>
REM
REM  EXEMPLO:
REM    iniciar_espcam.bat 192.168.1.75
REM ============================================================

IF "%~1"=="" (
    echo.
    echo  [ERRO] Voce precisa informar o IP do ESP32-CAM.
    echo.
    echo  Uso:    iniciar_espcam.bat ^<IP^>
    echo  Exemplo: iniciar_espcam.bat 192.168.1.75
    echo.
    pause
    exit /b 1
)

SET ESP_CAM_IP=%~1
SET ESP_CAM_URL=http://%ESP_CAM_IP%:81/stream

echo.
echo  +---------------------------------------------------------+
echo  ^|  Separador de Lixo - ESP32-CAM                        ^|
echo  ^|  Stream: %ESP_CAM_URL%
echo  +---------------------------------------------------------+
echo.

python main.py --camera %ESP_CAM_URL% --real --preview
