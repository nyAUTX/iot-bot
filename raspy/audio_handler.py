import os
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import replicate

load_dotenv()

logger = logging.getLogger(__name__)

MOOD_VOICES = {
    "happy": {
        "emotion": "happy",
        "voice_id": "Bright_Male",
        "pitch": 0,
        "speed": 1,
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
                    "voice_id": voice_config["voice_id"],
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
            with open(audio_path, "wb") as f:
                if hasattr(output, 'read'):
                    f.write(output.read())
                else:
                    # If output is a URL string
                    import urllib.request
                    urllib.request.urlretrieve(str(output), audio_path)
            
            logger.info(f"Audio generated: {audio_path}")
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
            return
        
        try:
            logger.info(f"Playing audio: {audio_path}")
            
            # Try different players based on OS
            try:
                # macOS
                subprocess.run(["afplay", audio_path], check=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                try:
                    # Linux
                    subprocess.run(["mpg123", audio_path], check=True)
                except FileNotFoundError:
                    try:
                        # Linux alternative
                        subprocess.run(["aplay", audio_path], check=True)
                    except FileNotFoundError:
                        try:
                            # Windows
                            import winsound
                            winsound.PlaySound(audio_path, winsound.SND_FILENAME)
                        except (ImportError, Exception):
                            logger.warning("No audio player found. Audio generated but not played.")
            
            logger.info("Audio playback finished")
        
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
