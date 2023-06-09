# -*- coding: utf-8 -*-
import argparse
import os.path
import string
import sys
import subprocess
import random

import sounddevice as sd
import soundfile as sf
from typing import Dict
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play


def start(data: Dict):
    try:
        abs_path: str = os.path.dirname(os.path.abspath(__file__))
        father_path: str = f"{os.path.dirname(abs_path)}/audio_files" if data['output_path'] == "" else data[
            'output_path']
        input_text: str = ""

        if not os.path.exists(father_path):
            os.makedirs(father_path)

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

        temp_name: str = random_str(20)
        tts = gTTS(text=input_text, lang=data['lang'], tld=data['tld'], slow=data['slow'])
        tts.save(f"{father_path}/{temp_name}.mp3")

        file_path: str = f"{father_path}/{data['output']}.{data['format']}"
        temp_file_path: str = f"{father_path}/{temp_name}.mp3"

        command: list = ["ffmpeg",
                         "-i",
                         temp_file_path,
                         "-codec:a",
                         data['codec'],
                         "-b:a",
                         f"{data['bit_rate']}k",
                         "-ar",
                         "8000",
                         f"{file_path}",
                         "-y"
                         ]
        ex = subprocess.run(command)

        if ex.returncode != 0:
            raise Exception("Error converting audio file")

        os.remove(temp_file_path)

        if data['play']:
            audio = AudioSegment.from_file(file_path, format=data['format'],
                                           frame_rate=data['sample_rate'],
                                           channels=data['channels'])
            play(audio)
    except Exception as ex:
        raise ex


def random_str(length: int) -> str:
    c: str = string.ascii_letters + string.digits
    r: str = ''.join(random.choice(c) for i in range(length))
    return r


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
        parser.add_argument("-i", "--input-file", type=str, default=None, help="Custom input file")
        parser.add_argument("-l", "--lang", type=str, default="en", help="Language to be used")
        parser.add_argument("--tld", type=str, default="us", help="Top level domain")
        parser.add_argument("--slow", type=bool, default=False, help="Slow down the audio")
        parser.add_argument("--output", type=str, default="output", help="Output file")
        parser.add_argument("--output-path", type=str, default="", help="Output folder")
        parser.add_argument("-p", "--play", type=bool, default=False)
        parser.add_argument("-f", "--format", type=str, default="mp3")
        parser.add_argument("-s", "--sample-rate", type=int, default=44_100)
        parser.add_argument("-b", "--bit-rate", type=int, default=32)
        parser.add_argument("--codec", type=str, default="libmp3lame")
        parser.add_argument("-c", "--channels", type=int, default=2)
        parser.add_argument("-r", "--record", type=bool, default=False)
        parser.add_argument("--record-sample_rate", type=int, default=44_100)
        parser.add_argument("--record-seconds", type=int, default=10)

        params: Dict = vars(parser.parse_args())
        start(params)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as ex:
        sys.exit(1)
