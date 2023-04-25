#!/usr/src/env python
# -*- coding: utf-8 -*-
from pydub import AudioSegment
from pydub.playback import play

from bark import SAMPLE_RATE, generate_audio, preload_models
# from IPython.display import Audio
import sounddevice as sd
import soundfile as sf


# download and load all modelspe
preload_models()

# generate audio from text
# text_prompt = """
#      Hello, my name is Suno. And, uh — and I like pizza. [laughs]
#      But I also have other interests such as playing tic tac toe.
# """
text_prompt = """
     Hola soy un modelo entrenado [laughs], tenga muy buen dia
"""
audio_array = generate_audio(text_prompt)

# play text in notebook
# Audio(audio_array, autoplay=True, rate=SAMPLE_RATE)

# audio = AudioSegment.from_file(audio_array, format="wav")
# audio.export("audio.wav", format="wav")
# play(audio)
sd.play(audio_array, SAMPLE_RATE)
sd.wait()

sf.write('audio.wav', audio_array, SAMPLE_RATE)
