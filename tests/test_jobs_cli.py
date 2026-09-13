from __future__ import annotations

import unittest

from mathinmovement.cli import build_parser


class JobsCLITests(unittest.TestCase):
    def test_worker_once_parser(self):
        args = build_parser().parse_args(
            ["worker", "--once"]
        )
        self.assertTrue(args.once)

    def test_jobs_list_parser(self):
        args = build_parser().parse_args(
            ["jobs", "list", "--status", "queued", "--json"]
        )
        self.assertEqual(args.jobs_command, "list")
        self.assertEqual(args.status, "queued")
        self.assertTrue(args.json)

    def test_serve_parser(self):
        args = build_parser().parse_args(
            ["serve", "--host", "0.0.0.0", "--port", "8080"]
        )
        self.assertEqual(args.host, "0.0.0.0")
        self.assertEqual(args.port, 8080)


if __name__ == "__main__":
    unittest.main()
