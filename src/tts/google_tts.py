# Code for Google TTS
from gtts import gTTS
import pdfplumber
from pydub import AudioSegment

def google_tts(text, audio_path, lang='en', tld='us'):
    # Convert text to audio using gTTS
    tts = gTTS(text=text, lang=lang, tld=tld)
    tts.save("temp.mp3")

    # Optionally convert to WAV format
    audio = AudioSegment.from_mp3("temp.mp3")
    audio.export(audio_path, format="wav")