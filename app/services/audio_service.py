from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AudioService:
    def __init__(self):
        pass

    def text_to_speech(self, text: str, output_path="output.mp3"):
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text,
        ) as response:
            response.stream_to_file(output_path)
        return output_path
