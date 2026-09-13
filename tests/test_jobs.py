from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from mathinmovement.jobs import JobStore
from mathinmovement.worker import run_worker_once


class JobStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "jobs.sqlite"
        self.store = JobStore(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def test_enqueue_get_and_list(self):
        job = self.store.enqueue(
            kind="produce",
            payload={
                "target": "area-triangulo",
                "quality": "draft",
            },
            job_id="job-1",
        )
        self.assertEqual(job.status, "queued")
        self.assertEqual(
            self.store.get("job-1").payload["target"],
            "area-triangulo",
        )
        listed = self.store.list(status="queued")
        self.assertEqual([item.id for item in listed], ["job-1"])

    def test_claim_is_atomic_and_only_claims_once(self):
        self.store.enqueue(
            kind="produce",
            payload={"target": "area-triangulo"},
            job_id="job-1",
        )
        first = self.store.claim_next(kinds={"produce"})
        second = self.store.claim_next(kinds={"produce"})
        self.assertIsNotNone(first)
        self.assertEqual(first.id, "job-1")
        self.assertEqual(first.status, "running")
        self.assertIsNone(second)

    def test_cancel_only_queued_job(self):
        self.store.enqueue(
            kind="produce",
            payload={"target": "area-triangulo"},
            job_id="job-1",
        )
        canceled = self.store.cancel("job-1")
        self.assertEqual(canceled.status, "canceled")
        with self.assertRaises(ValueError):
            self.store.claim_next(kinds={"produce"}) or self.store.cancel(
                "job-1"
            )

    def test_succeed_and_fail_transitions(self):
        self.store.enqueue(
            kind="produce",
            payload={"target": "a"},
            job_id="ok",
        )
        self.store.claim_next()
        succeeded = self.store.succeed(
            "ok",
            {"output": "video.mp4"},
        )
        self.assertEqual(succeeded.status, "succeeded")
        self.assertEqual(succeeded.result["output"], "video.mp4")

        self.store.enqueue(
            kind="produce",
            payload={"target": "b"},
            job_id="bad",
        )
        self.store.claim_next()
        failed = self.store.fail("bad", "boom")
        self.assertEqual(failed.status, "failed")
        self.assertEqual(failed.error, "boom")


class WorkerTests(unittest.TestCase):
    def test_worker_executes_queued_produce_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = JobStore(Path(tmp) / "jobs.sqlite")
            store.enqueue(
                kind="produce",
                payload={
                    "target": "area-triangulo",
                    "quality": "draft",
                },
                job_id="job-1",
            )
            fake_result = SimpleNamespace(
                record=SimpleNamespace(id="area-triangulo"),
                output=Path("media/demo/vertical/area-triangulo.mp4"),
                raw_output=None,
                imported=False,
            )
            with patch(
                "mathinmovement.worker.produce",
                return_value=fake_result,
            ) as mocked:
                completed = run_worker_once(store)

            self.assertEqual(completed.status, "succeeded")
            self.assertEqual(
                completed.result["content_id"],
                "area-triangulo",
            )
            mocked.assert_called_once()

    def test_worker_records_production_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = JobStore(Path(tmp) / "jobs.sqlite")
            store.enqueue(
                kind="produce",
                payload={"target": "missing"},
                job_id="job-1",
            )
            with patch(
                "mathinmovement.worker.produce",
                side_effect=RuntimeError("render failed"),
            ):
                completed = run_worker_once(store)

            self.assertEqual(completed.status, "failed")
            self.assertIn("render failed", completed.error)


if __name__ == "__main__":
    unittest.main()
