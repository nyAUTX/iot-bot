import os
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import replicate
import requests

load_dotenv()

logger = logging.getLogger(__name__)

# Single voice used for all moods
SINGLE_VOICE = "German_PlayfulMan"

MOOD_VOICES = {
    "happy": {
        "emotion": "happy",
        "pitch": 0,
        "speed": 1,
    },
    "flirty": {
        "emotion": "surprised",
        "pitch": 2,
        "speed": 0.9,
    },
    "angry": {
        "emotion": "disgusted",
        "pitch": -2,
        "speed": 1.2,
    },
    "bored": {
        "emotion": "sad",
        "pitch": 0,
        "speed": 0.8,
    }
}


class AudioHandler:
    """Generate and play audio using text-to-speech."""
    
    @staticmethod
    def generate_audio(text: str, mood: str = "happy", timestamp: str = None) -> str:
        """
        Generate audio from text using Replicate.
        
        Args:
            text: Text to convert to speech
            mood: Mood to use for voice generation
            timestamp: Optional timestamp for naming
        
        Returns:
            Path to generated audio file
        """
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            voice_config = MOOD_VOICES.get(mood, MOOD_VOICES["happy"])
            
            logger.info(f"Generating audio with mood: {mood}")
            logger.info(f"Voice: {SINGLE_VOICE}, Emotion: {voice_config['emotion']}")
            logger.info(f"Pitch: {voice_config['pitch']}, Speed: {voice_config['speed']}")
            logger.info(f"Text: {text[:100]}...")
            
            output = replicate.run(
                "minimax/speech-02-turbo",
                input={
                    "text": text,
                    "pitch": voice_config["pitch"],
                    "speed": voice_config["speed"],
                    "volume": 1,
                    "bitrate": 128000,
                    "channel": "mono",
                    "emotion": voice_config["emotion"],
                    "voice_id": SINGLE_VOICE,
                    "sample_rate": 32000,
                    "audio_format": "mp3",
                    "language_boost": "German",
                    "subtitle_enable": False,
                    "english_normalization": True
                }
            )
            
            # Create audio directory
            Path("audio").mkdir(parents=True, exist_ok=True)
            
            # Save audio file
            audio_path = f"audio/audio_{timestamp}.mp3"
            
            # Handle the output - Replicate returns a URL string
            if isinstance(output, str):
                logger.info(f"Downloading audio from Replicate...")
                response = requests.get(output, timeout=30)
                response.raise_for_status()
                
                with open(audio_path, "wb") as f:
                    f.write(response.content)
                    
                file_size = Path(audio_path).stat().st_size
                logger.info(f"Audio file downloaded: {audio_path} ({file_size} bytes, 128kbps @ 32kHz)")
            else:
                # Fallback: if it's a file-like object
                logger.warning("Output is not a URL, attempting direct write")
                with open(audio_path, "wb") as f:
                    if hasattr(output, 'read'):
                        f.write(output.read())
                    else:
                        f.write(output)
            
            return audio_path
        
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return None
    
    @staticmethod
    def play_audio(audio_path: str):
        """
        Play audio file.
        
        Args:
            audio_path: Path to audio file
        """
        if not Path(audio_path).exists():
            logger.error(f"Audio file not found: {audio_path}")
            return False
        
        file_size = Path(audio_path).stat().st_size
        logger.info(f"Playing audio: {audio_path} ({file_size} bytes)")
        
        # Verify file is not empty or corrupt
        if file_size < 1000:
            logger.error(f"Audio file is too small ({file_size} bytes), likely corrupt")
            return False
        
        try:
            import platform
            system = platform.system()
            
            # macOS
            if system == "Darwin":
                logger.info("Using afplay (macOS)")
                result = subprocess.run(["afplay", audio_path], check=False)
                if result.returncode == 0:
                    logger.info("Audio playback finished successfully")
                    return True
                else:
                    logger.error(f"afplay failed with return code {result.returncode}")
            
            # Linux (including Raspberry Pi)
            elif system == "Linux":
                # Prioritize players that work well with Bluetooth speakers
                players = [
                    ("play (sox)", ["play", audio_path]),  # Your tested solution
                    ("mpg123", ["mpg123", "-q", audio_path]),  # Good MP3 support with ALSA
                    ("mpg321", ["mpg321", "-q", audio_path]),  # Alternative MP3 player
                    ("cvlc", ["cvlc", "--play-and-exit", audio_path]),  # VLC without GUI
                    ("ffplay", ["ffplay", "-nodisp", "-autoexit", audio_path]),
                    ("paplay", ["paplay", audio_path])  # PulseAudio
                ]
                
                for player_name, cmd in players:
                    try:
                        logger.info(f"Trying {player_name}...")
                        result = subprocess.run(cmd, check=False,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
                        if result.returncode == 0:
                            logger.info(f"Audio playback finished successfully with {player_name}")
                            return True
                        else:
                            logger.debug(f"{player_name} returned code {result.returncode}")
                            if result.stderr:
                                logger.debug(f"{player_name} stderr: {result.stderr.decode()[:200]}")
                    except FileNotFoundError:
                        logger.debug(f"{player_name} not found")
                        continue
            
            # Windows
            elif system == "Windows":
                import winsound
                logger.info("Using winsound (Windows)")
                winsound.PlaySound(audio_path, winsound.SND_FILENAME)
                logger.info("Audio playback finished successfully")
                return True
            
            logger.warning("Could not play audio with any available player")
            return False
        
        except Exception as e:
            logger.error(f"Error playing audio: {e}", exc_info=True)
            return False
