import logging
import os
from aeneas.executetask import ExecuteTask
from aeneas.task import Task
from aeneas.textfile import TextFile
from aeneas.language import Language

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_captions(text, audio_file, output_folder, caption_name):
    """
    Generate captions for the given text and audio file using aeneas.
    """
    logging.info("Starting caption generation with aeneas.")

    # Create a temporary text file
    text_file = os.path.join(output_folder, "temp_text.txt")
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(text)

    # Configure the aeneas Task
    config_string = u"task_language=eng|is_text_type=plain|os_task_file_format=srt"
    task = Task(config_string=config_string)
    task.audio_file_path_absolute = audio_file
    task.text_file_path_absolute = text_file
    task.sync_map_file_path_absolute = os.path.join(output_folder, f"{caption_name}.srt")

    # Execute the task
    ExecuteTask(task).execute()

    # Remove the temporary text file
    os.remove(text_file)

    logging.info("SRT file generated with aeneas.")

    # Convert SRT to LRC
    srt_to_lrc(task.sync_map_file_path_absolute, os.path.join(output_folder, f"{caption_name}.lrc"))

def srt_to_lrc(srt_file, lrc_file):
    """
    Convert SRT file to LRC format.
    """
    logging.info("Converting SRT to LRC.")
    
    with open(srt_file, 'r') as srt, open(lrc_file, 'w') as lrc:
        for line in srt:
            if '-->' in line:
                start_time = line.split('-->')[0].strip()
                h, m, s = start_time.split(':')
                s, ms = s.split(',')
                lrc_time = f"[{m}:{s}.{ms[:2]}]"
            elif line.strip() and not line[0].isdigit():
                lrc.write(f"{lrc_time} {line}")

    logging.info("LRC file generated.")

# Example usage:
if __name__ == "__main__":
    text = "Your book summary text goes here. This is a second sentence. And a third one."
    audio_file = 'path/to/your/audio/file.mp3'  # Replace with your audio file path
    output_folder = 'path/to/output/folder'  # Replace with your desired output folder
    caption_name = 'my_captions'

    generate_captions(text, audio_file, output_folder, caption_name)
