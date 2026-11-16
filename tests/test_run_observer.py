
import json
import tempfile
import unittest

from pathlib import Path

from src.hr_assistant.observability.run_observer import RunObserver


class TestRunObserver(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_file = Path(self.temp_dir.name) / "logs" / "runs.jsonl"
        self.observer = RunObserver(self.log_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def read_record(self):
        with open(self.log_file, "r", encoding="utf-8") as file:
            return json.loads(file.readline())

    def test_successful_run_is_saved(self):
        self.observer.start_stage("retrieval")
        self.observer.end_stage("retrieval")

        record = self.observer.save()

        self.assertEqual(record["status"], "success")
        self.assertEqual(record["stages"]["retrieval"]["status"], "success")
        self.assertTrue(self.log_file.exists())

    def test_failed_run_is_saved(self):
        record = self.observer.fail(ValueError("Invalid context"))

        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["error"]["type"], "ValueError")
        self.assertEqual(record["error"]["message"], "Invalid context")

        persisted = self.read_record()
        self.assertEqual(persisted["status"], "failed")

    def test_failed_stage_is_closed_and_recorded(self):
        self.observer.start_stage("generation")

        record = self.observer.fail(RuntimeError("LLM unavailable"))

        self.assertNotIn("generation", self.observer.active_stages)
        self.assertEqual(record["stages"]["generation"]["status"], "failed")
        self.assertEqual(
            record["stages"]["generation"]["metadata"]["exception_type"],
            "RuntimeError",
        )

    def test_multiple_active_stages_are_marked_interrupted(self):
        self.observer.start_stage("retrieval")
        self.observer.start_stage("generation")

        record = self.observer.fail(RuntimeError("Pipeline stopped"))

        self.assertEqual(record["stages"]["retrieval"]["status"], "interrupted")
        self.assertEqual(record["stages"]["generation"]["status"], "interrupted")
        self.assertEqual(self.observer.active_stages, {})

    def test_save_rejects_active_stages(self):
        self.observer.start_stage("retrieval")

        with self.assertRaises(RuntimeError):
            self.observer.save()

    def test_duplicate_save_is_rejected(self):
        self.observer.save()

        with self.assertRaises(RuntimeError):
            self.observer.save()

    def test_metrics_are_persisted(self):
        self.observer.add_metrics({"source_count": 3})

        record = self.observer.save()

        self.assertEqual(record["metrics"]["source_count"], 3)

    def test_invalid_metrics_are_rejected(self):
        with self.assertRaises(ValueError):
            self.observer.add_metrics(["invalid"])


if __name__ == "__main__":
    unittest.main()
