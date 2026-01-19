# ANDI IoT System - Quick Start Guide

## 5-Minute Setup

### 1. Clone the repository

```bash
cd /path/to/iot-bot/raspy
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Copy .env.example to .env

```bash
cp .env.example .env
```

### 4. Edit .env with your API keys

```bash
# Open .env and add:
# - TELEGRAM_TOKEN (from @BotFather)
# - OPENAI_API_KEY (from platform.openai.com)
# - REPLICATE_API_TOKEN (from replicate.com)
# - CHAT_ID (your Telegram chat ID)
nano .env
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Test the setup

```bash
python test_components.py
```

### 7. Run the system

```bash
python main.py
```

## What Happens After Running

1. **Telegram Bot starts** - Look for initialization messages in the console
2. **Hardware initializes** - GPIO setup, camera, and sensor start
3. **Monitoring begins** - System listens for sensor triggers and mood changes

## How to Use

1. Open Telegram and message your bot with `/start`
2. Choose a mood: 😊 Happy, 😘 Flirty, 😠 Angry, or 😑 Bored
3. Point an object or hand at the ultrasonic sensor (< 5cm away)
4. System will:
   - Flash LED in warning sequence
   - Take a photo
   - Analyze with LLM based on selected mood
   - Generate audio response
   - Play the audio

## Troubleshooting Quick Fixes

| Issue                        | Solution                                       |
| ---------------------------- | ---------------------------------------------- |
| "No module named 'telegram'" | Run: `pip install -r requirements.txt`         |
| "TELEGRAM_TOKEN not set"     | Edit .env with actual token from @BotFather    |
| "Camera not found"           | Enable CSI camera in `raspi-config`            |
| "Serial connection failed"   | Enable UART in `raspi-config`                  |
| "Audio won't play"           | Check speaker connection, try different player |
| "LLM errors"                 | Verify OPENAI_API_KEY is valid in .env         |

## File Structure

```
raspy/
├── main.py                    # Run this file
├── bot.py                     # Telegram bot
├── sensor_controller.py       # Sensor & LED control
├── image_analyzer.py          # LLM analysis
├── audio_handler.py           # Text-to-speech
├── serial_handler.py          # Serial communication
├── archiver.py                # File archiving
├── test_components.py         # System test
├── README.md                  # Full documentation
├── QUICKSTART.md              # This file
├── .env                       # Your API keys (not in git)
├── requirements.txt           # Python packages
└── venv/                      # Virtual environment
```

## Next Steps

- **Customize prompts** - Edit mood prompts in `image_analyzer.py`
- **Adjust sensor threshold** - Change `< 5` in `main.py` to different distance
- **Change LED sequence** - Modify `warning_sequence()` in `sensor_controller.py`
- **Experiment with voices** - Adjust voice settings in `audio_handler.py`

## Getting Help

1. Check console output for detailed error messages
2. Run `python test_components.py` to diagnose issues
3. See [README.md](README.md) for full documentation
4. Check API key validity on their respective websites

---

**Ready to go?** Run `python main.py` and have fun! 🚀
