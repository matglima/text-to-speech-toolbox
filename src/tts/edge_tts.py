# Code for Edge TTS
import subprocess

def edge_tts_CLI(text, output_file, voice_model='pt-BR-ThalitaNeural'):
  # Define the command to execute
  command = f'edge-tts --voice {voice_model} --file {text} --write-media {output_file}'

  try:
      # Execute the command and check for errors
      result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
      print(result.stdout)
  except subprocess.CalledProcessError as e:
      print(f"Command '{command}' failed with return code {e.returncode}")
      print(e.output)
