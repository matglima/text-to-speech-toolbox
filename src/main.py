import argparse
import os
import logging
from typing import List
from pydub import AudioSegment
from IPython.display import Audio, display
import chardet
import subprocess

from tts.mello_tts import melo_tts, TTSParameters
from tts.google_tts import google_tts
from tts.edge_tts import edge_tts_CLI
from utils.pdf_extractor import pdf_to_markdown, markdown_to_plain_text, split_text_to_chunks, add_spaces_to_text

# Import functions from generate_captions.py
from utils.generate_captions import get_audio_duration, split_text, calculate_sentence_durations, generate_timestamps, generate_srt, generate_lrc

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_logging(log_level: str) -> None:
    logging.getLogger().setLevel(log_level)

def text_to_speech(text: str, output_file: str, tts_tool: str, params: str) -> None:
    try:
        logging.info(f"Using {tts_tool} TTS tool to generate audio for text: {text[:30]}...")
        if tts_tool == 'melo':
            melo_tts(text, output_file, params)
        elif tts_tool == 'google':
            google_tts(text, output_file)
        elif tts_tool == 'edge':
            edge_tts_CLI(text, output_file)
        else:
            raise ValueError(f"Unknown TTS tool: {tts_tool}")
        logging.info(f"Generated audio file: {output_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred while running {tts_tool}: {e.output}")
        logging.error(f"Return code: {e.returncode}")
    except Exception as e:
        logging.error(f"General error occurred: {e}")

def convert_chunks_to_audio(chunks: List[str], output_folder: str, tts_tool: str, combined_output_file: str) -> str:
    combined_audio = AudioSegment.empty()  # Initialize an empty AudioSegment

    # Receive the parameters from the user if using meloTTS
    if tts_tool == 'melo':
      params = TTSParameters()
    else:
      params = None

    for i, chunk in enumerate(chunks):
        temp_output_file = os.path.join(output_folder, f"chunk_{i+1}.mp3")
        logging.info(f"Processing chunk {i+1}: {temp_output_file}")

        text_to_speech(chunk, temp_output_file, tts_tool, params)

        if not os.path.exists(temp_output_file):
            logging.warning(f"Failed to create audio file: {temp_output_file}")
            continue

        try:
            chunk_audio = AudioSegment.from_file(temp_output_file)
            combined_audio += chunk_audio
        except Exception as e:
            logging.error(f"Error loading audio file {temp_output_file}: {e}")

        os.remove(temp_output_file)

    combined_audio.export(combined_output_file, format="mp3")
    return combined_output_file

def split_audio_to_chunks(audio_file: str, chunk_length_ms: int) -> List[AudioSegment]:
    audio = AudioSegment.from_file(audio_file)
    return [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

def detect_encoding(file_path: str) -> str:
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def read_file(file_path: str, encoding: str) -> str:
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()
    except UnicodeDecodeError:
        logging.warning(f"Failed to decode file with encoding {encoding}. Trying 'utf-8' with errors='ignore'.")
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()

def process_pdf(file_path: str) -> List[str]:
    logging.info("Converting PDF to markdown...")
    markdown_text = pdf_to_markdown(file_path, page_numbers=[1])

    logging.info("Converting markdown to plain text...")
    plain_text = markdown_to_plain_text(markdown_text)
    
    logging.info("Splitting text into chunks...")
    return split_text_to_chunks(plain_text)

def process_text(file_path: str, encoding: str) -> List[str]:
    text = read_file(file_path, encoding)
    logging.info("Splitting text into chunks...")
    return split_text_to_chunks(text)

def main() -> None:
    parser = argparse.ArgumentParser(description='Text to Speech Converter')
    parser.add_argument('text_path', type=str, help='Path to the text file to convert')
    parser.add_argument('output_folder', type=str, help='Folder to save the output audio files')
    parser.add_argument('--tts_tool', type=str, choices=['melo', 'google', 'edge'], default='google', help='TTS tool to use')
    parser.add_argument('--chunk_length', type=int, default=60, help='Chunk length in seconds')
    parser.add_argument('--log_level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Logging level')
    parser.add_argument('--generate_captions', action='store_true', help='Generate captions for the audio')

    args = parser.parse_args()

    setup_logging(args.log_level)

    os.makedirs(args.output_folder, exist_ok=True)

    encoding = detect_encoding(args.text_path)
    logging.info(f"Detected encoding: {encoding}")

    if args.text_path.lower().endswith('.pdf'):
        chunks = process_pdf(args.text_path)
    elif args.text_path.lower().endswith('.txt'):
        chunks = process_text(args.text_path, encoding)
    else:
        logging.error("Unsupported file type. Please provide a PDF or TXT file.")
        return
    
    logging.info("Adding spaces to each chunk...")
    chunks = [add_spaces_to_text(chunk) for chunk in chunks]

    combined_output_file = os.path.join(args.output_folder, "combined_audio.mp3")
    
    logging.info("Converting text chunks to a single audio file...")
    combined_audio_file = convert_chunks_to_audio(chunks, args.output_folder, args.tts_tool, combined_output_file)

    if args.generate_captions:
        logging.info("Generating captions...")
        text = read_file(args.text_path, encoding)
        audio_duration = get_audio_duration(combined_audio_file)
        sentences = split_text(text)
        sentence_durations = calculate_sentence_durations(sentences, audio_duration)
        timestamps = generate_timestamps(sentences, sentence_durations)
        generate_srt(timestamps)
        generate_lrc(timestamps)
        logging.info("Captions generated and saved as output.srt and output.lrc")

    logging.info(f"Playing combined audio file {combined_audio_file}")
    display(Audio(combined_audio_file, autoplay=True))

if __name__ == "__main__":
    main()
