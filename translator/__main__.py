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
from faster_whisper import WhisperModel
from loguru import logger
from pynput import keyboard


q = queue.Queue()
samplerate = 16000
channels = 1
duration = 5  # seconds per recording
chunk = 1024
logger.add("audio.log", rotation="1 MB")

class TranslationPrompts(Enum):
    ES = "Traduce el siguiente texto al español."
    EN = "Translate the following text to English."
    FR = "Traduisez le texte suivant en français."
    DE = "Übersetzen Sie den folgenden Text ins Deutsche."

def translate_transcription(text: str, p: Dict) -> None:
    to_language: str = p.get('to_lang', 'es').upper()
    service: str = p.get('service', 'deepseek').lower()

    if text is None:
        logger.info("transcription failed")
        pass

    if service == "deepseek":
        translate_with_deepseek(text, to_language)
    if service == "openai":
        translate_with_openai(text, to_language)
    if service == "ollama":
        # TODO: implement ollama connection
        pass

def callback(indata, frames, time, status):
    q.put(indata.copy())

def transcribe_audio(p: dict) -> str | None:
    """Transcribe audio using OpenAI's Whisper model."""
    try:
        file_path: str = p.get('output_file', 'output.wav')
        text: str = p.get('text')

        if p.get("transcript") == "local":
            transcript = transcription_with_whisper(text, p)
        else:
            transcript = transcription_with_openai(file_path)
        return transcript
    except Exception as e:
        logger.error(f"error transcribing audio: {e}")
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
            logger.info("Press Ctrl+C to stop recording...")

            try:
                while True:
                    data = q.get()
                    audio_data.append(data)
            except KeyboardInterrupt:
                logger.info("Recording stopped.")
            audio_data = np.concatenate(audio_data, axis=0)
            wav.write(output_file, samplerate, audio_data)
            logger.info(f"audio saved to {output_file}")
        t = transcribe_audio(params_record)

    translate_transcription(t, params_record)

def transcription_with_whisper(text: str, params: Dict) -> str:
    """
    Transcribe audio using OpenAI's Whisper model.
    :param text:
    :param params:
    :return:
    """
    model = WhisperModel("small", device=params.get("hardware"))  # Usa "cpu" si no tienes GPU
    response: str = ""
    lng: str = str(params.get("from_lang")).lower()
    segments, info = model.transcribe(params.get("output_file"), language=lng)
    for segment in segments:
        logger.info(f"[TEXT]: {segment.text}")
        response += segment.text
    return response

def transcription_with_openai(file_path: str) -> str:
    client = OpenAI()
    with open(file_path, "rb") as audio_file:
        transcript_response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
        transcript = transcript_response.strip()
        logger.info(f"[TEXT]: {transcript}")

    return transcript

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
        logger.info(f"🌍 [TRANSLATE]: {translation}")
        return translation
    else:
        logger.error(f"[ERROR]: {response.text}")
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
        logger.info("[translate]:", translation)
        return translation.lower()
    except Exception as e:
        logger.error(f"[ERROR]: {e}")
        return text

def continuous_recording(params: Dict) -> None:
    """Continuous recording and translation until interrupted."""
    logger.info("🔊 Continuous mode activated. Press Ctrl+C to exit.")
    try:
        while True:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
                record_audio(params)
                t = transcribe_audio(params.get("output_file"))
                translate_transcription(t, params)
    except KeyboardInterrupt:
        logger.info("🛑 stop record")

def record_audio(params: Dict) -> None:
    """Records audio from the microphone and saves it to a file."""
    logger.info(f"🎙️ recording {params.get("chunk_duration")} seconds... (Press Ctrl+C to stop)")

    sample_rate = params.get("samplerate")
    output_file = params.get("output_file")
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()  # Wait until the recording is finished
    # Save the audio in WAV format
    import scipy.io.wavfile as wav
    wav.write(output_file, sample_rate, audio_data)

def listen_for_spacebar(params: Dict) -> None:
    """Listen for spacebar press to re-execute the script."""
    try:
        esc_key_pressed: bool = False
        logger.info("Press the space to execute the script or press esc to exit")

        with keyboard.Events() as events:
            for event in events:
                if event.key == keyboard.Key.space:
                    logger.info("Space pressed. Re-executing the script.")
                    if params.get("record") and params.get("continuous"):
                        continuous_recording(params)
                    elif params.get("record"):
                        record_audio(params)
                        t: str = transcribe_audio(params)
                        translate_transcription(t, params)
                    else:
                        start(params)
                    break
                elif event.key == keyboard.Key.esc:
                    logger.info("Esc pressed. Exiting the script.")
                    esc_key_pressed = True
                    sys.exit(0)
    except Exception as e:
        logger.error(f"[ERROR]: {e}")
    finally:
        if not esc_key_pressed:
            listen_for_spacebar(params)

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Text to speech",
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser = parser.add_subparsers(title='Script select', dest='script_type')
        parser.version = '0.0.1'
        parser.add_argument("-v", "--version", action="version")
        parser.add_argument("--samplerate", default=16000, type=int, help="Sampling rate")
        parser.add_argument("--channels", default=1, type=int, help="Channels")
        parser.add_argument("--chunk-duration", default=1024, type=int, help="Chunk size")
        parser.add_argument("--duration", default=5, type=int, help="Duration")
        parser.add_argument("--continuous", action="store_true",
                            help="Activa el modo grabación continua")
        parser.add_argument("--hardware", default="cpu", choices=["cpu", "cuda"], help="Hardware to use")
        parser.add_argument("--from-lang", default="es", type=str, help="Language of audio")
        parser.add_argument("--to-lang", default="es", type=str, help="Language to be translated")
        parser.add_argument("-o", "--output-file", type=str, default="output.wav", help="Output file name")
        parser.add_argument("-r", "--record", action="store_true", help="Record audio")
        parser.add_argument("--stop-and-resume", action="store_true", help="Stop recording after recording")
        parser.add_argument("-s", "--service", choices=["openai", "deepseek", "ollama"], default="deepseek",
                            help="Service to use")
        parser.add_argument("-t", "--text", default="", type=str, help="Translate text directly")
        parser.add_argument("--transcript", choices=["local"], default="local", type=str, help="Transcription service to use")
        params: Dict = vars(parser.parse_args())

        listen_for_spacebar(params)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as ex:
        sys.exit(1)
