/*
 * ============================================================
 * Separador de Lixo Inteligente - Código do ESP32
 * ============================================================
 * 
 * Este código roda no ESP32 e recebe o tipo de lixo
 * detectado pelo sistema Python via Serial (USB).
 * 
 * O ESP32 lê a string recebida e pode acionar servos,
 * motores ou LEDs para separar o lixo.
 * 
 * Comunicação: Serial @ 115200 baud
 * Formato: string terminada com '\n'
 * Valores possíveis: "plastico", "papel", "metal", "nenhum"
 * ============================================================
 */

// ── Definição dos pinos ──
// Ajuste conforme sua montagem física
#define SERVO_PLASTICO_PIN  13
#define SERVO_PAPEL_PIN     12
#define SERVO_METAL_PIN     14

#define LED_PLASTICO_PIN    25
#define LED_PAPEL_PIN       26
#define LED_METAL_PIN       27
#define LED_STATUS_PIN       2  // LED embutido do ESP32

// ── Variáveis globais ──
String receivedData = "";

void setup() {
    // Inicializa comunicação serial
    Serial.begin(115200);
    
    // Configura pinos dos LEDs como saída
    pinMode(LED_PLASTICO_PIN, OUTPUT);
    pinMode(LED_PAPEL_PIN, OUTPUT);
    pinMode(LED_METAL_PIN, OUTPUT);
    pinMode(LED_STATUS_PIN, OUTPUT);
    
    // Desliga todos os LEDs
    resetLEDs();
    
    // Pisca LED de status para indicar que está pronto
    for (int i = 0; i < 3; i++) {
        digitalWrite(LED_STATUS_PIN, HIGH);
        delay(200);
        digitalWrite(LED_STATUS_PIN, LOW);
        delay(200);
    }
    
    Serial.println("ESP32 Separador de Lixo - Pronto!");
    Serial.println("Aguardando comandos...");
}

void loop() {
    // Verifica se há dados disponíveis na serial
    if (Serial.available() > 0) {
        // Lê a string até o caractere de nova linha
        receivedData = Serial.readStringUntil('\n');
        receivedData.trim();  // Remove espaços e \r
        
        // Processa o tipo de lixo recebido
        processTrashType(receivedData);
    }
}

/**
 * Processa o tipo de lixo recebido e aciona o mecanismo
 * de separação correspondente.
 * 
 * @param trashType String com o tipo: "plastico", "papel", "metal" ou "nenhum"
 */
void processTrashType(String trashType) {
    Serial.print("Recebido: ");
    Serial.println(trashType);
    
    // Reseta todos os LEDs antes de acionar o novo
    resetLEDs();
    
    if (trashType == "plastico") {
        Serial.println(">> Acionando separador: PLÁSTICO");
        digitalWrite(LED_PLASTICO_PIN, HIGH);
        activateSeparator(SERVO_PLASTICO_PIN);
        
    } else if (trashType == "papel") {
        Serial.println(">> Acionando separador: PAPEL");
        digitalWrite(LED_PAPEL_PIN, HIGH);
        activateSeparator(SERVO_PAPEL_PIN);
        
    } else if (trashType == "metal") {
        Serial.println(">> Acionando separador: METAL");
        digitalWrite(LED_METAL_PIN, HIGH);
        activateSeparator(SERVO_METAL_PIN);
        
    } else if (trashType == "nenhum") {
        Serial.println(">> Nenhum lixo detectado");
        // Pisca LED de status brevemente
        digitalWrite(LED_STATUS_PIN, HIGH);
        delay(100);
        digitalWrite(LED_STATUS_PIN, LOW);
        
    } else {
        Serial.print(">> Tipo desconhecido: ");
        Serial.println(trashType);
    }
    
    // Envia confirmação de volta ao Python
    Serial.println("OK");
}

/**
 * Aciona o mecanismo de separação (servo motor).
 * 
 * TODO: Implementar controle real do servo motor.
 * Por enquanto, simula com um delay.
 * 
 * @param servoPin Pino do servo motor a ser acionado
 */
void activateSeparator(int servoPin) {
    // Aqui você implementaria o controle do servo motor
    // Exemplo com a biblioteca ESP32Servo:
    //
    // #include <ESP32Servo.h>
    // Servo myServo;
    // myServo.attach(servoPin);
    // myServo.write(90);   // Gira para posição de separação
    // delay(2000);          // Mantém por 2 segundos
    // myServo.write(0);    // Retorna à posição original
    
    // Simulação: LED de status pisca durante "ação"
    for (int i = 0; i < 3; i++) {
        digitalWrite(LED_STATUS_PIN, HIGH);
        delay(300);
        digitalWrite(LED_STATUS_PIN, LOW);
        delay(300);
    }
    
    Serial.println("Separação concluída");
}

/**
 * Desliga todos os LEDs indicadores.
 */
void resetLEDs() {
    digitalWrite(LED_PLASTICO_PIN, LOW);
    digitalWrite(LED_PAPEL_PIN, LOW);
    digitalWrite(LED_METAL_PIN, LOW);
    digitalWrite(LED_STATUS_PIN, LOW);
}
