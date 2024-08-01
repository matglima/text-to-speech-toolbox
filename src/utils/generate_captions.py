import logging
import time
import re
import os
import nltk
nltk.download('punkt', quiet=True)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def split_text(text):
    """
    Split text into sentences using NLTK's sentence tokenizer.
    """
    logging.info("Splitting text into sentences.")
    sentences = nltk.sent_tokenize(text)
    logging.info(f"Text split into {len(sentences)} sentences for captioning.")
    return sentences

def calculate_sentence_durations(sentences, total_duration):
    """
    Calculate the duration for each sentence based on the total audio duration.
    This method uses word count instead of character count for better estimation.
    """
    logging.info("Calculating sentence durations.")
    total_words = sum(len(sentence.split()) for sentence in sentences)
    sentence_durations = [(len(sentence.split()) / total_words) * total_duration for sentence in sentences]
    logging.info("Sentence durations calculated.")
    return sentence_durations

def generate_timestamps(sentences, durations, initial_delay=0.5):
    """
    Generate timestamps for each sentence with an initial delay.
    """
    logging.info("Generating timestamps for each sentence.")
    timestamps = []
    current_time = initial_delay
    for sentence, duration in zip(sentences, durations):
        timestamps.append((sentence, current_time, current_time + duration))
        current_time += duration
    logging.info("Timestamps generated.")
    return timestamps

def generate_srt(timestamps, output_folder, caption_name):
    """
    Generate SRT file content from timestamps.
    """
    logging.info("Generating SRT file.")
    srt_content = ""
    for i, (sentence, start, end) in enumerate(timestamps):
        start_time = time.strftime('%H:%M:%S', time.gmtime(start)) + f',{int((start % 1) * 1000):03d}'
        end_time = time.strftime('%H:%M:%S', time.gmtime(end)) + f',{int((end % 1) * 1000):03d}'
        srt_content += f"{i+1}\n{start_time} --> {end_time}\n{sentence.strip()}\n\n"
    with open(os.path.join(output_folder, caption_name + '.srt'), 'w') as f:
        f.write(srt_content)
    logging.info("SRT file generated.")

def generate_lrc(timestamps, output_folder, caption_name):
    """
    Generate LRC file content from timestamps.
    """
    logging.info("Generating LRC file.")
    lrc_content = ""
    for sentence, start, _ in timestamps:
        start_time = time.strftime('[%M:%S', time.gmtime(start)) + f'.{int((start % 1) * 100):02d}]'
        lrc_content += f"{start_time} {sentence.strip()}\n"
    with open(os.path.join(output_folder, caption_name + '.lrc'), 'w') as f:
        f.write(lrc_content)
    logging.info("LRC file generated.")

def generate_captions(text, audio_duration, output_folder, caption_name):
    """
    Generate captions for the given text and audio duration.
    """
    sentences = split_text(text)
    sentence_durations = calculate_sentence_durations(sentences, audio_duration)
    timestamps = generate_timestamps(sentences, sentence_durations)
    generate_srt(timestamps, output_folder, caption_name)
    generate_lrc(timestamps, output_folder, caption_name)
from pydub import AudioSegment    
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
# # Example usage:
# with open('/content/central-places.txt','r') as file:
#   text = file.read()
# # text = "Your book summary text goes here."
# audio_filename = 'output.wav'  # or 'output.mp3'
# audio_duration = get_audio_duration(audio_filename)
# sentences = split_text(text)
# sentence_durations = calculate_sentence_durations(sentences, audio_duration)
# timestamps = generate_timestamps(sentences, sentence_durations)
# generate_srt(timestamps)
# generate_lrc(timestamps)
