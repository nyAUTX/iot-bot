import logging
import time

logger = logging.getLogger(__name__)

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    logger.warning("pyserial not available - running in simulation mode")
    SERIAL_AVAILABLE = False


class SerialHandler:
    """Handle serial communication with device."""
    
    def __init__(self, port='/dev/serial0', baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        
        if SERIAL_AVAILABLE:
            self._init_serial()
    
    def _init_serial(self):
        """Initialize serial connection."""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(2)  # Wait for connection to stabilize
            logger.info(f"Serial connection established on {self.port}")
        except Exception as e:
            logger.error(f"Error initializing serial connection: {e}")
            self.ser = None
    
    def send_mood(self, mood: str):
        """
        Send mood command to device over serial.
        
        Args:
            mood: Mood string (happy, flirty, angry, bored)
        """
        if not self.ser:
            logger.debug(f"[SIMULATION] Would send mood: {mood}")
            return
        
        try:
            message = f"MOOD:{mood}\n".encode()
            self.ser.write(message)
            logger.info(f"Mood sent over serial: {mood}")
        except Exception as e:
            logger.error(f"Error sending mood over serial: {e}")
    
    def send_message(self, message: str):
        """
        Send a message over serial.
        
        Args:
            message: Message to send
        """
        if not self.ser:
            logger.debug(f"[SIMULATION] Would send message: {message}")
            return
        
        try:
            if not message.endswith('\n'):
                message += '\n'
            self.ser.write(message.encode())
            logger.info(f"Message sent over serial: {message.strip()}")
        except Exception as e:
            logger.error(f"Error sending message over serial: {e}")
    
    def read_message(self) -> str:
        """
        Read a message from serial.
        
        Returns:
            Message string or None
        """
        if not self.ser:
            return None
        
        try:
            if self.ser.in_waiting:
                message = self.ser.readline().decode().strip()
                if message:
                    logger.debug(f"Received from serial: {message}")
                    return message
        except Exception as e:
            logger.error(f"Error reading from serial: {e}")
        
        return None
    
    def close(self):
        """Close serial connection."""
        if self.ser:
            try:
                self.ser.close()
                logger.info("Serial connection closed")
            except Exception as e:
                logger.error(f"Error closing serial connection: {e}")
