from TTS.api import TTS
import torch


class coqui_tts(TTS):
  def __init__(self):
      super.__init__()
      self.speaker() = 'tts_models/multilingual/multi-dataset/xtts_v2'
      
  def initialize_model(self):
      self.model = TTS(model_name=self.speaker, gpu=torch.cuda.is_available())
      
  def prompt_user_for_parameters(self):
      speed_input = input("Enter the speed (default: 1.0): ") or "1.0"
      self.speed = float(speed_input)
      self.lang = input("Enter the language (default: 'en'): ") or "en"

      # List available speaker IDs
      print("Available speaker IDs: " + ", ".join(TTS.list_models())

      self.model_name = input("Enter the model name (default: 'tts_models/multilingual/multi-dataset/xtts_v2'): ") or "tts_models/multilingual/multi-dataset/xtts_v2"
      if self.model_name not in TTS.list_models():
          raise ValueError(f"Model name '{self.model_name}' not found in the model's list.")

  def convert_to_audio(self, text, output_path):
        if self.model is None:
            self.initialize_model()
        
        try:
            # Generate the audio file from the text
            self.model.tts_to_file(text, speaker=self.speaker_ids[self.speaker_id], file_path=output_path, speed=self.speed, language=self.lang)
        except ValueError as ve:
            print(f"Error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

