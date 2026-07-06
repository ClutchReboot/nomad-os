import os
import tempfile
import wave
from importlib import import_module


class SpeechToText:
    """Convert microphone audio into text."""

    def __init__(self):
        self.sample_rate = 16000
        self.duration_seconds = 5.0
        self.frames = int(self.sample_rate * self.duration_seconds)

        # Stored module references to avoid repeated imports
        self._sounddevice = None
        self._numpy = None
        self._whisper = None
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = self.whisper.load_model("base")
        return self._model

    @property
    def numpy(self):
        if self._numpy is None:
            self._numpy = import_module("numpy")
        return self._numpy

    @property
    def sounddevice(self):
        if self._sounddevice is None:
            self._sounddevice = import_module("sounddevice")
        return self._sounddevice

    @property
    def whisper(self):
        if self._whisper is None:
            self._whisper = import_module("whisper")
        return self._whisper

    def transcribe(self, prompt: str = "") -> str:
        """Capture microphone audio and convert it to text.

        If a prompt is provided, it is printed before recording begins.
        The method records a short audio sample, transcribes it with Whisper,
        and falls back to keyboard input if recording or transcription fails.
        """
        if prompt:
            print(prompt)

        try:
            audio = self._record_audio(self.frames, self.sample_rate)
            peak = self.numpy.max(self.numpy.abs(audio))
            print(f"Audio peak level: {peak:.4f}")  # Debugging output
            if peak < 0.01:
                return self._fallback_to_keyboard("")

            return self._transcribe_with_whisper(audio, self.sample_rate)
        except Exception:
            return self._fallback_to_keyboard(prompt)

    def detect_wakeword(
        self,
        wakeword: str = "nomad",
        prompt: str = "",
        duration_seconds: float = 1.5,
        silence_threshold: float = 0.005,
    ) -> bool:
        """Record a short audio sample and check whether a wake word was spoken."""
        if prompt:
            print(prompt)

        try:
            audio = self._record_audio(
                int(self.sample_rate * duration_seconds),
                self.sample_rate,
            )
            peak = self.numpy.max(self.numpy.abs(audio))
            if peak < silence_threshold:
                return False

            transcript = self._transcribe_with_whisper(
                audio,
                self.sample_rate,
                fallback_to_keyboard=False,
            )
            if not transcript:
                return False

            normalized = self._normalize_transcript(transcript)
            detected = wakeword.lower() in normalized
            if detected:
                print("✓ Wake word detected!")
            return detected
        except Exception:
            return False

    def _record_audio(self, frames: int, sample_rate: int):
        audio = self.sounddevice.rec(
            frames,
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        self.sounddevice.wait()
        return self.numpy.asarray(audio, dtype=self.numpy.float32).reshape(-1)

    def _normalize_transcript(self, transcript: str) -> str:
        return (
            transcript.strip()
            .lower()
            .replace(" ", "")
            .replace(".", "")
            .replace(",", "")
            .replace("!", "")
            .replace("?", "")
        )

    def _transcribe_with_whisper(
        self, audio, sample_rate: int, fallback_to_keyboard: bool = True
    ) -> str:
        try:
            audio = self.numpy.asarray(audio).reshape(-1)
            peak = self.numpy.max(self.numpy.abs(audio))
            if peak == 0:
                raise ValueError("Captured silence")

            # Boost weak audio signals
            if peak < 0.3:
                boost_factor = min(0.8 / peak, 4.0)  # Cap boost at 4x to avoid noise
                audio = audio * boost_factor
                peak = self.numpy.max(self.numpy.abs(audio))

            pcm_audio = self.numpy.int16(audio / peak * 32767)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
                temp_path = handle.name

            try:
                with wave.open(temp_path, "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(pcm_audio.tobytes())

                result = self.model.transcribe(temp_path, fp16=False, language="en")
                transcript = str(result.get("text", "")).strip()
                if transcript:
                    print(f"Heard: {transcript}")
                    return transcript
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except Exception:
            pass

        if fallback_to_keyboard:
            return self._fallback_to_keyboard("")
        return ""

    def _fallback_to_keyboard(self, prompt: str) -> str:
        return input(prompt)

    def listen_continuously(self) -> str:
        """Listen until speech ends or timeout, with dynamic stop on silence.

        Records audio in chunks and stops when silence is detected,
        rather than using a fixed window. Falls back to keyboard if needed.
        """
        try:
            sample_rate = 16000
            chunk_duration = 0.5  # 500ms chunks
            chunk_frames = int(sample_rate * chunk_duration)
            silence_threshold = 0.005  # Lower threshold for better sensitivity
            silence_chunks_needed = 4  # ~2 seconds of silence to stop
            max_chunks = 60  # ~30 second max duration

            audio_chunks = []
            silence_count = 0

            for chunk_idx in range(max_chunks):
                audio = self.sounddevice.rec(
                    chunk_frames,
                    samplerate=sample_rate,
                    channels=1,
                    dtype="float32",
                )
                self.sounddevice.wait()
                audio = self.numpy.asarray(audio, dtype=self.numpy.float32).reshape(-1)
                audio_chunks.append(audio)

                # Check if this chunk is silent
                peak = self.numpy.max(self.numpy.abs(audio))
                if peak < silence_threshold:
                    silence_count += 1
                    # Stop if we've heard enough silence after hearing something
                    if silence_count >= silence_chunks_needed and len(audio_chunks) > 2:
                        break
                else:
                    # Reset silence counter when we detect speech
                    silence_count = 0

            if not audio_chunks:
                return ""

            # Concatenate all chunks
            full_audio = self.numpy.concatenate(audio_chunks)
            return self._transcribe_with_whisper(full_audio, sample_rate)
        except Exception:
            return ""
