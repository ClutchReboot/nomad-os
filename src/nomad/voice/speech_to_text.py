"""Speech-to-text helpers."""

import os
import tempfile
import wave
from importlib import import_module


class SpeechToText:
    """Convert microphone audio into text.

    The implementation uses sounddevice for microphone capture and whisper for
    transcription so it can work on Python 3.14 without the old PyAudio-based
    stack.
    """

    def transcribe(self, prompt: str = "") -> str:
        try:
            sounddevice = import_module("sounddevice")
            numpy = import_module("numpy")
        except ImportError as exc:
            print(f"Audio backend unavailable: {exc}")
            return self._fallback_to_keyboard(prompt)

        if prompt:
            print(prompt)

        try:
            sample_rate = 16000
            duration_seconds = 5.0
            frames = int(sample_rate * duration_seconds)
            print("Listening...")
            audio = sounddevice.rec(
                frames,
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
            )
            sounddevice.wait()
            audio = numpy.asarray(audio, dtype=numpy.float32).reshape(-1)
            
            peak = numpy.max(numpy.abs(audio))
            if peak < 0.01:
                print("No speech detected (silence). Please speak louder.")
                return self._fallback_to_keyboard("")
            
            return self._transcribe_with_whisper(audio, sample_rate)
        except Exception as exc:
            print(f"Microphone capture failed: {exc}")
            return self._fallback_to_keyboard(prompt)

    def _transcribe_with_whisper(self, audio, sample_rate: int) -> str:
        try:
            whisper = import_module("whisper")
            numpy = import_module("numpy")
        except ImportError as exc:
            print(f"Whisper transcription unavailable: {exc}")
            return self._fallback_to_keyboard("")

        try:
            audio = numpy.asarray(audio).reshape(-1)
            peak = numpy.max(numpy.abs(audio))
            if peak == 0:
                raise ValueError("Captured silence")

            pcm_audio = numpy.int16(audio / peak * 32767)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
                temp_path = handle.name

            try:
                with wave.open(temp_path, "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(pcm_audio.tobytes())

                model = whisper.load_model("tiny")
                result = model.transcribe(temp_path, fp16=False, language="en")
                transcript = str(result.get("text", "")).strip()
                if transcript:
                    print(f"Heard: {transcript}")
                    return transcript
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except Exception as exc:
            print(f"Speech recognition failed: {exc}")

        return self._fallback_to_keyboard("")

    def _fallback_to_keyboard(self, prompt: str) -> str:
        return input(prompt)

    def listen_continuously(self) -> str:
        """Listen in a loop until speech is detected, or fall back to keyboard.

        Useful for wake-word detection and other always-listening scenarios.
        """
        try:
            sounddevice = import_module("sounddevice")
            numpy = import_module("numpy")
        except ImportError as exc:
            print(f"Audio backend unavailable: {exc}")
            return input("> ")

        try:
            sample_rate = 16000
            duration_seconds = 5.0
            frames = int(sample_rate * duration_seconds)
            audio = sounddevice.rec(
                frames,
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
            )
            sounddevice.wait()
            audio = numpy.asarray(audio, dtype=numpy.float32).reshape(-1)

            peak = numpy.max(numpy.abs(audio))
            if peak < 0.01:
                return ""

            return self._transcribe_with_whisper(audio, sample_rate)
        except Exception as exc:
            print(f"Microphone capture failed: {exc}")
            return ""

