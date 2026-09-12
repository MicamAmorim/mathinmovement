from __future__ import annotations

import unittest

from mathinmovement.registry import Registry


class AudioAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()
        cls.qenem = [
            record
            for record in cls.registry.all()
            if record.type == "qenem"
        ]

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
