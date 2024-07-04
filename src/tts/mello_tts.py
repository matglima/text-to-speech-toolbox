# Code for Mello TTS
from melo.api import TTS
import re

class TTSParameters:
    def __init__(self):
        self.prompt_user_for_parameters()

    def prompt_user_for_parameters(self):
        # Prompt the user for optional input with default values
        speed_input = input("Enter the speed (default: 1.0): ") or "1.0"
        self.speed = float(speed_input)
        self.lang = input("Enter the language (default: 'EN'): ") or "EN"

        # Initialize the TTS model
        self.device = 'auto'  # Will automatically use GPU if available
        model = TTS(language=self.lang, device=self.device)
        self.speaker_ids = model.hps.data.spk2id

        # List available speaker IDs
        print("Available speaker IDs: " + ", ".join(self.speaker_ids.keys()))

        self.speaker_id = input("Enter the speaker ID (default: 'EN-BR'): ") or "EN-BR"
        if self.speaker_id not in self.speaker_ids:
            raise ValueError(f"Speaker ID '{self.speaker_id}' not found in the model's speaker ID list.")
        
        self.model = model

def preprocess_text(text):
    # Add pauses after periods
    text = re.sub(r'\. ', '. ... ', text)  # Adding ellipsis for a longer pause
    return text

def melo_tts(text, output_path, params):
    try:
        # Preprocess the text to handle pauses better
        text = preprocess_text(text)

        # Generate the audio file from the text
        params.model.tts_to_file(text, params.speaker_ids[params.speaker_id], output_path=output_path, speed=params.speed)
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

