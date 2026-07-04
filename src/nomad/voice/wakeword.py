import os
import tempfile
import wave
from importlib import import_module


class WakeWordDetector:
    """Detect when the robot should start listening for 'Nomad'.

    Listens in short chunks and transcribes with Whisper to detect the wake word.
    Falls back to keyboard if audio unavailable.
    """

    def __init__(self):
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

    def listen(self) -> bool:
        """Listen for the 'Nomad' wake word. Returns True if detected.

        Records audio, transcribes it, and checks if 'nomad'
        appears in the text. Returns False if silence or no match.
        """
        try:
            # Short listening window for wake-word detection
            sample_rate = 16000
            duration_seconds = 1.5  # Slightly longer for better capture
            frames = int(sample_rate * duration_seconds)

            audio = self.sounddevice.rec(
                frames,
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
            )
            self.sounddevice.wait()
            audio = self.numpy.asarray(audio, dtype=self.numpy.float32).reshape(-1)

            # Check for silence
            peak = self.numpy.max(self.numpy.abs(audio))
            if peak < 0.005:  # Lowered threshold to be more sensitive
                return False

            # Transcribe and check for "nomad"
            transcript = self._transcribe_audio(audio, sample_rate)
            if transcript:
                print(f"  Heard: {transcript}")
                # Remove spaces and punctuation for matching
                normalized = (
                    transcript.strip()
                    .lower()
                    .replace(" ", "")
                    .replace(".", "")
                    .replace(",", "")
                )
                detected = "nomad" in normalized
                if detected:
                    print(f"✓ Wake word detected!")
                return detected
            return False

        except Exception:
            return False

    def _transcribe_audio(self, audio, sample_rate: int) -> str:
        """Transcribe audio using Whisper."""
        try:

            audio = self.numpy.asarray(audio).reshape(-1)
            peak = self.numpy.max(self.numpy.abs(audio))
            if peak == 0:
                return ""

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
                text = str(result.get("text", "")).strip()
                return text
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except Exception:
            return ""

    def _fallback_keyboard_wakeword(self) -> bool:
        """Fallback when audio is unavailable."""
        text = input("Say 'Nomad' (or type it): ").strip().lower()
        return "nomad" in text
