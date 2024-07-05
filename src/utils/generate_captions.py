import logging
from pydub import AudioSegment
import time
import re

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_audio_duration(filename):
    """
    Get the duration of an audio file in seconds.
    
    Parameters:
    filename (str): Path to the audio file.
    
    Returns:
    float: Duration of the audio file in seconds.
    """
    logging.info(f"Getting duration for {filename}")
    audio = AudioSegment.from_file(filename)
    duration = len(audio) / 1000.0  # pydub calculates duration in milliseconds
    logging.info(f"Duration of the audio is {duration} seconds")
    return duration

def split_text(text, max_words_per_caption=10):
    """
    Split text into sentences and ensure each caption is not too long.
    
    Parameters:
    text (str): The transcription text.
    max_words_per_caption (int): Maximum number of words per caption.
    
    Returns:
    list: List of sentences suitable for captioning.
    """
    logging.info("Splitting text into sentences.")
    # Split text by punctuation and newlines
    raw_sentences = re.split(r'[.?!\n]', text)
    sentences = []
    for sentence in raw_sentences:
        words = sentence.strip().split()
        for i in range(0, len(words), max_words_per_caption):
            sentences.append(' '.join(words[i:i + max_words_per_caption]))
    logging.info(f"Text split into {len(sentences)} sentences for captioning.")
    return sentences

def calculate_sentence_durations(sentences, total_duration):
    """
    Calculate the duration for each sentence based on the total audio duration.
    
    Parameters:
    sentences (list): List of sentences.
    total_duration (float): The total duration of the audio file in seconds.
    
    Returns:
    list: List of durations for each sentence.
    """
    logging.info("Calculating sentence durations.")
    total_characters = sum(len(sentence) for sentence in sentences)
    sentence_durations = [(len(sentence) / total_characters) * total_duration for sentence in sentences]
    logging.info("Sentence durations calculated.")
    return sentence_durations

def generate_timestamps(sentences, durations):
    """
    Generate timestamps for each sentence.
    
    Parameters:
    sentences (list): List of sentences.
    durations (list): List of durations for each sentence.
    
    Returns:
    list: List of tuples containing sentence, start time, and end time.
    """
    logging.info("Generating timestamps for each sentence.")
    timestamps = []
    current_time = 0.0
    for sentence, duration in zip(sentences, durations):
        timestamps.append((sentence, current_time, current_time + duration))
        current_time += duration
    logging.info("Timestamps generated.")
    return timestamps

def generate_srt(timestamps):
    """
    Generate SRT file content from timestamps.
    
    Parameters:
    timestamps (list): List of tuples containing sentence, start time, and end time.
    """
    logging.info("Generating SRT file.")
    srt_content = ""
    for i, (sentence, start, end) in enumerate(timestamps):
        start_time = time.strftime('%H:%M:%S', time.gmtime(start)) + f',{int((start % 1) * 1000):03d}'
        end_time = time.strftime('%H:%M:%S', time.gmtime(end)) + f',{int((end % 1) * 1000):03d}'
        srt_content += f"{i+1}\n{start_time} --> {end_time}\n{sentence.strip()}\n\n"
    with open('output.srt', 'w') as f:
        f.write(srt_content)
    logging.info("SRT file generated.")

def generate_lrc(timestamps):
    """
    Generate LRC file content from timestamps.
    
    Parameters:
    timestamps (list): List of tuples containing sentence, start time, and end time.
    """
    logging.info("Generating LRC file.")
    lrc_content = ""
    for sentence, start, _ in timestamps:
        start_time = time.strftime('[%M:%S', time.gmtime(start)) + f'.{int((start % 1) * 100):02d}]'
        lrc_content += f"{start_time} {sentence.strip()}\n"
    with open('output.lrc', 'w') as f:
        f.write(lrc_content)
    logging.info("LRC file generated.")

# # Example usage:
# text = "Your book summary text goes here."
# audio_filename = 'output.wav'  # or 'output.mp3'
# audio_duration = get_audio_duration(audio_filename)
# sentences = split_text(text)
# sentence_durations = calculate_sentence_durations(sentences, audio_duration)
# timestamps = generate_timestamps(sentences, sentence_durations)
# generate_srt(timestamps)
# generate_lrc(timestamps)
