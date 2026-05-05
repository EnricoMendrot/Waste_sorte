/*
 * ============================================================
 * Separador de Lixo Inteligente - Código do ESP32 (Wi-Fi)
 * ============================================================
 * 
 * Este código roda no ESP32 e recebe o tipo de lixo
 * detectado pelo sistema Python via HTTP (Wi-Fi).
 * 
 * O ESP32 roda um servidor web simples que aceita
 * requisições POST no endpoint /lixo.
 * 
 * Comunicação: HTTP POST em http://<IP_ESP32>:80/lixo
 * Formato: body com string plain/text
 * Valores possíveis: "plastico", "papel", "metal", "nenhum"
 * ============================================================
 */

#include <WiFi.h>
#include <WebServer.h>

// ── Configurações Wi-Fi ──
// ALTERE para sua rede Wi-Fi
const char* ssid     = "SUA_REDE_WIFI";
const char* password = "SUA_SENHA_WIFI";

// ── Servidor web na porta 80 ──
WebServer server(80);

// ── Definição dos pinos ──
#define LED_PLASTICO_PIN    25
#define LED_PAPEL_PIN       26
#define LED_METAL_PIN       27
#define LED_STATUS_PIN       2  // LED embutido

// ── Último tipo de lixo recebido ──
String lastTrashType = "nenhum";

void setup() {
    Serial.begin(115200);
    
    // Configura pinos
    pinMode(LED_PLASTICO_PIN, OUTPUT);
    pinMode(LED_PAPEL_PIN, OUTPUT);
    pinMode(LED_METAL_PIN, OUTPUT);
    pinMode(LED_STATUS_PIN, OUTPUT);
    
    resetLEDs();
    
    // Conecta ao Wi-Fi
    Serial.println("Conectando ao Wi-Fi...");
    WiFi.begin(ssid, password);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
        digitalWrite(LED_STATUS_PIN, !digitalRead(LED_STATUS_PIN));
    }
    
    Serial.println("\nWi-Fi conectado!");
    Serial.print("IP do ESP32: ");
    Serial.println(WiFi.localIP());
    
    // Configura rotas do servidor
    server.on("/", HTTP_GET, handleRoot);
    server.on("/lixo", HTTP_POST, handleTrash);
    server.onNotFound(handleNotFound);
    
    // Inicia servidor
    server.begin();
    Serial.println("Servidor HTTP iniciado na porta 80");
    
    // LED de status fixo = pronto
    digitalWrite(LED_STATUS_PIN, HIGH);
}

void loop() {
    // Processa requisições HTTP
    server.handleClient();
}

/**
 * Rota GET / — Página de status
 */
void handleRoot() {
    String html = "<!DOCTYPE html><html><body>";
    html += "<h1>Separador de Lixo - ESP32</h1>";
    html += "<p>Status: Online</p>";
    html += "<p>Ultimo tipo: " + lastTrashType + "</p>";
    html += "</body></html>";
    
    server.send(200, "text/html", html);
}

/**
 * Rota POST /lixo — Recebe o tipo de lixo
 */
void handleTrash() {
    // Lê o corpo da requisição
    String trashType = server.arg("plain");
    trashType.trim();
    
    Serial.print("HTTP POST /lixo -> ");
    Serial.println(trashType);
    
    // Processa
    lastTrashType = trashType;
    processTrashType(trashType);
    
    // Responde OK
    server.send(200, "text/plain", "OK: " + trashType);
}

/**
 * Rota 404 — Página não encontrada
 */
void handleNotFound() {
    server.send(404, "text/plain", "Endpoint nao encontrado");
}

/**
 * Processa o tipo de lixo e aciona o mecanismo.
 */
void processTrashType(String trashType) {
    resetLEDs();
    
    if (trashType == "plastico") {
        Serial.println(">> PLASTICO");
        digitalWrite(LED_PLASTICO_PIN, HIGH);
        
    } else if (trashType == "papel") {
        Serial.println(">> PAPEL");
        digitalWrite(LED_PAPEL_PIN, HIGH);
        
    } else if (trashType == "metal") {
        Serial.println(">> METAL");
        digitalWrite(LED_METAL_PIN, HIGH);
        
    } else {
        Serial.println(">> NENHUM / DESCONHECIDO");
        blinkLED(LED_STATUS_PIN, 3, 100);
    }
}

/**
 * Desliga todos os LEDs indicadores.
 */
void resetLEDs() {
    digitalWrite(LED_PLASTICO_PIN, LOW);
    digitalWrite(LED_PAPEL_PIN, LOW);
    digitalWrite(LED_METAL_PIN, LOW);
}

/**
 * Pisca um LED N vezes.
 */
void blinkLED(int pin, int times, int delayMs) {
    for (int i = 0; i < times; i++) {
        digitalWrite(pin, HIGH);
        delay(delayMs);
        digitalWrite(pin, LOW);
        delay(delayMs);
    }
}
