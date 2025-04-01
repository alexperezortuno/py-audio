# -*- coding: utf-8 -*-
import argparse
import sys
import queue

import numpy as np
from enum import Enum
from openai import OpenAI
import scipy.io.wavfile as wav
import sounddevice as sd
from typing import Dict

q = queue.Queue()
client = OpenAI()
samplerate = 16000
channels = 1
duration = 5 # seconds per recording
chunk = 1024


class TranslationPrompts(Enum):
    ES = "Traduce el siguiente texto al español."
    EN = "Translate the following text to English."
    FR = "Traduisez le texte suivant en français."
    DE = "Übersetzen Sie den folgenden Text ins Deutsche."


def callback(indata, frames, time, status):
    q.put(indata.copy())

def transcribe_audio(params: Dict, file_path: str) -> None:
    """Transcribe audio using OpenAI's Whisper model."""
    try:
        language_code = str(params["language"]).upper()
        with open(file_path, "rb") as audio_file:
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            transcript = transcript_response.strip()
            print("\n[Texto]:", transcript)

            # Traducción
            translation_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": TranslationPrompts[language_code].value},
                    {"role": "user", "content": transcript}
                ],
                temperature=0.5
            )
            translation = translation_response.choices[0].message.content.strip()
            print("[Traducción]:", translation)
    except Exception as e:
        print(f"Error transcribing audio: {e}")


def start(params: Dict) -> None:
    """
    Record audio from the microphone and save it to a file until user stop with CTRL + D.
    :param params:
    :return:
    """
    output_file = params.get('output_file', 'output.wav')
    language = params.get('language', 'en')
    audio_data = []

    with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
        print("Press Ctrl+C to stop recording...")

        try:
            while True:
                data = q.get()
                audio_data.append(data)
        except KeyboardInterrupt:
            print("\nRecording stopped.")
        audio_data = np.concatenate(audio_data, axis=0)
        wav.write(output_file, samplerate, audio_data)
        print(f"Audio saved to {output_file}")
    transcribe_audio(params, output_file)
    #transcribe_audio(params, "output.wav")


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Text to speech",
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser = parser.add_subparsers(title='Script select', dest='script_type')
        parser.version = '0.0.1'
        parser.add_argument("-v", "--version", action="version")
        parser.add_argument("-o", "--output-file", type=str, default="output.wav", help="Output file name")
        parser.add_argument("-l", "--language", default="es", type=str, help="Language to be used")
        params: Dict = vars(parser.parse_args())
        start(params)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as ex:
        sys.exit(1)
