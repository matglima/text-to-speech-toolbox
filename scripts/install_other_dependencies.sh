#!/bin/bash

git clone https://github.com/myshell-ai/MeloTTS.git
cd MeloTTS
pip install -e .
python -m unidic download
python -m spacy download en_core_web_sm # This install a dependency for spacy
