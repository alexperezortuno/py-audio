#!/usr/src/env python
# -*- coding: utf-8 -*-
import argparse
import os.path
import re
import sys
from typing import Dict
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play


def start(data: Dict):
    abs_path: str = os.path.dirname(os.path.abspath(__file__))
    father_path: str = os.path.dirname(abs_path)
    tts = gTTS(text=data['text'], lang=data['lang'], slow=data['slow'])
    tts.save(f"{father_path}/{data['output']}")
    file_path: str = f"{father_path}/{data['output']}"
    _, format_ext = os.path.splitext(file_path)
    print(file_path)
    print(re.sub("[.]", "", format_ext))

    if data['play']:
        audio = AudioSegment.from_file(file_path, format=re.sub("[.]", "", format_ext))
        play(audio)


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="ZeroMQ workers",
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser = parser.add_subparsers(title='Script select', dest='script_type')
        parser.version = '0.0.0'
        parser.add_argument("-v", "--version", action="version")
        parser.add_argument("-t", "--text", type=str,
                            default="Hello my name is Bark. I am a trained model. I hope you have a great day.",
                            help="Text to be turned into audio")
        parser.add_argument("-l", "--lang", type=str, default="en", help="Language to be used")
        parser.add_argument("--slow", type=bool, default=False, help="Slow down the audio")
        parser.add_argument("--output", type=str, default="output.mp3", help="Output file")
        parser.add_argument("-p", "--play", type=bool, default=False)
        parser.add_argument("-s", "--sample_rate", type=int, default=24_000)

        params: Dict = vars(parser.parse_args())
        start(params)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as ex:
        sys.exit(1)
