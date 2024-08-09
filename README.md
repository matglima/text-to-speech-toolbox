**Text to Speech Toolbox**
==========================

A collection of tools and scripts for text-to-speech (TTS) conversion, including support for various TTS engines and utility scripts for audio and video processing.

**Installation**
---------------

To install the required dependencies for simple and fast TTS with Melo, gtts and edgetts, run:
```bash
python text-to-speech-toolbox/setup.py install
python text-to-speech-toolbox/setup.py clean --all
```
To install dependencies for Coqui TTS, run:
```bash
pip install -r requirements_coqui.txt
```
**Usage**
-----

The main entry point for the TTS toolbox is `main.py`. To use the TTS toolbox, simply run:
```bash
python main.py
```
This will provide a list of available options and usage instructions.

**TTS Engines**
----------------

The TTS toolbox currently supports the following TTS engines:

* Coqui TTS (`tts/coqui_xtts.py`)
* Edge TTS (`tts/edge_tts.py`)
* Google TTS (`tts/google_tts.py`)
* Mello TTS (`tts/mello_tts.py`)

**Utility Scripts**
-----------------

The TTS toolbox also includes several utility scripts for audio and video processing:

* `audio2video.py`: converts audio files to video files
* `generate_captions.py`: generates captions for audio and video files
* `generate_captions_aeneas.py`: generates captions for audio and video files using the Aeneas library
* `pdf_extractor.py`: extracts text from PDF files
* `youtube_transcript.py`: extracts transcripts from YouTube videos

**Examples**
------------

Example audio files are provided in the `src/examples` directory.

**Testing**
---------

To run unit tests, execute:
```bash
python unittests.py
```
**License**
---------

This project is licensed under the terms of the [LICENSE](LICENSE) file.

**Contributing**
------------

Contributions are welcome! Please submit a pull request or issue report to contribute to the project.
