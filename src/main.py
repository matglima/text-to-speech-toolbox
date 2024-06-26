import argparse
import os
from pydub import AudioSegment
from IPython.display import Audio, display

from tts.mello_tts import mello_tts
from tts.google_tts import google_tts
from tts.edge_tts import edge_tts_CLI


# Usage: python main.py path/to/text/file.txt path/to/output/folder --tts_tool google --chunk_length 60


def text_to_speech(text, output_file, tts_tool):
    if tts_tool == 'mello':
        mello_tts(text, output_file)
    elif tts_tool == 'google':
        google_tts(text, output_file)
    elif tts_tool == 'edge':
        edge_tts_CLI(text, output_file)
    else:
        raise ValueError(f"Unknown TTS tool: {tts_tool}")

def convert_chunks_to_audio(chunks, output_folder, tts_tool):
    audio_files = []  # List to store the paths of generated audio files

    # Iterate over each chunk of text
    for i, chunk in enumerate(chunks):
        # Define the path for the output audio file
        output_file = os.path.join(output_folder, f"chunk_{i+1}.mp3")

        # Convert the text chunk to speech and save as an audio file
        text_to_speech(chunk, output_file, tts_tool)

        # Append the path of the created audio file to the list
        audio_files.append(output_file)

    return audio_files  # Return the list of audio file paths

def split_audio_to_chunks(audio_file, chunk_length_ms):
    audio = AudioSegment.from_file(audio_file)
    return [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

def main():
    parser = argparse.ArgumentParser(description='Text to Speech Converter')
    parser.add_argument('text_path', type=str, help='Path to the text file to convert')
    parser.add_argument('output_folder', type=str, help='Folder to save the output audio files')
    parser.add_argument('--tts_tool', type=str, choices=['mello', 'google', 'edge'], default='google', help='TTS tool to use')
    parser.add_argument('--chunk_length', type=int, default=60, help='Chunk length in seconds')

    args = parser.parse_args()

    # Create the output folder if it doesn't exist
    os.makedirs(args.output_folder, exist_ok=True)

    # Read the content of the text file
    with open(args.text_path, 'r') as file:
        text = file.read()

    # Split text into chunks
    chunk_length_ms = args.chunk_length * 1000  # Convert seconds to milliseconds
    chunks = [text[i:i + chunk_length_ms] for i in range(0, len(text), chunk_length_ms)]

    # Convert text chunks to audio
    audio_files = convert_chunks_to_audio(chunks, args.output_folder, args.tts_tool)

    # Display each chunk
    for i, audio_file in enumerate(audio_files):
        print(f"Playing chunk {audio_file}")
        display(Audio(audio_file, autoplay=True))

if __name__ == "__main__":
    main()