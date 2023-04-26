#!/usr/src/env python
# -*- coding: utf-8 -*-
import argparse
import re
from typing import Dict

from bark import SAMPLE_RATE, generate_audio, preload_models
import sounddevice as sd
import soundfile as sf


def start(data: Dict) -> None:
    # download and load all models
    preload_models(
        text_use_gpu=data['text_use_gpu'],
        text_use_small=data['text_use_small'],
        coarse_use_gpu=data['coarse_use_gpu'],
        coarse_use_small=data['coarse_use_small'],
        fine_use_gpu=data['fine_use_gpu'],
        fine_use_small=data['fine_use_small'],
        codec_use_gpu=data['codec_use_gpu'],
    )

    # generate audio from text
    # text_prompt = "Hola soy un modelo entrenado. ¡Que tenga muy buen dia!."
    text_prompt = [
        """
         Hello, my name is Suno. And, uh — and I like pizza. [laughs]
         But I also have other interests such as playing tic tac toe.
        """,
        "WOMAN: Hola soy un modelo entrenado. ¡Que tengas muy buen dia!.",
        "En que te puedo ayudar.",
        "¿Tienes algun problema?.",
        "¿Te puedo ayudar en algo más?",
    ]

    try:
        for text in text_prompt:
            audio_array = generate_audio(text,
                                         history_prompt=data['speaker'],
                                         text_temp=data['temp'],
                                         waveform_temp=data['waveform_temp'],
                                         silent=data['silent'],
                                         )

            if data['play_audio']:
                sd.play(audio_array, data['sample_rate'])
                sd.wait()

            sf.write(
                f'{re.sub("[?¿!¡,.]", "", text.replace("WOMAN: ", "").replace("MAN: ", "")[:24]).replace(" ", "_").lower()}.wav',
                audio_array, data['sample_rate'])
            del audio_array
    except Exception as ex:
        raise ex


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ZeroMQ workers",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparser = parser.add_subparsers(title='Script select', dest='script_type')
    parser.version = '0.0.0'
    parser.add_argument("-v", "--version", action="version")
    parser.add_argument("--text_use_gpu", type=bool, default=False)
    parser.add_argument("--text_use_small", type=bool, default=True)
    parser.add_argument("--coarse_use_gpu", type=bool, default=False)
    parser.add_argument("--coarse_use_small", type=bool, default=True)
    parser.add_argument("--fine_use_gpu", type=bool, default=False)
    parser.add_argument("--fine_use_small", type=bool, default=True)
    parser.add_argument("--codec_use_gpu", type=bool, default=False)
    parser.add_argument("-p", "--play_audio", type=bool, default=False)
    parser.add_argument("-s", "--sample_rate", type=int, default=SAMPLE_RATE)
    parser.add_argument("--speaker", type=str, default="es_speaker_0")
    parser.add_argument("-t", "--temp", type=float, default=0.7)
    parser.add_argument("--waveform_temp", type=float, default=0.7)
    parser.add_argument("--silent", type=bool, default=False)
    params: Dict = vars(parser.parse_args())
    try:
        start(params)
    except KeyboardInterrupt:
        print('\nInterrupted by user')
        exit(0)
    except Exception as e:
        print(e)
        exit(1)
