# -*- coding: utf-8 -*-
import argparse
import sys
import queue
import os
import tempfile

import requests
import numpy as np
from enum import Enum
from openai import OpenAI
import scipy.io.wavfile as wav
import sounddevice as sd
from typing import Dict


q = queue.Queue()
samplerate = 16000
channels = 1
duration = 5  # seconds per recording
chunk = 1024


class TranslationPrompts(Enum):
    ES = "Traduce el siguiente texto al español."
    EN = "Translate the following text to English."
    FR = "Traduisez le texte suivant en français."
    DE = "Übersetzen Sie den folgenden Text ins Deutsche."

def process_transcription(text: str, params: Dict) -> None:
    language: str = params.get('language', 'es').upper()
    service: str = params.get('service', 'deepseek').lower()

    if text is None:
        print("transcription failed")
        pass

    if service == "deepseek":
        translate_with_deepseek(text, language)
    if service == "openai":
        translate_with_openai(text, language)
    if service == "ollama":
        # TODO: implement ollama connection
        pass

def callback(indata, frames, time, status):
    q.put(indata.copy())

def transcribe_audio(file_path: str) -> str | None:
    """Transcribe audio using OpenAI's Whisper model."""
    try:
        client = OpenAI()
        with open(file_path, "rb") as audio_file:
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            transcript = transcript_response.strip()
            print("\n[Texto]:", transcript)

        return transcript
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None

def start(params_record: Dict) -> None:
    """
    Record audio from the microphone and save it to a file until user stop with CTRL + D.
    :param params_record:
    :return:
    """
    output_file: str = params_record.get('output_file', 'output.wav')
    text: str = params_record.get('text')
    audio_data = []

    if text != "":
        t = text
    else:
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
        t = transcribe_audio(output_file)

    process_transcription(t, params)

def translate_with_deepseek(text: str, target_language: str) -> str:
    """
    Translate with DeepSeek
    :param text:
    :param target_language:
    :return:
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")  # Reemplaza con tu API key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": TranslationPrompts[target_language].value},
            {"role": "user", "content": text}
        ],
        "stream": False
    }
    response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        translation: str = response.json().get("choices")[0]["message"]["content"]
        print("🌍 [translate]:", translation)
        return translation
    else:
        print(f"[ERROR]: {response.text}")
        return text  # Fallback al texto original si hay error

def translate_with_openai(text: str, target_language: str) -> str:
    """
    Translate text with OpenAI
    :param text:
    :param target_language:
    :return:
    """
    try:
        client = OpenAI()
        translation_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": TranslationPrompts[target_language].value},
                {"role": "user", "content": text}
            ],
            temperature=0.5
        )
        translation = translation_response.choices[0].message.content.strip()
        print("[translate]:", translation)
        return translation.lower()
    except Exception as e:
        print(f"[ERROR]: {e}")
        return text

def continuous_recording(params: Dict) -> None:
    """Grabación y traducción continua hasta interrupción."""
    print("🔊 Modo continuo activado. Presiona Ctrl+C para salir.")
    try:
        while True:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
                record_audio(params)
                t = transcribe_audio(params.get("output_file"))
                process_transcription(t, params)
    except KeyboardInterrupt:
        print("\n🛑 Grabación detenida.")

def record_audio(params: Dict) -> None:
    """Graba audio desde el micrófono y lo guarda en un archivo."""
    print(f"🎙️ Grabando {params.get("chunk_duration")} segundos... (Presiona Ctrl+C para detener)")

    sample_rate = params.get("samplerate")
    output_file = params.get("output_file")
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()  # Espera hasta que termine la grabación
    # Guarda el audio en formato WAV
    import scipy.io.wavfile as wav
    wav.write(output_file, sample_rate, audio_data)


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Text to speech",
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser = parser.add_subparsers(title='Script select', dest='script_type')
        parser.version = '0.0.1'
        parser.add_argument("-v", "--version", action="version")
        parser.add_argument("-o", "--output-file", type=str, default="output.wav", help="Output file name")
        parser.add_argument("-l", "--language", default="es", type=str, help="Language to be used")
        parser.add_argument("-s", "--service", choices=["openai", "deepseek", "ollama"], default="deepseek",
                            help="Service to use")
        parser.add_argument("-t", "--text", default="", type=str, help="Translate text directly")
        parser.add_argument("--samplerate", default=16000, type=int, help="Sampling rate")
        parser.add_argument("--channels", default=1, type=int, help="Channels")
        parser.add_argument("--chunk-duration", default=1024, type=int, help="Chunk size")
        parser.add_argument("--duration", default=5, type=int, help="Duration")
        parser.add_argument("--continuous", action="store_true",
                            help="Activa el modo grabación continua")
        parser.add_argument("-r", "--record", action="store_true", help="Record audio")
        parser.add_argument("--stop-and-resume", action="store_true", help="Stop recording after recording")
        params: Dict = vars(parser.parse_args())

        if params.get("record") and params.get("continuous"):
            continuous_recording(params)
        elif params.get("record"):
            record_audio(params)
            t: str = transcribe_audio(params.get("output_file"))
            process_transcription(t, params)
        else:
            start(params)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as ex:
        sys.exit(1)
