import os
import base64
import logging
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MOOD_PROMPTS = {
    "happy": "Gib mir ein kurzes, freundliches und kreatives Mode-Kompliment zu dem Outfit auf dem Bild. Ein einziger, charmanter Satz genügt. Sei dabei so freundlich und entzückend wie möglich gegenüber dem Kleidungsstil, nach dem Motto: 'Das ist das stilvollste, was ich je gesehen habe'.",
    
    "flirty": "Gib mir einen kurzen, charmant-flirtenden Kommentar zu dem Outfit auf dem Bild. Ein einziger, verspielter Satz genügt. Sei dabei so flirtend und verführerisch wie möglich, nach dem Motto: 'Wow, in diesem Outfit siehst du einfach umwerfend aus'.",
    
    "angry": "Gib mir einen kurzen, vernichtenden Mode-Roast zu dem Outfit auf dem Bild. Ein einziger, bissiger Satz genügt. Sei dabei so arrogant und herablassend wie möglich gegenüber dem Kleidungsstil, nach dem Motto: 'Das ist das Hässlichste, was ich je gesehen habe'.",
    
    "bored": "Gib mir einen kurzen, gelangweilt-gleichgültigen Kommentar zu dem Outfit auf dem Bild. Ein einziger, langweiliger Satz genügt. Sei dabei so desinteressiert und abweisend wie möglich, nach dem Motto: 'Meh, nichts Besonderes'."
}


class ImageAnalyzer:
    """Analyze images using OpenAI Vision API."""
    
    @staticmethod
    def encode_image(path: str) -> str:
        """Encode image to base64."""
        try:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            return None
    
    @staticmethod
    def analyze_image(image_path: str, mood: str = "happy") -> str:
        """
        Analyze image using OpenAI Vision API based on mood.
        
        Args:
            image_path: Path to the image file
            mood: Mood to use for analysis (happy, flirty, angry, bored)
        
        Returns:
            Analysis text
        """
        try:
            base64_image = ImageAnalyzer.encode_image(image_path)
            if not base64_image:
                return "Konnte das Bild nicht verarbeiten."
            
            prompt = MOOD_PROMPTS.get(mood, MOOD_PROMPTS["happy"])
            
            logger.info(f"Sending image to OpenAI for analysis with mood: {mood}")
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
            )
            
            analysis = response.choices[0].message.content
            logger.info(f"Analysis completed: {analysis[:100]}...")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return "Es gab einen Fehler bei der Bildanalyse."
