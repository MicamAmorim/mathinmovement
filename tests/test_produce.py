from __future__ import annotations

import unittest

from mathinmovement.cli import build_parser
from mathinmovement.production import resolve_target


class ProduceTests(unittest.TestCase):
    def test_cli_accepts_existing_id(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "produce",
                "ENEM-2021-MT-11",
                "--format",
                "horizontal",
                "--quality",
                "draft",
                "--skip-voice",
                "--dry-run",
            ]
        )
        self.assertEqual(args.target, "ENEM-2021-MT-11")
        self.assertEqual(args.format, "horizontal")
        self.assertTrue(args.skip_voice)
        self.assertTrue(args.dry_run)

    def test_resolve_existing_id(self):
        record, imported = resolve_target("ENEM-2021-MT-11")
        self.assertFalse(imported)
        self.assertEqual(record.id, "ENEM-2021-MT-11")
        self.assertEqual(record.type, "qenem")


if __name__ == "__main__":
    unittest.main()
