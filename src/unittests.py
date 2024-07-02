import unittest
from unittest.mock import patch, mock_open, call
import os
from pydub import AudioSegment

class TestTTSConverter(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='This is a test text.')
    @patch('os.path.exists', return_value=True)
    @patch('pydub.AudioSegment.from_file')
    def test_text_to_speech(self, mock_audio_segment, mock_exists, mock_file):
        from main import text_to_speech, convert_chunks_to_audio

        mock_audio_segment.return_value = AudioSegment.silent(duration=1000)
        chunks = ["This is a test text."]
        output_folder = "test_output"
        tts_tool = "google"
        combined_output_file = "test_output/combined_audio.mp3"
        
        os.makedirs(output_folder, exist_ok=True)
        combined_audio_file = convert_chunks_to_audio(chunks, output_folder, tts_tool, combined_output_file)

        self.assertTrue(os.path.exists(combined_audio_file))

    @patch('chardet.detect', return_value={'encoding': 'utf-8'})
    @patch('builtins.open', new_callable=mock_open, read_data='This is a test text.')
    def test_detect_encoding(self, mock_file, mock_chardet):
        from main import detect_encoding

        encoding = detect_encoding("test.txt")
        self.assertEqual(encoding, 'utf-8')

    @patch('pydub.AudioSegment.from_file')
    def test_split_audio_to_chunks(self, mock_audio_segment):
        from main import split_audio_to_chunks

        mock_audio_segment.return_value = AudioSegment.silent(duration=10000)
        chunks = split_audio_to_chunks("test.mp3", 5000)

        self.assertEqual(len(chunks), 2)

if __name__ == '__main__':
    unittest.main()
