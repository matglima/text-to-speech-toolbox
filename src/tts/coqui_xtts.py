from TTS.api import TTS
import torch
import os
# By using XTTS you agree to CPML license https://coqui.ai/cpml
os.environ["COQUI_TOS_AGREED"] = "1"
class coqui_tts:
    def __init__(self):
        self.speaker = 'tts_models/multilingual/multi-dataset/xtts_v2'
        self.model = None
        self.speed = 0.8
        self.lang = 'en'
        self.model_name = 'tts_models/multilingual/multi-dataset/xtts_v2'

        # Get the absolute path of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the path to the female.wav file
        female_wav_path = os.path.join(script_dir, "../examples/female.wav")
        
        # Print the path
        print(female_wav_path)
        self.speaker_wav = female_wav_path

    def initialize_model(self):
        self.model = TTS(model_name=self.model_name, gpu=torch.cuda.is_available())

    def prompt_user_for_parameters(self):
        speed_input = input("Enter the speed (default: 1.0): ") or "1.0"
        self.speed = float(speed_input)
        self.lang = input("Enter the language (default: 'en'): ") or "en"

        # List available models
        print("Available models: " + ", ".join(TTS.list_models()))

        self.model_name = input("Enter the model name (default: 'tts_models/multilingual/multi-dataset/xtts_v2'): ") or "tts_models/multilingual/multi-dataset/xtts_v2"
        if self.model_name not in TTS.list_models():
            raise ValueError(f"Model name '{self.model_name}' not found in the model's list.")

    def convert_to_audio(self, text, output_path):
        if self.model is None:
            self.initialize_model()
        
        try:
            # Generate the audio file from the text
            self.model.tts_to_file(text, file_path=output_path, speaker_wav=self.speaker_wav, speed=self.speed, language=self.lang)
        except ValueError as ve:
            print(f"Error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
