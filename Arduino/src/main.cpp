#include <Arduino_GFX_Library.h>

// Pins for LilyGO T-Display S3 (Right Header)
#define SCK_PIN 18
#define MOSI_PIN 17
#define MISO_PIN -1
#define CS_PIN 43
#define DC_PIN 16
#define RST_PIN 21

// Use the standard HWSPI for maximum compatibility
Arduino_DataBus *bus = new Arduino_HWSPI(DC_PIN, CS_PIN, SCK_PIN, MOSI_PIN, MISO_PIN);
Arduino_GFX *gfx = new Arduino_GC9A01(bus, RST_PIN, 0, true);

// Full screen 240x240 canvas
Arduino_Canvas *canvas = new Arduino_Canvas(240, 240, gfx);

int16_t blinkH = 0;
bool isBlinking = false;
float scannerPos = 0;

void setup() {
  gfx->begin();
  canvas->begin();
  gfx->fillScreen(RGB565_BLACK);
}

void drawThinkingEye() {
  canvas->fillScreen(RGB565_BLACK);

  // 1. Large Circular Boundary (Glowing)
  canvas->drawCircle(120, 120, 118, 0x07E0); // Green

  // 2. The "Scanner" Line (Thinking animation)
  scannerPos += 0.05;
  int scanY = 120 + (sin(scannerPos) * 110);
  canvas->drawFastHLine(10, scanY, 220, 0x07E0);

  // 3. Central Iris (Cyber Style)
  canvas->drawCircle(120, 120, 60, 0x07E0);
  canvas->fillCircle(120, 120, 15, 0x07E0); // Pupil

  // 4. Eyelid / Blink Logic
  if (!isBlinking && random(100) > 98) isBlinking = true;

  if (isBlinking) {
    blinkH += 12;
    if (blinkH >= 120) isBlinking = false;
  } else if (blinkH > 0) {
    blinkH -= 12;
  }

  if (blinkH > 0) {
    canvas->fillRect(0, 0, 240, blinkH, RGB565_BLACK);
    canvas->fillRect(0, 240 - blinkH, 240, 240, RGB565_BLACK);
  }

  // 5. Final Push
  canvas->flush();
}

void loop() {
  drawThinkingEye();
}