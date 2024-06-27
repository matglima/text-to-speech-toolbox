import pdfplumber
import spacy
import re # Importing the 're' module for regular expression operations
import os
from pydub import AudioSegment
from moviepy.editor import concatenate_audioclips, AudioFileClip

''' 
Using spacy to correctly separate words when reading the content of PDFs
'''

# Load the spaCy language model
nlp = spacy.load('en_core_web_sm')

def add_spaces_to_text(text):
    # Use spaCy to tokenize and reconstruct the text with spaces
    doc = nlp(text)
    return ' '.join([token.text for token in doc])

def pdf_to_markdown(pdf_path, page_numbers=None):
    with pdfplumber.open(pdf_path) as pdf:
        markdown_content = ""
        if page_numbers is None:
            page_numbers = range(len(pdf.pages))
        for page_num in page_numbers:
            page = pdf.pages[page_num]
            # Extract text from each page
            text = page.extract_text(x_tolerance=1, y_tolerance=3)
            if text:
                # Add spaces where they might be missing using spaCy
                text = add_spaces_to_text(text)
                # Format the text with basic Markdown: double newline for new paragraphs
                markdown_page = text.replace('\n', '\n\n')
                # Add a separator line between pages
                markdown_content += markdown_page + '\n\n---\n\n'
        return markdown_content

'''
Converting Markdown to Plain Text
'''


def markdown_to_plain_text(markdown_text):
    # Remove Markdown URL syntax ([text](link)) and keep only the text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', markdown_text)

    # Remove Markdown formatting for bold and italic text
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold with **
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic with *
    text = re.sub(r'\_\_([^_]+)\_\_', r'\1', text)  # Bold with __
    text = re.sub(r'\_([^_]+)\_', r'\1', text)      # Italic with _

    # Remove Markdown headers, list items, and blockquote symbols
    text = re.sub(r'#+\s?', '', text)  # Headers
    text = re.sub(r'-\s?', '', text)   # List items
    text = re.sub(r'>\s?', '', text)   # Blockquotes

    return text


'''
Final teext cleaning:

# Here, we are removing a specific unwanted word or artifact from the text
# Replace "artifact" with any specific word or symbol you need to remove

cleaned_text = plain_text.replace("artifact", "")
'''

'''
Splitting Text into Manageable Chunks for Text-to-Speech
'''
def split_text_to_chunks(text, max_chunk_size=4096):
    chunks = []  # List to hold the chunks of text
    current_chunk = ""  # String to build the current chunk

    # Split the text into sentences and iterate through them
    for sentence in text.split('.'):
        sentence = sentence.strip()  # Remove leading/trailing whitespaces
        if not sentence:
            continue  # Skip empty sentences

        # Check if adding the sentence would exceed the max chunk size
        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
            current_chunk += sentence + "."  # Add sentence to current chunk
        else:
            chunks.append(current_chunk)  # Add the current chunk to the list
            current_chunk = sentence + "."  # Start a new chunk

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

'''
Usage:
# chunks = split_text(cleaned_text) # use this if you have cleaned the text, else use the next line.
chunks = split_text(plain_text)

# Printing each chunk with its number
for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i}:\n{chunk}\n---\n")
'''

'''
Combining Individual Audio Clips into a Single File
'''

def extract_number(filename):
    """ Extracts the number from the filename """
    numbers = re.findall(r'\d+', filename)
    return int(numbers[0]) if numbers else 0

def combine_audio_with_moviepy(folder_path, output_file):
    audio_clips = []  # List to store the audio clips

    # Retrieve and sort files based on the numeric part of the filename
    sorted_files = sorted(os.listdir(folder_path), key=extract_number)

    # Iterate through each sorted file in the given folder
    for file_name in sorted_files:
        if file_name.endswith('.mp3'):
            # Construct the full path of the audio file
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing file: {file_path}")

            try:
                # Create an AudioFileClip object for each audio file
                clip = AudioFileClip(file_path)
                audio_clips.append(clip)  # Add the clip to the list
            except Exception as e:
                # Print any errors encountered while processing the file
                print(f"Error processing file {file_path}: {e}")

    # Check if there are any audio clips to combine
    if audio_clips:
        # Concatenate all the audio clips into a single clip
        final_clip = concatenate_audioclips(audio_clips)
        # Write the combined clip to the specified output file
        final_clip.write_audiofile(output_file)
        print(f"Combined audio saved to {output_file}")
    else:
        print("No audio clips to combine.")




  