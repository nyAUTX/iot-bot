import asyncio
import os
import logging
import threading
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import modules (removed bot import)
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
mood_file_path = "mood.txt"


def read_mood_from_file():
    """Read current mood from mood.txt file."""
    try:
        if Path(mood_file_path).exists():
            with open(mood_file_path, "r") as f:
                mood = f.read().strip()
                if mood in ["happy", "flirty", "angry", "bored"]:
                    return mood
    except Exception as e:
        logger.error(f"Error reading mood file: {e}")
    return "happy"  # default


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
    # For simple reads we can return without lock; mood changes are infrequent
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
                await asyncio.sleep(3)

            await asyncio.sleep(0.2)

    except KeyboardInterrupt:
        logger.info("Sensor loop interrupted")
    except Exception as e:
        logger.error(f"Error in sensor loop: {e}", exc_info=True)
    finally:
        sensor_controller.cleanup()


async def mood_watcher_loop():
    """Watch mood.txt file for changes and update mood."""
    logger.info("Starting mood file watcher...")
    last_modified = None
    
    try:
        while True:
            try:
                if Path(mood_file_path).exists():
                    current_modified = Path(mood_file_path).stat().st_mtime
                    
                    # Check if file was modified
                    if last_modified is None or current_modified != last_modified:
                        last_modified = current_modified
                        new_mood = read_mood_from_file()
                        set_mood(new_mood)
                        
            except Exception as e:
                logger.error(f"Error in mood watcher: {e}")
            
            await asyncio.sleep(0.5)  # Check every 500ms
            
    except Exception as e:
        logger.error(f"Error in mood watcher loop: {e}", exc_info=True)


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
    
    # Create mood.txt if it doesn't exist
    if not Path(mood_file_path).exists():
        with open(mood_file_path, "w") as f:
            f.write("happy")
        logger.info("Created mood.txt with default mood: happy")
    
    # Read initial mood from file
    initial_mood = read_mood_from_file()
    set_mood(initial_mood)
    
    logger.info("System ready. Start bot.py separately to control mood.")
    logger.info("Watching mood.txt for changes...")
    
    # Run async loops
    try:
        await asyncio.gather(
            sensor_loop(),
            serial_receive_loop(),
            mood_watcher_loop()  # Watch mood file
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
