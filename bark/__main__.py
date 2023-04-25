#!/usr/src/env python
# -*- coding: utf-8 -*-
import re
from bark import SAMPLE_RATE, generate_audio, preload_models
import soundfile as sf


# download and load all models
preload_models()
# preload_models(
#     text_use_gpu=False,
#     text_use_small=True,
#     coarse_use_gpu=False,
#     coarse_use_small=True,
#     fine_use_gpu=False,
#     fine_use_small=True,
#     codec_use_gpu=False,
# )

# generate audio from text
# text_prompt = """
#      Hello, my name is Suno. And, uh — and I like pizza. [laughs]
#      But I also have other interests such as playing tic tac toe.
# """
# text_prompt = "Hola soy un modelo entrenado. ¡Que tenga muy buen dia!."
text_prompt = [
    "Hola soy un modelo entrenado. ¡Que tenga muy buen dia!.",
    "En que te puedo ayudar.",
    "¿Tienes algun problema?",
    "¿Te puedo ayudar en algo más?",
]

# audio_array = generate_audio(text_prompt)

try:
    for text in text_prompt:
        audio_array = generate_audio(text, history_prompt="es_speaker_1")

        # sd.play(audio_array, SAMPLE_RATE)
        # sd.wait()

        sf.write(f'{re.sub("[?¿!¡,.]", "", text).replace(" ", "_").lower()}.wav', audio_array, SAMPLE_RATE)
        audio_array = None
except KeyboardInterrupt:
    print('\nInterrupted by user')
    exit(0)
except Exception as e:
    print(e)
    exit(1)
