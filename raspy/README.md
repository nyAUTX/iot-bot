# ANDI IoT System - Complete Setup Guide

A fully integrated IoT system that uses a Telegram bot to control mood-based fashion analysis with LLM and audio feedback.

## System Architecture

```
Telegram Bot (mood selection)
        ↓
    Mood State
        ↓ ├─→ Serial Communication (send mood to device)
        ├─→ Sensor Monitoring (ultrasound distance)
            ↓
        Sensor Triggered (< 5cm)
            ↓
        LED Warning Sequence
            ↓
        Take Photo
            ↓
        Archive Photo (if exists)
            ↓
        LLM Analysis (mood-based)
            ↓
        Generate Audio (Replicate TTS)
            ↓
        Archive Audio (if exists)
            ↓
        Play Audio
```

## Components

### Core Files

- **main.py** - Main orchestrator that coordinates all components
- **bot.py** - Telegram bot for mood control (happy, flirty, angry, bored)
- **sensor_controller.py** - Ultrasonic sensor, LED, and camera control
- **image_analyzer.py** - LLM-based image analysis with mood-specific prompts
- **audio_handler.py** - Text-to-speech audio generation and playback
- **serial_handler.py** - Serial communication with external devices
- **archiver.py** - File archiving utility with timestamps

### Configuration Files

- **.env** - Environment variables (TELEGRAM_TOKEN, OPENAI_API_KEY, CHAT_ID, REPLICATE_API_TOKEN)
- **requirements.txt** - Python dependencies

## Setup Instructions

### 1. Prerequisites

#### On Raspberry Pi:

```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv
sudo apt-get install libatlas-base-dev libjasper-dev libtiff5 libjasper1 libharfbuzz0b libwebp6 libopenjp2-7 libtiff5
```

#### On macOS (for development/testing):

```bash
# Already has Python and audio support
```

### 2. Clone and Setup Virtual Environment

```bash
cd /path/to/iot-bot/raspy
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configuration - Create .env File

Create a `.env` file in the project root with your API keys:

```env
# Telegram Bot
TELEGRAM_TOKEN=your_telegram_bot_token_here
CHAT_ID=your_chat_id_here

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Replicate (for text-to-speech)
REPLICATE_API_TOKEN=your_replicate_api_token_here
```

#### How to get these tokens:

**Telegram Token:**

1. Start a chat with @BotFather on Telegram
2. Use `/newbot` command
3. Follow instructions and copy the token

**Chat ID:**

1. After creating bot, send any message to your bot
2. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find your chat_id in the response

**OpenAI API Key:**

1. Go to https://platform.openai.com/account/api-keys
2. Create new API key and copy it

**Replicate API Token:**

1. Go to https://replicate.com/account/api-tokens
2. Create and copy your API token

### 5. Hardware Setup (Raspberry Pi)

#### GPIO Pins Used:

- **Ultrasonic Sensor:**
  - TRIG: GPIO 23
  - ECHO: GPIO 24

- **RGB LED:**
  - RED: GPIO 17
  - GREEN: GPIO 27
  - BLUE: GPIO 22

- **Camera:** CSI Camera connector (Picamera2)

- **Serial:** UART on /dev/serial0 (115200 baud)

#### Wiring:

1. Connect ultrasonic sensor to TRIG (GPIO 23) and ECHO (GPIO 24)
2. Connect RGB LED with resistors to RED, GREEN, BLUE GPIO pins
3. Enable CSI camera in `sudo raspi-config` under Interface Options
4. Enable serial port and disable terminal if using UART

### 6. Run the System

```bash
python main.py
```

The system will:

1. Start the Telegram bot
2. Initialize hardware (sensor, LED, camera)
3. Begin monitoring distance
4. Listen for mood changes from Telegram

## Usage

### Control via Telegram Bot

1. Send `/start` to the bot
2. Choose a mood:
   - 😊 **Happy** - Friendly, complimentary fashion analysis
   - 😘 **Flirty** - Charming, flirting fashion comments
   - 😠 **Angry** - Harsh, critical fashion roasts
   - 😑 **Bored** - Disinterested, dismissive comments

3. When the ultrasonic sensor is covered (distance < 5cm):
   - LED will flash in warning sequence (Green → Yellow → Red)
   - Photo is captured and analyzed
   - LLM generates mood-based response
   - Audio is generated and played
   - Both image and audio are archived with timestamps

### File Organization

```
raspy/
├── photo.jpg                    # Latest captured photo
├── audio.mp3                   # Latest generated audio
├── photos/
│   ├── photo_20240119_123456.jpg
│   └── archive/
│       ├── photo_20240118_143022.jpg
│       └── ...
├── audio/
│   ├── audio_20240119_123456.mp3
│   └── archive/
│       ├── audio_20240118_143022.mp3
│       └── ...
└── venv/                       # Virtual environment
```

## Mood-Based Responses

### Happy Mode 😊

- Friendly, complimentary analysis
- Voice: Bright, positive tone
- Speed: Normal

### Flirty Mode 😘

- Charming, playful analysis
- Voice: Excited, higher pitch
- Speed: Slightly faster

### Angry Mode 😠

- Harsh, critical roasts
- Voice: Angry, deeper tone
- Speed: Faster and more aggressive

### Bored Mode 😑

- Dismissive, uninterested comments
- Voice: Sad, calm tone
- Speed: Slower and monotone

## Troubleshooting

### Serial Connection Issues

- Check if `/dev/serial0` is available (Raspberry Pi)
- Ensure UART is enabled in raspi-config
- Verify baudrate is 115200

### Camera Issues

- Run `libcamera-hello` to test camera
- Check camera ribbon cable connection
- Ensure camera is enabled in raspi-config

### Audio Playback Not Working

- On Raspberry Pi: Ensure audio jack or HDMI is configured
- On macOS: System should play audio automatically
- Install `mpg123` on Linux: `sudo apt-get install mpg123`

### Telegram Bot Not Responding

- Verify TELEGRAM_TOKEN in .env
- Check if bot is running (no errors in console)
- Ensure internet connection

### LLM Analysis Errors

- Verify OPENAI_API_KEY is valid
- Check API usage limits
- Ensure image file exists and is readable

### Audio Generation Issues

- Verify REPLICATE_API_TOKEN is valid
- Check internet connection for Replicate API
- Ensure text is in German for best results

## Development & Testing

### Run in Simulation Mode

The system automatically detects if running on Raspberry Pi. If not:

- Sensor returns random distances (1-100 cm)
- LED commands are logged (not executed)
- Camera creates dummy files
- Serial communication is logged (not executed)

### Enable Debug Logging

Add to main.py:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```python
# Test image analyzer
from image_analyzer import ImageAnalyzer
response = ImageAnalyzer.analyze_image("test.jpg", "happy")

# Test audio generation
from audio_handler import AudioHandler
AudioHandler.generate_audio("Das ist ein Test!", "happy")
AudioHandler.play_audio("audio.mp3")

# Test sensor
from sensor_controller import SensorController
sensor = SensorController()
distance = sensor.measure_distance()
```

## Performance Notes

- Serial communication: 115200 baud, non-blocking
- Sensor polling: 200ms intervals (adjustable)
- LLM analysis: ~2-5 seconds per image
- Audio generation: ~3-10 seconds per response
- Total latency from trigger to audio playback: ~10-20 seconds

## License

Project for FH IOT Course

## Support

For issues or questions, check:

1. Console logs for detailed error messages
2. .env configuration
3. Hardware connections
4. API key validity
