from TTS.api import TTS
import torch


class coqui_tts(TTS):
  def __init__(self):
      super.__init__()
      self.e() = 'tts_models/multilingual/multi-dataset/xtts_v2'
      
  def initialize_model(self):
      self.model = TTS(self.model_name, gpu=torch.cuda.is_available())
      
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
            self.model.tts_to_file(text, self.speaker_ids[self.speaker_id], output_path=output_path, speed=self.speed)
        except ValueError as ve:
            print(f"Error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    











# generate speech by cloning a voice using default settings
tts.tts_to_file(text="It took me quite a long time to develop a voice, and now that I have it I'm not going to be silent.",
                file_path="output.wav",
                speaker_wav="/path/to/target/speaker.wav",
                language="en")


