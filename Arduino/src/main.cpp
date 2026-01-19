#include <Arduino_GFX_Library.h>
#include <Arduino.h>

// --- PIN DEFINITIONS ---
#define SCK_PIN 18
#define MOSI_PIN 17
#define CS_PIN 10
#define DC_PIN 16
#define RST_PIN 21
#define UART_RX 44
#define UART_TX 43

// --- COLORS (565 Format) ---
#define C_NEUTRAL  0xCEFB
#define C_HAPPY    0xCFA1
#define C_ANGRY    0xD820
#define C_FLIRTY   0xE97C
#define C_BORED    0xD69A
#define C_DIM      0x03E0

// Global Objects
Arduino_DataBus *bus = new Arduino_HWSPI(DC_PIN, CS_PIN, SCK_PIN, MOSI_PIN, -1);
Arduino_GFX *gfx = new Arduino_GC9A01(bus, RST_PIN, 0, true);
Arduino_Canvas *canvas = new Arduino_Canvas(240, 240, gfx);
HardwareSerial uart(1);

// Eye Animation Variables
float eyeX = 120, eyeY = 120, targetX = 120, targetY = 120;
float rot1 = 0, rot2 = 0;
int16_t blinkH = 0;
bool isBlinking = false;
uint16_t currentMainColor = C_NEUTRAL;
uint16_t currentDimColor = C_DIM;

// Emotion Functions
void emotionNeutral() { currentMainColor = C_NEUTRAL; currentDimColor = 0x03E0; }
void emotionHappy()   { currentMainColor = C_HAPPY;   currentDimColor = 0x780F; }
void emotionAngry()   { currentMainColor = C_ANGRY;   currentDimColor = 0x7800; }
void emotionFlirty()  { currentMainColor = C_FLIRTY;  currentDimColor = 0x7BE0; }
void emotionBored()   { currentMainColor = C_BORED;   currentDimColor = 0x0210; }

void setup() {
  // Initialize Serial
  Serial.begin(115200);
  uart.begin(115200, SERIAL_8N1, UART_RX, UART_TX);

  // Initialize Display
  gfx->begin();
  canvas->begin();

  emotionNeutral(); // Start with neutral
}

void drawEye() {
  canvas->fillScreen(BLACK);
  rot1 += 0.02;
  rot2 -= 0.015;

  // Outer Rings
  for (int i = 0; i < 6; i++) {
    float angle = rot1 + (i * PI / 3);
    int x1 = 120 + cos(angle) * 112, y1 = 120 + sin(angle) * 112;
    int x2 = 120 + cos(angle + 0.4) * 116, y2 = 120 + sin(angle + 0.4) * 116;
    canvas->drawLine(x1, y1, x2, y2, currentMainColor);
  }

  for (int i = 0; i < 10; i++) {
    float angle = rot2 + (i * PI / 5);
    int xNode = 120 + cos(angle) * 102, yNode = 120 + sin(angle) * 102;
    canvas->fillCircle(xNode, yNode, 2, currentDimColor);
  }

  // Eye Movement
  if (random(100) > 96) {
    targetX = 120 + random(-30, 30);
    targetY = 120 + random(-20, 20);
  }
  eyeX += (targetX - eyeX) * 0.12;
  eyeY += (targetY - eyeY) * 0.12;

  // Iris, Pupil, Shards
  canvas->fillCircle((int)eyeX, (int)eyeY, 50, currentMainColor);
  canvas->fillCircle((int)eyeX, (int)eyeY, 22, BLACK);
  canvas->drawCircle(eyeX, eyeY, 12, currentDimColor);

  float shardAngle = rot1 * 2.5;
  int sx = eyeX + cos(shardAngle) * 18, sy = eyeY + sin(shardAngle) * 18;
  canvas->fillCircle(sx, sy, 3, currentMainColor);
  canvas->fillCircle(eyeX - 16, eyeY - 16, 5, WHITE);

  // Blink Logic
  if (!isBlinking && random(100) > 98) isBlinking = true;
  if (isBlinking) {
    blinkH += 25;
    if (blinkH >= 120) isBlinking = false;
  } else if (blinkH > 0) {
    blinkH -= 15;
  }

  if (blinkH > 0) {
    canvas->fillRect(0, 0, 240, blinkH, BLACK);
    canvas->fillRect(0, 240 - blinkH, 240, 240, BLACK);
  }

  canvas->flush();
}

void loop() {
  // 1. Check for commands from Raspberry Pi
  if (uart.available()) {
    String msg = uart.readStringUntil('\n');
    msg.trim(); // Remove whitespace or \r
    Serial.println("Command Received: " + msg);

    if (msg == "happy")        emotionHappy();
    else if (msg == "angry")   emotionAngry();
    else if (msg == "flirty")  emotionFlirty();
    else if (msg == "bored")   emotionBored();
    else if (msg == "neutral") emotionNeutral();
  }

  // 2. Render the eye
  drawEye();

  delay(10);
}