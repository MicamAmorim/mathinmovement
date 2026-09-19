from __future__ import annotations

import shutil
import subprocess
import unittest

from mathinmovement.config import PROJECT_ROOT
from mathinmovement.registry import Registry


class AudioAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()
        cls.qenem = cls.registry.find(
            content_type="qenem",
            status="production",
        )

    def test_countdown_opus_is_decodable_by_ffprobe(self):
        ffprobe = shutil.which("ffprobe")
        if ffprobe is None:
            self.skipTest("ffprobe não disponível")

        audio = PROJECT_ROOT / "assets" / "audio" / "countdown-5s.opus"
        self.assertTrue(audio.is_file())
        result = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(float(result.stdout.strip()), 5.0)

    def test_all_qenem_audio_is_package_relative_and_exists(self):
        self.assertEqual(len(self.qenem), 30)
        for record in self.qenem:
            narration = record.manifest.get("narration") or {}
            segments = narration.get("segments") or []
            for segment in segments:
                audio = segment.get("audio")
                if not audio:
                    continue
                self.assertTrue(
                    str(audio).startswith("assets/audio/"),
                    f"{record.id}: caminho não portátil: {audio}",
                )
                self.assertTrue(
                    (record.path / str(audio)).is_file(),
                    f"{record.id}: áudio ausente: {audio}",
                )


if __name__ == "__main__":
    unittest.main()
