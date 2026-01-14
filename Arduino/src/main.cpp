#include <Arduino_GFX_Library.h>

#define TFT_CS   10
#define TFT_DC    9
#define TFT_RST   8

Arduino_DataBus *bus = new Arduino_HWSPI(TFT_DC, TFT_CS);
Arduino_GFX *gfx = new Arduino_GC9A01(bus, TFT_RST, 0, true);

// 80x80 Canvas (approx 12.8KB RAM - safe for UNO R4)
// A larger canvas allows the iris to move inside it without needing external repair
Arduino_Canvas *canvas = new Arduino_Canvas(80, 80, gfx);

int16_t curX = 80, curY = 80;
int16_t targetX = 80, targetY = 80;

void setup() {
  gfx->begin();
  gfx->fillScreen(RGB565_BLACK);

  // Static background: White eye socket
  gfx->fillCircle(120, 120, 110, RGB565_WHITE);

  canvas->begin();
}

void drawSmoothEye(int16_t x, int16_t y) {
  // --- EVERYTHING HAPPENS ON THE CANVAS FIRST ---
  // This clears the canvas to white (no flickering on main screen)
  canvas->fillScreen(RGB565_WHITE);

  // Draw iris/pupil in the center of the 80x80 canvas
  // We use 40,40 as the center of our 80x80 box
  canvas->fillCircle(40, 40, 30, RGB565_BLUE);   // Iris
  canvas->fillCircle(40, 40, 14, RGB565_BLACK);  // Pupil
  canvas->fillCircle(30, 30, 6, RGB565_WHITE);   // Glint

  // --- ONE SINGLE PUSH TO SCREEN ---
  // We push the whole 80x80 block.
  // Because the background of the canvas is white, it naturally
  // "erases" the previous iris position as it moves.
  gfx->draw16bitRGBBitmap(x, y, (uint16_t*)canvas->getFramebuffer(), 80, 80);
}

void loop() {
  // Move toward target
  if (curX < targetX) curX++;
  else if (curX > targetX) curX--;

  if (curY < targetY) curY++;
  else if (curY > targetY) curY--;

  drawSmoothEye(curX, curY);

  if (curX == targetX && curY == targetY) {
    delay(random(500, 1500));
    // Set target so the 80x80 box stays within the 240x240 screen
    targetX = random(40, 120);
    targetY = random(40, 120);
  }

  delay(2); // Faster delay for smoother motion
}