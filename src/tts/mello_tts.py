# Code for Mello TTS
from melo.api import TTS

def mello_tts(text, output_path, speed=1.0, speaker_id='EN-BR', lang='EN'):
  # Device selection
  device = 'auto'  # Will automatically use GPU if available

  # Initialize the TTS model
  model = TTS(language=lang, device=device)
  speaker_ids = model.hps.data.spk2id

  # Ensure the 'EN-BR' speaker ID exists
  if 'EN-BR' not in speaker_ids:
      raise ValueError("Speaker ID 'EN-BR' not found in the model's speaker ID list.")

  # Output path for the generated audio
  output_path = 'en-br.wav'

  # Generate the audio file from the text
  model.tts_to_file(text, speaker_ids[speaker_id], output_path=output_path, speed=speed)

