from __future__ import annotations

import ast
from pathlib import Path
import unittest

from mathinmovement.config import PROJECT_ROOT
from mathinmovement.registry import Registry


class FullCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()
        cls.records = cls.registry.all()

    def test_catalog_contains_exactly_30_demos_and_30_qenem(self):
        demos = [r for r in self.records if r.type == "demo"]
        qenem = [r for r in self.records if r.type == "qenem"]
        self.assertEqual(len(self.records), 60)
        self.assertEqual(len(demos), 30)
        self.assertEqual(len(qenem), 30)

    def test_catalog_promotion_state_is_explicit(self):
        production = [
            r for r in self.records
            if r.manifest.get("status") == "production"
        ]
        drafts = [
            r for r in self.records
            if r.manifest.get("status") == "draft"
        ]
        self.assertEqual(
            {r.id for r in production},
            {
                "area-triangulo",
                "area-paralelogramo",
                "area-trapezio",
                "area-losango",
                "area-triangulo-equilatero",
                "area-poligonos-regulares",
                "comprimento-circunferencia-pi",
                "area-circulo",
                "comprimento-arco",
                "area-setor-circular",
                "area-coroa-circular",
                "teorema-pitagoras",
                "relacoes-metricas-triangulo-retangulo",
                "razoes-trigonometricas-semelhanca",
                "lei-senos",
                "lei-cossenos",
                "area-triangulo-seno",
                "escalas-comprimentos-areas-volumes",
                "relacao-euler-poliedros",
                "diagonal-paralelepipedo",
                "ENEM-2021-MT-11",
            },
        )
        self.assertEqual(len(drafts), 39)

        for record in production:
            render = record.manifest["render"]
            self.assertEqual(render["production_engine"], "native")
            self.assertTrue(render["native_ready"])

        candidate_ids = {
            "area-prismas-planificacao",
            "volume-prismas",
            "area-cilindro",
            "volume-cilindro",
            "area-piramides-regulares",
        }
        for record in drafts:
            render = record.manifest["render"]
            self.assertEqual(render["production_engine"], "compatibility")
            self.assertEqual(render["native_ready"], record.id in candidate_ids)

    def test_every_compatibility_source_and_scene_exists(self):
        for record in self.records:
            compat = (record.manifest.get("render") or {}).get("compatibility")
            self.assertIsInstance(compat, dict, record.id)

            source = PROJECT_ROOT / compat["source"]
            self.assertTrue(source.exists(), f"{record.id}: fonte ausente {source}")

            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
            classes = {
                node.name for node in tree.body
                if isinstance(node, ast.ClassDef)
            }
            self.assertIn(
                compat["scene"],
                classes,
                f"{record.id}: cena {compat['scene']!r} ausente em {source}",
            )

    def test_qenem_answers_match_solution(self):
        for record in self.records:
            if record.type != "qenem":
                continue
            self.assertEqual(
                record.manifest["question"]["answer"],
                record.manifest["solution"]["final_answer"],
                record.id,
            )


if __name__ == "__main__":
    unittest.main()
