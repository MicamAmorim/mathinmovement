from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "src" / "mathinmovement" / "studio"


class StudioAssetTests(unittest.TestCase):
    def test_studio_assets_exist_and_reference_core_endpoints(self):
        index = (STUDIO / "index.html").read_text(encoding="utf-8")
        script = (STUDIO / "app.js").read_text(encoding="utf-8")
        style = (STUDIO / "styles.css").read_text(encoding="utf-8")

        self.assertIn("Math in Movement Studio", index)
        self.assertIn('id="catalog"', index)
        self.assertIn('id="renderForm"', index)
        self.assertIn('id="jobsBody"', index)
        self.assertIn('request("/contents")', script)
        self.assertIn('request("/jobs?limit=30")', script)
        self.assertIn('method: "POST"', script)
        self.assertIn(".catalog-grid", style)
        self.assertIn(".job-status", style)

    def test_package_data_includes_studio_assets(self):
        data = tomllib.loads(
            (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )
        package_data = (
            data.get("tool", {})
            .get("setuptools", {})
            .get("package-data", {})
            .get("mathinmovement", [])
        )
        self.assertIn("studio/*.html", package_data)
        self.assertIn("studio/*.css", package_data)
        self.assertIn("studio/*.js", package_data)


if __name__ == "__main__":
    unittest.main()
