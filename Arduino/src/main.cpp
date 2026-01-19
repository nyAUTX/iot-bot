#include <Arduino_GFX_Library.h>

// --- COLORS (565 Format) ---
#define C_NEUTRAL  0xCEFB // Blue / light gray
#define C_HAPPY    0xCFA1 // Green
#define C_ANGRY    0xD820 // Red
#define C_FLIRTY   0xE97C // Pink
#define C_BORED    0xD69A // Gray
#define C_DIM      0x03E0 // Dim Green for details

// --- PIN DEFINITIONS ---
#define SCK_PIN 18
#define MOSI_PIN 17
#define CS_PIN 10
#define DC_PIN 16
#define RST_PIN 21

Arduino_DataBus *bus = new Arduino_HWSPI(DC_PIN, CS_PIN, SCK_PIN, MOSI_PIN, -1);
Arduino_GFX *gfx = new Arduino_GC9A01(bus, RST_PIN, 0, true);
Arduino_Canvas *canvas = new Arduino_Canvas(240, 240, gfx);

float eyeX = 120, eyeY = 120, targetX = 120, targetY = 120;
float rot1 = 0, rot2 = 0;
int16_t blinkH = 0;
bool isBlinking = false;

// We'll use this to track the current active emotion
uint16_t currentMainColor = C_NEUTRAL;
uint16_t currentDimColor = C_DIM;

void setup() {
  gfx->begin();
  canvas->begin();
}

// ---------------------------------------------------------
// EMOTION METHODS
// ---------------------------------------------------------

void emotionNeutral() {
  currentMainColor = C_NEUTRAL;
  currentDimColor = 0x03E0;
}

void emotionHappy() {
  currentMainColor = C_HAPPY;
  currentDimColor = 0x780F; // Dim Pink
}

void emotionAngry() {
  currentMainColor = C_ANGRY;
  currentDimColor = 0x7800; // Dim Red
}

void emotionFlirty() {
  currentMainColor = C_FLIRTY;
  currentDimColor = 0x7BE0; // Dim Gold
}

void emotionBored() {
  currentMainColor = C_BORED;
  currentDimColor = 0x0210; // Dim Cyan
}

// ---------------------------------------------------------
// CORE DRAWING LOGIC
// ---------------------------------------------------------

void drawEye() {
  canvas->fillScreen(BLACK);

  rot1 += 0.02;
  rot2 -= 0.015;

  // 1. Outer Rings (Using current emotion colors)
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

  // 2. Movement
  if (random(100) > 96) {
    targetX = 120 + random(-30, 30);
    targetY = 120 + random(-20, 20);
  }
  eyeX += (targetX - eyeX) * 0.12;
  eyeY += (targetY - eyeY) * 0.12;

  // 3. Iris and Pupil
  canvas->fillCircle((int)eyeX, (int)eyeY, 50, currentMainColor);
  canvas->fillCircle((int)eyeX, (int)eyeY, 22, BLACK);

  // 4. Inner Detail
  canvas->drawCircle(eyeX, eyeY, 12, currentDimColor);
  float shardAngle = rot1 * 2.5;
  int sx = eyeX + cos(shardAngle) * 18, sy = eyeY + sin(shardAngle) * 18;
  canvas->fillCircle(sx, sy, 3, currentMainColor);

  // 5. Lens Reflection
  canvas->fillCircle(eyeX - 16, eyeY - 16, 5, WHITE);

  // 6. Blink
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
  // Example: Change emotion every 3 seconds
  unsigned long m = millis();
  if (m < 3000) emotionNeutral();
  else if (m < 6000) emotionHappy();
  else if (m < 9000) emotionAngry();
  else if (m < 12000) emotionFlirty();
  else emotionBored();

  drawEye();
  delay(10);
}