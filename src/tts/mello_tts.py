# Code for Mello TTS
from melo.api import TTS

def mello_tts(text, output_path):
    try:
        # Device selection
        device = 'auto'  # Will automatically use GPU if available

        # Prompt the user for optional input with default values
        speed_input = input("Enter the speed (default: 1.0): ") or "1.0"
        speed = float(speed_input)
        lang = input("Enter the language (default: 'EN'): ") or "EN"

        # Initialize the TTS model
        model = TTS(language=lang, device=device)
        speaker_ids = model.hps.data.spk2id

        # List available speaker IDs
        print("Available speaker IDs: " + ", ".join(speaker_ids.keys()))

        speaker_id = input("Enter the speaker ID (default: 'EN-BR'): ") or "EN-BR"

        # Ensure the entered speaker ID exists
        if speaker_id not in speaker_ids:
            raise ValueError(f"Speaker ID '{speaker_id}' not found in the model's speaker ID list.")

        # Generate the audio file from the text
        model.tts_to_file(text, speaker_ids[speaker_id], output_path=output_path, speed=speed)
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")