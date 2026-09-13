from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from mathinmovement.jobs import JobStore


HAS_FASTAPI = importlib.util.find_spec("fastapi") is not None
HAS_MULTIPART = importlib.util.find_spec("multipart") is not None
HAS_API = HAS_FASTAPI and HAS_MULTIPART


@unittest.skipUnless(HAS_API, "FastAPI/multipart extra não instalado")
class APISmokeTests(unittest.TestCase):
    def test_app_exposes_health_contents_and_jobs_routes(self):
        from mathinmovement.api import create_app

        with tempfile.TemporaryDirectory() as tmp:
            app = create_app(
                store=JobStore(Path(tmp) / "jobs.sqlite")
            )

        paths = {route.path for route in app.routes}
        self.assertIn("/", paths)
        self.assertIn("/studio", paths)
        self.assertIn("/studio/assets", paths)
        self.assertIn("/health", paths)
        self.assertIn("/contents", paths)
        self.assertIn("/imports", paths)
        self.assertIn("/uploads/music", paths)
        self.assertIn("/system/open-media-folder", paths)
        self.assertIn("/jobs", paths)
        self.assertIn("/jobs/{job_id}", paths)
        self.assertIn("/jobs/{job_id}/cancel", paths)


if __name__ == "__main__":
    unittest.main()
