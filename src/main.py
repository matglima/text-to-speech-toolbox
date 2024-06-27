import argparse
import os
from pydub import AudioSegment
from IPython.display import Audio, display
import chardet

from tts.mello_tts import mello_tts
from tts.google_tts import google_tts
from tts.edge_tts import edge_tts_CLI
from utils.pdf_extractor import pdf_to_markdown, markdown_to_plain_text, split_text_to_chunks, add_spaces_to_text

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

def convert_chunks_to_audio(chunks, output_folder, tts_tool, combined_output_file):
    combined_audio = AudioSegment.empty()  # Initialize an empty AudioSegment

    # Iterate over each chunk of text
    for i, chunk in enumerate(chunks):
        # Define a temporary path for the output audio file
        temp_output_file = os.path.join(output_folder, f"chunk_{i+1}.mp3")
        print(f"Processing chunk {i+1}: {temp_output_file}")

        # Convert the text chunk to speech and save as a temporary audio file
        text_to_speech(chunk, temp_output_file, tts_tool)

        # Check if the file was created
        if not os.path.exists(temp_output_file):
            print(f"Failed to create audio file: {temp_output_file}")
            continue

        # Load the temporary audio file and concatenate it to the combined audio
        chunk_audio = AudioSegment.from_file(temp_output_file)
        combined_audio += chunk_audio

        # Optionally, remove the temporary file to save space
        os.remove(temp_output_file)

    # Export the combined audio file
    combined_audio.export(combined_output_file, format="mp3")
    return combined_output_file  # Return the path of the combined audio file

def split_audio_to_chunks(audio_file, chunk_length_ms):
    audio = AudioSegment.from_file(audio_file)
    return [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def main():
    parser = argparse.ArgumentParser(description='Text to Speech Converter')
    parser.add_argument('text_path', type=str, help='Path to the text file to convert')
    parser.add_argument('output_folder', type=str, help='Folder to save the output audio files')
    parser.add_argument('--tts_tool', type=str, choices=['mello', 'google', 'edge'], default='google', help='TTS tool to use')
    parser.add_argument('--chunk_length', type=int, default=60, help='Chunk length in seconds')

    args = parser.parse_args()

    # Create the output folder if it doesn't exist
    os.makedirs(args.output_folder, exist_ok=True)

    # Detect the encoding of the text file
    encoding = detect_encoding(args.text_path)
    print(f"Detected encoding: {encoding}")

    try:
        # Read the content of the text file with the detected encoding
        with open(args.text_path, 'r', encoding=encoding) as file:
            text = file.read()
    except UnicodeDecodeError:
        # If decoding fails, try with a different encoding or handle the error
        print(f"Failed to decode file with encoding {encoding}. Trying 'utf-8' with errors='ignore'.")
        with open(args.text_path, 'r', encoding='utf-8', errors='ignore') as file:
            text = file.read()

    # Convert pdf to markdown (assumes text_path is a PDF file)
    markdown_text = pdf_to_markdown(args.text_path, page_numbers=[1])

    # Convert markdown to plain text
    plain_text = markdown_to_plain_text(markdown_text)
    
    # Split text into chunks
    chunks = split_text_to_chunks(plain_text)
    
    # Add spaces to each chunk (if required by your text processing)
    chunks = [add_spaces_to_text(chunk) for chunk in chunks]

    # Define the path for the combined output audio file
    combined_output_file = os.path.join(args.output_folder, "combined_audio.mp3")

    # Convert text chunks to a single audio file
    combined_audio_file = convert_chunks_to_audio(chunks, args.output_folder, args.tts_tool, combined_output_file)

    # # Display the combined audio file
    # print(f"Playing combined audio file {combined_audio_file}")
    # display(Audio(combined_audio_file, autoplay=True))

if __name__ == "__main__":
    main()
