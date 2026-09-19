from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mathinmovement.postprocess import (
    TimedAudioEvent,
    build_ffmpeg_command,
    build_timed_audio_mix_command,
)
from mathinmovement.production import _raw_fingerprint
from mathinmovement.models import ContentRecord


class PostProcessTests(unittest.TestCase):
    def test_ffmpeg_command_contains_music_ducking_and_loudness(self):
        command = build_ffmpeg_command(
            "raw.mp4",
            "master.mp4",
            soundtrack="music.mp3",
            duration=12.0,
            has_source_audio=True,
            music_volume=0.15,
            fade_in=1.0,
            fade_out=2.0,
            ducking=True,
            normalize=True,
            ffmpeg_binary="ffmpeg",
        )
        joined = " ".join(command)
        self.assertIn("-stream_loop -1", joined)
        self.assertIn("sidechaincompress", joined)
        self.assertIn("loudnorm=I=-16", joined)
        self.assertIn("volume=0.15", joined)
        self.assertIn("afade=t=in", joined)
        self.assertIn("afade=t=out", joined)
        self.assertIn("-c:v copy", joined)

    def test_ffmpeg_command_without_source_audio_uses_music_only(self):
        command = build_ffmpeg_command(
            "raw.mp4",
            "master.mp4",
            soundtrack="music.mp3",
            duration=8.0,
            has_source_audio=False,
            ducking=True,
            normalize=False,
            ffmpeg_binary="ffmpeg",
        )
        joined = " ".join(command)
        self.assertNotIn("sidechaincompress", joined)
        self.assertIn("[music]", joined)
        self.assertIn("-c:a aac", joined)

    def test_timed_countdown_uses_ffmpeg_atempo_and_delay(self):
        event = TimedAudioEvent(
            tag="countdown-5s",
            start=3.0,
            audio=Path("countdown-5s-original.mp3"),
            volume=1.0,
            speed=0.9,
        )
        command = build_timed_audio_mix_command(
            "raw.mp4",
            "master.mp4",
            events=[event],
            duration=12.0,
            has_source_audio=True,
            ffmpeg_binary="ffmpeg",
        )
        joined = " ".join(command)
        self.assertIn("countdown-5s-original.mp3", joined)
        self.assertIn("atempo=0.9", joined)
        self.assertIn("adelay=3000:all=1", joined)
        self.assertIn("amix=inputs=3", joined)
        self.assertIn("-c:v copy", joined)
        self.assertIn("-b:a 320k", joined)\n        self.assertIn("alimiter=limit=0.95", joined)\n        self.assertIn("-ar 48000", joined)\n        self.assertIn("-ac 2", joined)

    def test_raw_fingerprint_changes_when_asset_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.yaml"
            asset = root / "assets" / "audio" / "voice.mp3"
            asset.parent.mkdir(parents=True)
            manifest.write_text("id: demo\n", encoding="utf-8")
            asset.write_bytes(b"one")

            record = ContentRecord(
                id="demo",
                type="demo",
                title="Demo",
                path=root,
                manifest={},
            )
            first = _raw_fingerprint(
                record,
                video_format="vertical",
                quality="draft",
            )
            asset.write_bytes(b"two")
            second = _raw_fingerprint(
                record,
                video_format="vertical",
                quality="draft",
            )
            self.assertNotEqual(first, second)

    def test_raw_fingerprint_changes_with_quality(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "manifest.yaml").write_text(
                "id: demo\n",
                encoding="utf-8",
            )
            record = ContentRecord(
                id="demo",
                type="demo",
                title="Demo",
                path=root,
                manifest={},
            )
            draft = _raw_fingerprint(
                record,
                video_format="vertical",
                quality="draft",
            )
            final = _raw_fingerprint(
                record,
                video_format="vertical",
                quality="final",
            )
            self.assertNotEqual(draft, final)


if __name__ == "__main__":
    unittest.main()
