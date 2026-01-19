import os
import base64
import replicate
import asyncio
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()

current_mode = "good"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GOOD_PROMPT = "Gib mir ein kurzes, freundliches und kreatives Mode-Kompliment zu dem Outfit auf dem Bild. Ein einziger, charmanter Satz genügt. Sei dabei so freundlich und entzückend wie möglich gegenüber dem Kleidungsstil, nach dem Motto: ‚Das ist das stilvollste, was ich je gesehen habe"
EVIL_PROMPT = "Gib mir einen kurzen, vernichtenden Mode-Roast zu dem Outfit auf dem Bild. Ein einziger, bissiger Satz genügt. Sei dabei so arrogant und herablassend wie möglich gegenüber dem Kleidungsstil, nach dem Motto: ‚Das ist das Hässlichste, was ich je gesehen habe"

def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

image_path = "luki.jpeg" 

def check_mood():
    with open("mood.txt", "r") as file:
        return file.read()
    
def check_for_image():
    image = Path(image_path)
    if image.is_file():
        return True
    else:
        return False

def judge_image_fashion(image_url: str):
    PROMPT = GOOD_PROMPT if current_mode == "good" else EVIL_PROMPT
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": PROMPT,
                    },
                    {"type": "input_image", "image_url": f"data:image/png;base64,{base64_image}"},
                ],
            }
        ],
    )

    return response.output[0].content[0].text


def generate_audio_from_text(text: str):
    output = replicate.run(
    "minimax/speech-02-turbo",
    input={
        "text": text,
        "pitch": 0,
        "speed": 1,
        "volume": 1,
        "bitrate": 128000,
        "channel": "mono",
        "emotion": "angry",
        "voice_id": "Deep_Voice_Man",
        "sample_rate": 32000,
        "audio_format": "mp3",
        "language_boost": "German",
        "subtitle_enable": False,
        "english_normalization": True
    }
    )

    # To access the file URL:
    print(output.url)
    #=> "http://example.com"

    # To write the file to disk:
    with open("my-audio.mp3", "wb") as file:
        file.write(output.read())


if __name__ == "__main__":
    while True:
        if check_for_image():
            mood = check_mood()
            print("Mood: ", mood)
            base64_image = encode_image(image_path)
            comment = judge_image_fashion(base64_image)
            print("Generated Comment:", comment)
            #generate_audio_from_text(comment)
        print("Waiting for image...")
        time.sleep(10)