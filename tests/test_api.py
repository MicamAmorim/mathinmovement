from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from mathinmovement.jobs import JobStore


HAS_FASTAPI = importlib.util.find_spec("fastapi") is not None


@unittest.skipUnless(HAS_FASTAPI, "FastAPI extra não instalado")
class APISmokeTests(unittest.TestCase):
    def test_app_exposes_health_contents_and_jobs_routes(self):
        from mathinmovement.api import create_app

        with tempfile.TemporaryDirectory() as tmp:
            app = create_app(
                store=JobStore(Path(tmp) / "jobs.sqlite")
            )

        paths = {route.path for route in app.routes}
        self.assertIn("/health", paths)
        self.assertIn("/contents", paths)
        self.assertIn("/jobs", paths)
        self.assertIn("/jobs/{job_id}", paths)
        self.assertIn("/jobs/{job_id}/cancel", paths)


if __name__ == "__main__":
    unittest.main()
