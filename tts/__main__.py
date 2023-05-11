#!/usr/src/env python
# -*- coding: utf-8 -*-
import argparse
import os.path
import re
import sys
import sounddevice as sd
import soundfile as sf
from typing import Dict
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play


def start(data: Dict):
    try:
        abs_path: str = os.path.dirname(os.path.abspath(__file__))
        father_path: str = os.path.dirname(abs_path)
        input_text: str = ""

        if data['record']:
            my_recording = sd.rec(
                int(data['record_seconds'] * data['record_sample_rate']),
                samplerate=data['record_sample_rate'],
                channels=data['channels'],
            )
            sd.wait()
            file_path: str = f"{father_path}/{data['output']}"
            sf.write(file_path, my_recording, data['record_sample_rate'])

        if data['text'] is None and data['input_file'] is None:
            input_text = input("Enter text: ")

        if data['text'] is not None:
            input_text = data['text']

        if data['input_file'] is not None:
            with open(f"{father_path}/{data['input_file']}", "r") as f:
                input_text = f.read()

        tts = gTTS(text=input_text, lang=data['lang'], tld=data['tld'], slow=data['slow'])
        tts.save(f"{father_path}/{data['output']}")

        file_path: str = f"{father_path}/{data['output']}"
        _, format_ext = os.path.splitext(file_path)

        if data['format'] != format_ext:
            file_name = os.path.splitext(os.path.basename(data['output']))[0]
            audio = AudioSegment.from_file(file_path, format=re.sub("[.]", "", format_ext))
            audio.export(f"{father_path}/{file_name}.{data['format']}", format=data['format'])
            format_ext = f".{data['format']}"

        if data['play']:
            audio = AudioSegment.from_file(file_path, format=re.sub("[.]", "", format_ext))
            play(audio)
    except Exception as ex:
        raise ex


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Text to speech",
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser = parser.add_subparsers(title='Script select', dest='script_type')
        parser.version = '0.0.0'
        parser.add_argument("-v", "--version", action="version")
        parser.add_argument("-t", "--text", type=str,
                            default=None,
                            help="Text to be turned into audio")
        parser.add_argument("-i", "--input_file", type=str, default=None, help="Custom input file")
        parser.add_argument("-l", "--lang", type=str, default="en", help="Language to be used")
        parser.add_argument("--tld", type=str, default="us", help="Top level domain")
        parser.add_argument("--slow", type=bool, default=False, help="Slow down the audio")
        parser.add_argument("--output", type=str, default="output.mp3", help="Output file")
        parser.add_argument("-p", "--play", type=bool, default=False)
        parser.add_argument("-f", "--format", type=str, default="mp3")
        parser.add_argument("-s", "--sample_rate", type=int, default=44_100)
        parser.add_argument("-c", "--channels", type=int, default=2)
        parser.add_argument("-r", "--record", type=bool, default=False)
        parser.add_argument("--record_sample_rate", type=int, default=44_100)
        parser.add_argument("--record_seconds", type=int, default=10)

        params: Dict = vars(parser.parse_args())
        start(params)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as ex:
        sys.exit(1)
