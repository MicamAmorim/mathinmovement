from __future__ import annotations

import unittest

from mathinmovement.cli import build_parser


class RenderAllStatusTests(unittest.TestCase):
    def test_render_accepts_all_status(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "render",
                "--all",
                "--type",
                "qenem",
                "--status",
                "all",
                "--engine",
                "native",
            ]
        )
        self.assertTrue(args.all)
        self.assertEqual(args.type, "qenem")
        self.assertEqual(args.status, "all")
        self.assertEqual(args.engine, "native")


if __name__ == "__main__":
    unittest.main()
