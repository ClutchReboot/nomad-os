import unittest
from unittest.mock import Mock, patch

from nomad.voice.wakeword import WakeWordDetector


class WakeWordDetectorPropertiesTests(unittest.TestCase):
    def test_properties_cache_module_imports(self):
        detector = WakeWordDetector()
        fake_sounddevice = object()
        fake_numpy = object()
        fake_whisper = Mock()
        fake_whisper.load_model.return_value = "model"

        with patch("nomad.voice.wakeword.import_module", side_effect=[fake_sounddevice, fake_numpy, fake_whisper]) as mocked_import:
            self.assertIs(detector.sounddevice, fake_sounddevice)
            self.assertIs(detector.numpy, fake_numpy)
            self.assertIs(detector.whisper, fake_whisper)
            self.assertEqual(detector.model, "model")

        self.assertEqual(mocked_import.call_count, 3)


if __name__ == "__main__":
    unittest.main()
