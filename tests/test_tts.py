from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from mathinmovement.models import ContentRecord
from mathinmovement.tts import (
    narration_fingerprint,
    prepare_narration,
)


class TTSTests(unittest.TestCase):
    def make_record(self, root: Path) -> ContentRecord:
        path = root / "content" / "enem" / "TEST-Q"
        path.mkdir(parents=True)
        manifest = {
            "schema_version": 1,
            "id": "TEST-Q",
            "type": "qenem",
            "status": "draft",
            "title": "Teste",
            "exam": {
                "name": "Teste",
                "year": 2026,
                "canonical_id": "TEST-Q",
                "question_number": 1,
            },
            "question": {
                "stem": "Enunciado.",
                "options": {
                    "A": "1",
                    "B": "2",
                    "C": "3",
                    "D": "4",
                    "E": "5",
                },
                "answer": "A",
            },
            "solution": {
                "goal": "Resolver.",
                "strategy": ["Calcular."],
                "steps": [{"label": "Passo", "math": "1"}],
                "final_answer": "A",
            },
            "render": {
                "production_engine": "native",
                "formats": ["vertical"],
                "native_formats": ["vertical"],
                "default_format": "vertical",
                "native_ready": True,
            },
            "narration": {
                "enabled": True,
                "language": "pt-BR",
                "voice": "pt-BR-AntonioNeural",
                "segments": [
                    {
                        "key": "source",
                        "text": "Olá mundo.",
                    }
                ],
            },
        }
        (path / "manifest.yaml").write_text(
            yaml.safe_dump(
                manifest,
                allow_unicode=True,
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        return ContentRecord(
            id="TEST-Q",
            type="qenem",
            title="Teste",
            path=path,
            manifest=manifest,
        )

    def test_generates_audio_and_updates_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = self.make_record(root)
            calls = []

            def fake_synth(
                text, output, voice, rate, volume, pitch
            ):
                calls.append((text, voice, rate, volume, pitch))
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b"fake-mp3")

            result = prepare_narration(
                record,
                project_root=root,
                synthesizer=fake_synth,
                duration_reader=lambda _: 2.75,
            )

            self.assertEqual(result.generated, 1)
            self.assertEqual(result.cached, 0)
            self.assertEqual(len(calls), 1)

            saved = yaml.safe_load(
                (
                    record.path / "manifest.yaml"
                ).read_text(encoding="utf-8")
            )
            segment = saved["narration"]["segments"][0]
            self.assertEqual(segment["duration"], 2.75)
            self.assertEqual(
                segment["audio"],
                "assets/audio/source.mp3",
            )
            self.assertTrue(
                (
                    record.path
                    / "assets"
                    / "audio"
                    / "source.mp3"
                ).is_file()
            )
            self.assertEqual(
                segment["tts_fingerprint"],
                narration_fingerprint(
                    "Olá mundo.",
                    "pt-BR-AntonioNeural",
                    "+4%",
                    "+0%",
                    "+0Hz",
                ),
            )

    def test_existing_audio_is_cache_without_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = self.make_record(root)
            audio = (
                record.path / "assets" / "audio" / "source.mp3"
            )
            audio.parent.mkdir(parents=True)
            audio.write_bytes(b"existing")
            segment = record.manifest["narration"]["segments"][0]
            segment["audio"] = (
                "content/enem/TEST-Q/assets/audio/source.mp3"
            )
            segment["duration"] = 3.0

            called = []
            result = prepare_narration(
                record,
                project_root=root,
                synthesizer=lambda *args: called.append(args),
                duration_reader=lambda _: 3.0,
            )
            self.assertEqual(result.generated, 0)
            self.assertEqual(result.cached, 1)
            self.assertEqual(called, [])

    def test_dry_run_plans_missing_audio_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = self.make_record(root)
            result = prepare_narration(
                record,
                project_root=root,
                dry_run=True,
                synthesizer=lambda *args: self.fail(
                    "não deveria sintetizar"
                ),
            )
            self.assertEqual(result.planned, 1)
            self.assertFalse(
                (
                    record.path / "assets" / "audio" / "source.mp3"
                ).exists()
            )


if __name__ == "__main__":
    unittest.main()
