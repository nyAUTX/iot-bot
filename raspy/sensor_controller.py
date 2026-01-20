import os
import time
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    from picamera2 import Picamera2
    RASPBERRY_PI = True
except ImportError:
    logger.warning("RPi.GPIO or picamera2 not available - running in simulation mode")
    RASPBERRY_PI = False


class SensorController:
    """Control ultrasonic sensor, LED, and camera."""
    
    def __init__(self):
        self.TRIG = 23
        self.ECHO = 24
        self.RED = 17
        self.GREEN = 27
        self.BLUE = 22
        
        self.camera = None
        
        if RASPBERRY_PI:
            self._init_hardware()
    
    def _init_hardware(self):
        """Initialize GPIO and camera."""
        try:
            # Set GPIO warnings to false to avoid noise
            GPIO.setwarnings(False)
            
            # Check if GPIO mode is already set, if not set it
            try:
                GPIO.setmode(GPIO.BCM)
            except ValueError:
                # Mode already set, that's fine
                pass
            
            # Ultrasonic pins
            GPIO.setup(self.TRIG, GPIO.OUT)
            GPIO.setup(self.ECHO, GPIO.IN)
            
            # RGB LED pins
            GPIO.setup(self.RED, GPIO.OUT)
            GPIO.setup(self.GREEN, GPIO.OUT)
            GPIO.setup(self.BLUE, GPIO.OUT)
            
            GPIO.output(self.TRIG, False)
            
            # Camera
            self.camera = Picamera2()
            self.camera.configure(self.camera.create_still_configuration())
            self.camera.start()
            
            logger.info("Hardware initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing hardware: {e}")
    
    def set_color(self, r, g, b):
        """Set RGB LED color (0=off, 1=on)."""
        if not RASPBERRY_PI:
            return
        
        try:
            GPIO.output(self.RED, r)
            GPIO.output(self.GREEN, g)
            GPIO.output(self.BLUE, b)
        except Exception as e:
            logger.error(f"Error setting LED color: {e}")
    
    def measure_distance(self):
        """
        Measure distance using ultrasonic sensor.
        Returns distance in cm.
        """
        if not RASPBERRY_PI:
            # Simulation mode - random distance
            import random
            return random.uniform(1, 100)
        
        try:
            GPIO.output(self.TRIG, True)
            time.sleep(0.00001)
            GPIO.output(self.TRIG, False)
            
            # Wait for ECHO to go high (reduced timeout for faster response)
            timeout = time.time() + 0.05  # 50ms instead of 100ms
            pulse_start = time.time()
            while GPIO.input(self.ECHO) == 0 and time.time() < timeout:
                pulse_start = time.time()
            
            # Wait for ECHO to go low (reduced timeout)
            timeout = time.time() + 0.05  # 50ms instead of 100ms
            pulse_end = time.time()
            while GPIO.input(self.ECHO) == 1 and time.time() < timeout:
                pulse_end = time.time()
            
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            return round(distance, 2)
        except Exception as e:
            logger.error(f"Error measuring distance: {e}")
            return -1
    
    def warning_sequence(self):
        """LED warning sequence with increasing speed, ending in red."""
        logger.info("LED warning sequence started")
        try:
            # First cycle - normal speed
            for _ in range(2):
                self.set_color(0, 1, 0)   # Green
                time.sleep(0.2)
                self.set_color(1, 1, 0)   # Yellow
                time.sleep(0.2)
                self.set_color(1, 0, 0)   # Red
                time.sleep(0.2)
            
            # Second cycle - faster
            for _ in range(2):
                self.set_color(0, 1, 0)   # Green
                time.sleep(0.1)
                self.set_color(1, 1, 0)   # Yellow
                time.sleep(0.1)
                self.set_color(1, 0, 0)   # Red
                time.sleep(0.1)
            
            # Third cycle - very fast
            for _ in range(3):
                self.set_color(0, 1, 0)   # Green
                time.sleep(0.05)
                self.set_color(1, 1, 0)   # Yellow
                time.sleep(0.05)
                self.set_color(1, 0, 0)   # Red
                time.sleep(0.05)
            
            # End with red for 1 second
            self.set_color(1, 0, 0)   # Red
            time.sleep(0.5)
            self.set_color(0, 0, 0)   # Off
        except Exception as e:
            logger.error(f"Error in warning sequence: {e}")
    
    def take_photo(self, timestamp=None):
        """
        Take a photo and save it.
        Returns the path to the saved photo.
        """
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if not RASPBERRY_PI:
            logger.info(f"Simulation: Photo would be saved as photo_{timestamp}.jpg")
            # Create a dummy file for testing
            dummy_path = f"photo_{timestamp}.jpg"
            Path(dummy_path).touch()
            return dummy_path
        
        try:
            Path("photos").mkdir(parents=True, exist_ok=True)
            filename = f"photos/photo_{timestamp}.jpg"
            self.camera.capture_file(filename)
            logger.info(f"Photo saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error taking photo: {e}")
            return None
    
    def cleanup(self):
        """Clean up hardware resources."""
        logger.info("Cleaning up hardware resources")
        try:
            if RASPBERRY_PI:
                self.set_color(0, 0, 0)
                if self.camera:
                    self.camera.stop()
                    self.camera.close()
                # Only cleanup if pins were actually set up
                try:
                    GPIO.cleanup()
                except RuntimeWarning:
                    # Ignore warning if nothing to cleanup
                    pass
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
