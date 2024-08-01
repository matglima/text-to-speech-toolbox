import argparse
import os
import logging
from typing import List, Callable, Dict
import chardet
import subprocess

# Third-party imports
from pydub import AudioSegment
from IPython.display import Audio, display

# Local imports
from utils.pdf_extractor import pdf_to_markdown, markdown_to_plain_text, split_text_to_chunks, add_spaces_to_text
from utils.generate_captions import get_audio_duration, split_text, calculate_sentence_durations, generate_timestamps, generate_srt, generate_lrc

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_logging(log_level: str) -> None:
    """Set up logging with the specified log level."""
    logging.getLogger().setLevel(log_level)
    
def edge_tts_wrapper(text: str, output_file: str) -> None:
    from tts.edge_tts import edge_tts_CLI
    edge_tts_CLI(text, output_file)

def google_tts_wrapper(text: str, output_file: str) -> None:
    from tts.google_tts import google_tts
    google_tts(text, output_file)

def create_model_wrapper(model_name: str) -> Callable:
    def wrapper(text: str, output_file: str, use_default_params: bool) -> None:
        if model_name == 'melo':
            from tts.mello_tts import melo_tts as model_class
        elif model_name == 'coqui':
            from tts.coqui_xtts import coqui_tts as model_class
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        model = model_class()
        if not use_default_params:
            model.prompt_user_for_parameters()
        model.convert_to_audio(text, output_file)
    return wrapper

# Dictionary mapping TTS tool names to their respective functions
TTS_TOOLS: Dict[str, Callable] = {
    'edge': edge_tts_wrapper,
    'google': google_tts_wrapper,
    'melo': create_model_wrapper('melo'),
    'coqui': create_model_wrapper('coqui')
}

def text_to_speech(text: str, output_file: str, tts_tool: str, use_default_params: bool = True) -> None:
    """
    Convert text to speech using the specified TTS tool.
    
    Args:
        text: The input text to convert to speech.
        output_file: The path to save the output audio file.
        tts_tool: The name of the TTS tool to use.
        use_default_params: Whether to use default parameters for the TTS tool.
    """
    try:
        logging.info(f"Using {tts_tool} TTS tool to generate audio for text: {text[:30]}...")
        
        if tts_tool not in TTS_TOOLS:
            raise ValueError(f"Unknown TTS tool: {tts_tool}")
        
        tts_function = TTS_TOOLS[tts_tool]
        
        if tts_tool in ['melo', 'coqui']:
            tts_function(text, output_file, use_default_params)
        else:
            tts_function(text, output_file)
            
        logging.info(f"Generated audio file: {output_file}")
    except ImportError as e:
        logging.error(f"Failed to import necessary module for {tts_tool}: {e}")
        logging.error(f"Make sure you have installed the correct dependencies for {tts_tool}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred while running {tts_tool}: {e.output}")
        logging.error(f"Return code: {e.returncode}")
    except Exception as e:
        logging.error(f"General error occurred: {e}")


def convert_chunks_to_audio(chunks: List[str], output_folder: str, tts_tool: str, combined_output_file: str, use_default_params: bool = True) -> str:
    """
    Convert text chunks to audio and combine them into a single file.
    
    Args:
        chunks: List of text chunks to convert.
        output_folder: Folder to save temporary audio files.
        tts_tool: The TTS tool to use for conversion.
        combined_output_file: Path for the final combined audio file.
        use_default_params: Whether to use default parameters for the TTS tool.
    
    Returns:
        Path to the combined audio file.
    """
    combined_audio = AudioSegment.empty()

    for i, chunk in enumerate(chunks):
        temp_output_file = os.path.join(output_folder, f"chunk_{i+1}.mp3")
        logging.info(f"Processing chunk {i+1}: {temp_output_file}")

        text_to_speech(chunk, temp_output_file, tts_tool, use_default_params)

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
    """
    Split an audio file into chunks of specified length.
    
    Args:
        audio_file: Path to the audio file to split.
        chunk_length_ms: Length of each chunk in milliseconds.
    
    Returns:
        List of AudioSegment objects representing the chunks.
    """
    audio = AudioSegment.from_file(audio_file)
    return [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

def detect_encoding(file_path: str) -> str:
    """
    Detect the encoding of a file.
    
    Args:
        file_path: Path to the file to detect encoding for.
    
    Returns:
        Detected encoding of the file.
    """
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def read_file(file_path: str, encoding: str) -> str:
    """
    Read a file with the specified encoding.
    
    Args:
        file_path: Path to the file to read.
        encoding: Encoding to use when reading the file.
    
    Returns:
        Contents of the file as a string.
    """
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()
    except UnicodeDecodeError:
        logging.warning(f"Failed to decode file with encoding {encoding}. Trying 'utf-8' with errors='ignore'.")
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()

def process_pdf(file_path: str, split_into_chunks: bool = True, max_chunk_size: int = 4096) -> List[str]:
    """
    Process a PDF file, converting it to text and optionally splitting into chunks.
    
    Args:
        file_path: Path to the PDF file.
        split_into_chunks: Whether to split the text into chunks.
    
    Returns:
        List of text chunks or a single text string.
    """
    logging.info("Converting PDF to markdown...")
    markdown_text = pdf_to_markdown(file_path, page_numbers=[1])

    logging.info("Converting markdown to plain text...")
    text = markdown_to_plain_text(markdown_text)
    
    logging.info("Splitting text into chunks...")
    if split_into_chunks:
        return split_text_to_chunks(text, max_chunk_size)
    else: 
        return [text]  # Return as a single-item list for consistency

def process_text(file_path: str, encoding: str, split_into_chunks: bool = True, max_chunk_size: int = 4096) -> List[str]:
    """
    Process a text file, reading its contents and optionally splitting into chunks.
    
    Args:
        file_path: Path to the text file.
        encoding: Encoding of the text file.
        split_into_chunks: Whether to split the text into chunks.
    
    Returns:
        List of text chunks or a single text string.
    """
    text = read_file(file_path, encoding)
    logging.info("Splitting text into chunks...")
    if split_into_chunks:
        return split_text_to_chunks(text, max_chunk_size)
    else: 
        return [text]  # Return as a single-item list for consistency

def main() -> None:
    """Main function to run the text-to-speech conversion process."""
    parser = argparse.ArgumentParser(description='Text to Speech Converter')
    parser.add_argument('text_path', type=str, help='Path to the text file to convert')
    parser.add_argument('output_folder', type=str, help='Folder to save the output audio files')
    parser.add_argument('output_audio_name', type=str, help='Output audio name')
    parser.add_argument('--tts_tool', type=str, choices=['melo', 'google', 'edge', 'coqui'], default='google', help='TTS tool to use')
    parser.add_argument('--chunk_length', type=int, default=200, help='Chunk length')
    parser.add_argument('--log_level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Logging level')
    parser.add_argument('--generate_captions', action='store_true', help='Generate captions for the audio')
    parser.add_argument('--use_default_params', action='store_true', help='Use default parameters for TTS')
    
    args = parser.parse_args()

    setup_logging(args.log_level)

    os.makedirs(args.output_folder, exist_ok=True)

    encoding = detect_encoding(args.text_path)
    logging.info(f"Detected encoding: {encoding}")

    # Determine whether to split into chunks based on the TTS tool
    split_into_chunks = True#args.tts_tool != 'coqui'
    
    if args.text_path.lower().endswith('.pdf'):
        chunks = process_pdf(args.text_path, split_into_chunks, max_chunk_size = args.chunk_length)
    elif args.text_path.lower().endswith('.txt'):
        chunks = process_text(args.text_path, encoding, split_into_chunks, max_chunk_size = args.chunk_length)
    else:
        logging.error("Unsupported file type. Please provide a PDF or TXT file.")
        return


    if args.tts_tool not in ['coqui']:
        logging.info("Adding spaces to each chunk...")
        chunks = [add_spaces_to_text(chunk) for chunk in chunks]

    combined_output_file = os.path.join(args.output_folder, f"{args.output_audio_name.split('.')[0]}.mp3")
    
    logging.info("Converting text chunks to a single audio file...")
    combined_audio_file = convert_chunks_to_audio(chunks, args.output_folder, args.tts_tool, combined_output_file, args.use_default_params)

    if args.generate_captions:
        logging.info("Generating captions...")
        text = markdown_to_plain_text(' '.join(chunks))
        audio_duration = get_audio_duration(combined_audio_file)
        sentences = split_text(text)
        sentence_durations = calculate_sentence_durations(sentences, audio_duration)
        timestamps = generate_timestamps(sentences, sentence_durations)
        generate_srt(timestamps, args.output_folder, args.output_audio_name.split('.')[0])
        generate_lrc(timestamps, args.output_folder, args.output_audio_name.split('.')[0])
        logging.info(f"Captions generated and saved")

    logging.info(f"Playing combined audio file {combined_audio_file}")
    display(Audio(combined_audio_file, autoplay=True))

if __name__ == "__main__":
    main()
