# Code for Mello TTS
from melo.api import TTS
import re

class melo_tts:
    def __init__(self):
        self.device = 'auto'
        self.lang = 'EN'
        self.speed = 0.8
        self.speaker_id = 'EN-BR'
        self.model = None
        self.speaker_ids = None

    def initialize_model(self):
        # Initialize the TTS model
        self.model = TTS(language=self.lang, device=self.device)
        self.speaker_ids = self.model.hps.data.spk2id

    def prompt_user_for_parameters(self):
        # Prompt the user for optional input with default values
        speed_input = input("Enter the speed (default: 1.0): ") or "1.0"
        self.speed = float(speed_input)
        self.lang = input("Enter the language (default: 'EN'): ") or "EN"

        self.initialize_model()

        # List available speaker IDs
        print("Available speaker IDs: " + ", ".join(self.speaker_ids.keys()))

        self.speaker_id = input("Enter the speaker ID (default: 'EN-BR'): ") or "EN-BR"
        if self.speaker_id not in self.speaker_ids:
            raise ValueError(f"Speaker ID '{self.speaker_id}' not found in the model's speaker ID list.")

    def preprocess_text(self, text):
        # Add pauses after periods
        text = re.sub(r'\. ', '. ... ', text)  # Adding ellipsis for a longer pause
        return text

    def convert_to_audio(self, text, output_path):
        if self.model is None:
            self.initialize_model()
        
        try:
            # Preprocess the text to handle pauses better
            text = self.preprocess_text(text)

            # Generate the audio file from the text
            self.model.tts_to_file(text, self.speaker_ids[self.speaker_id], output_path=output_path, speed=self.speed)
        except ValueError as ve:
            print(f"Error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# Example usage
if __name__ == "__main__":
    tts = melo_tts()
    tts.prompt_user_for_parameters()
    text_to_convert = input("Enter the text to convert to audio: ")
    output_file_path = input("Enter the output file path: ")
    tts.convert_to_audio(text_to_convert, output_file_path)
