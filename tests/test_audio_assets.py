from __future__ import annotations

import unittest

from mathinmovement.config import PROJECT_ROOT
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

    def test_all_qenem_audio_is_colocated_with_content(self):
        self.assertEqual(len(self.qenem), 30)
        for record in self.qenem:
            narration = record.manifest.get("narration") or {}
            segments = narration.get("segments") or []
            expected_prefix = (
                f"content/enem/{record.id}/assets/audio/"
            )
            for segment in segments:
                audio = segment.get("audio")
                if not audio:
                    continue
                self.assertTrue(
                    str(audio).startswith(expected_prefix),
                    f"{record.id}: caminho fora do conteúdo: {audio}",
                )
                self.assertTrue(
                    (PROJECT_ROOT / str(audio)).is_file(),
                    f"{record.id}: áudio ausente: {audio}",
                )

    def test_no_root_legacy_enem_directory_remains(self):
        self.assertFalse((PROJECT_ROOT / "enem").exists())


if __name__ == "__main__":
    unittest.main()
