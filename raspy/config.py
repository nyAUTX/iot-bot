"""
Configuration file for ANDI IoT System
Adjust these parameters to customize system behavior
"""

# ==================== SENSOR CONFIGURATION ====================

# Distance threshold for sensor trigger (in cm)
DISTANCE_TRIGGER_THRESHOLD = 5

# Sensor polling interval (in seconds)
SENSOR_POLL_INTERVAL = 0.2

# Delay after trigger to prevent multiple triggers (in seconds)
TRIGGER_DEBOUNCE_DELAY = 3

# ==================== LED CONFIGURATION ====================

# LED warning sequence colors (R, G, B)
LED_COLORS = {
    "green": (0, 1, 0),
    "yellow": (1, 1, 0),
    "red": (1, 0, 0),
    "off": (0, 0, 0)
}

# LED blink timing (in seconds)
LED_ON_TIME = 0.3
LED_OFF_TIME = 0.1
LED_BLINKS = 5  # Total blinks in sequence

# ==================== HARDWARE PINS ====================

# Ultrasonic sensor GPIO pins
ULTRASONIC_TRIG = 23
ULTRASONIC_ECHO = 24

# RGB LED GPIO pins
LED_RED = 17
LED_GREEN = 27
LED_BLUE = 22

# Serial port configuration
SERIAL_PORT = '/dev/serial0'
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1

# Camera
CAMERA_RESOLUTION = (1920, 1080)

# ==================== FILE PATHS ====================

PHOTO_DIR = "photos"
PHOTO_ARCHIVE_DIR = "photos/archive"
AUDIO_DIR = "audio"
AUDIO_ARCHIVE_DIR = "audio/archive"

CURRENT_PHOTO_FILE = "photo.jpg"
CURRENT_AUDIO_FILE = "audio.mp3"

# ==================== MOODS ====================

AVAILABLE_MOODS = ["happy", "flirty", "angry", "bored"]
DEFAULT_MOOD = "happy"

# ==================== LLM CONFIGURATION ====================

# OpenAI model for image analysis
LLM_MODEL = "gpt-4o-mini"

# Temperature for responses (0.0 = deterministic, 1.0 = random)
LLM_TEMPERATURE = 0.8

# ==================== AUDIO CONFIGURATION ====================

# Text-to-speech service
TTS_SERVICE = "minimax/speech-02-turbo"

# Audio parameters
AUDIO_BITRATE = 128000
AUDIO_SAMPLE_RATE = 32000
AUDIO_FORMAT = "mp3"
AUDIO_CHANNEL = "mono"

# Default audio settings per mood
AUDIO_SETTINGS = {
    "happy": {
        "emotion": "happy",
        "voice_id": "Bright_Male",
        "pitch": 0,
        "speed": 1.0,
    },
    "flirty": {
        "emotion": "excited",
        "voice_id": "Deep_Voice_Woman",
        "pitch": 2,
        "speed": 0.9,
    },
    "angry": {
        "emotion": "angry",
        "voice_id": "Deep_Voice_Man",
        "pitch": -2,
        "speed": 1.2,
    },
    "bored": {
        "emotion": "sad",
        "voice_id": "Calm_Male",
        "pitch": 0,
        "speed": 0.8,
    }
}

# ==================== LOGGING ====================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ==================== TELEGRAM ====================

# Telegram button keyboard
KEYBOARD = [
    ["😊 Happy", "😘 Flirty"],
    ["😠 Angry", "😑 Bored"]
]

# ==================== DEBUG MODE ====================

# Enable debug logging and extra info
DEBUG = False

# Simulate hardware if not on Raspberry Pi
SIMULATE_HARDWARE = True  # Set to False to require real hardware

# Mock sensor trigger for testing (distance in cm)
MOCK_TRIGGER_DISTANCE = None  # Set to a number to auto-trigger at that distance
