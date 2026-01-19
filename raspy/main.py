import asyncio
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import logging

# Import modules
from bot import start_telegram_bot
from sensor_controller import SensorController
from image_analyzer import ImageAnalyzer
from serial_handler import SerialHandler
from audio_handler import AudioHandler
from archiver import Archiver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Global state
current_mood = "happy"
mood_lock = threading.Lock()


def set_mood(new_mood):
    """Update the current mood and send it over serial."""
    global current_mood
    with mood_lock:
        if current_mood != new_mood:
            current_mood = new_mood
            logger.info(f"Mood changed to: {current_mood}")
            # Send mood over serial
            serial_handler.send_mood(current_mood)
            return True
    return False


def get_mood():
    """Get the current mood safely."""
    with mood_lock:
        return current_mood


def initialize_directories():
    """Create necessary directories if they don't exist."""
    directories = ["photos", "photos/archive", "audio", "audio/archive"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ensured: {directory}")


async def sensor_loop():
    """Continuously monitor the ultrasound sensor."""
    logger.info("Starting sensor monitoring loop...")
    try:
        while True:
            distance = sensor_controller.measure_distance()
            logger.debug(f"Distance: {distance} cm")

            # Trigger when sensor is covered (< 5 cm)
            if distance < 5:
                logger.info("Sensor covered! Triggering photo capture...")
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Warning LED sequence
                sensor_controller.warning_sequence()
                
                # Take photo
                photo_path = sensor_controller.take_photo(timestamp)
                logger.info(f"Photo captured: {photo_path}")
                
                # Archive existing photo if it exists
                if Path("photo.jpg").exists():
                    archiver.archive_file("photo.jpg", "photos/archive")
                
                # Move captured photo to photo.jpg
                import shutil
                shutil.move(photo_path, "photo.jpg")
                logger.info("Photo saved as photo.jpg")
                
                # Analyze image with LLM
                mood = get_mood()
                logger.info(f"Analyzing image with mood: {mood}")
                response_text = image_analyzer.analyze_image("photo.jpg", mood)
                logger.info(f"LLM Response: {response_text}")
                
                # Generate and play audio
                audio_path = audio_handler.generate_audio(response_text, mood, timestamp)
                logger.info(f"Audio generated: {audio_path}")
                
                # Archive existing audio if it exists
                if Path("audio.mp3").exists():
                    archiver.archive_file("audio.mp3", "audio/archive")
                
                # Move to audio.mp3 and play
                import shutil
                shutil.move(audio_path, "audio.mp3")
                audio_handler.play_audio("audio.mp3")
                logger.info("Audio played")
                
                # Prevent multiple triggers
                time.sleep(3)

            await asyncio.sleep(0.2)

    except KeyboardInterrupt:
        logger.info("Sensor loop interrupted")
    except Exception as e:
        logger.error(f"Error in sensor loop: {e}", exc_info=True)
    finally:
        sensor_controller.cleanup()


async def serial_receive_loop():
    """Listen for serial messages (if device sends data)."""
    logger.info("Starting serial receive loop...")
    try:
        while True:
            message = serial_handler.read_message()
            if message:
                logger.info(f"Received from device: {message}")
            await asyncio.sleep(0.5)
    except Exception as e:
        logger.error(f"Error in serial loop: {e}", exc_info=True)


async def main():
    """Main async orchestrator."""
    logger.info("=" * 50)
    logger.info("ANDI IoT System Starting...")
    logger.info("=" * 50)
    
    # Initialize
    initialize_directories()
    
    # Start components
    logger.info("Initializing components...")
    
    # Start Telegram bot in a separate thread
    bot_thread = threading.Thread(target=lambda: asyncio.run(start_telegram_bot(set_mood)), daemon=True)
    bot_thread.start()
    logger.info("Telegram bot started")
    time.sleep(2)  # Give bot time to initialize
    
    # Run async loops
    try:
        await asyncio.gather(
            sensor_loop(),
            serial_receive_loop()
        )
    except KeyboardInterrupt:
        logger.info("System shutdown requested")
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
    finally:
        logger.info("ANDI System shutting down...")
        sensor_controller.cleanup()


if __name__ == "__main__":
    # Initialize global handlers
    sensor_controller = SensorController()
    image_analyzer = ImageAnalyzer()
    serial_handler = SerialHandler()
    audio_handler = AudioHandler()
    archiver = Archiver()
    
    # Run main system
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Main interrupted - exiting")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
