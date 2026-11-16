
import json
import time
import uuid

from datetime import datetime, timezone
from pathlib import Path


class RunObserver:
    """Collect and persist structured execution telemetry."""

    def __init__(self, log_file):
        self.log_file = Path(log_file)

        self.run_id = str(uuid.uuid4())
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.start_time = time.perf_counter()

        self.stages = {}
        self.active_stages = {}
        self.metrics = {}

        self.status = "running"
        self.error = None
        self._saved = False

    def start_stage(self, stage_name):
        if stage_name in self.active_stages:
            raise ValueError(f"Stage already running: {stage_name}")

        self.active_stages[stage_name] = time.perf_counter()

    def end_stage(self, stage_name, status="success", metadata=None):
        if stage_name not in self.active_stages:
            raise ValueError(f"Stage was not started: {stage_name}")

        duration = time.perf_counter() - self.active_stages.pop(stage_name)

        self.stages[stage_name] = {
            "status": status,
            "duration_seconds": round(duration, 4),
            "metadata": metadata or {},
        }

    def add_metrics(self, metrics):
        if not isinstance(metrics, dict):
            raise ValueError("metrics must be a dictionary")

        self.metrics.update(metrics)

    def build_record(self):
        finished_at = datetime.now(timezone.utc).isoformat()
        total_duration = time.perf_counter() - self.start_time

        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": finished_at,
            "total_duration_seconds": round(total_duration, 4),
            "status": self.status,
            "error": self.error,
            "stages": self.stages,
            "metrics": self.metrics,
        }

    def save(self):
        if self._saved:
            raise RuntimeError("Run telemetry has already been saved.")

        if self.active_stages:
            raise RuntimeError(
                f"Cannot save while stages are running: "
                f"{list(self.active_stages.keys())}"
            )

        if self.status == "running":
            self.status = "success"

        record = self.build_record()

        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

        self._saved = True
        return record

    def fail(self, exception):
        """Record a failed run and close any active stages."""

        if not isinstance(exception, BaseException):
            raise TypeError("exception must be an exception instance")

        if self._saved:
            return None

        self.status = "failed"
        self.error = {
            "type": type(exception).__name__,
            "message": str(exception)[:1000],
        }

        now = time.perf_counter()
        active_stage_names = list(self.active_stages.keys())

        for stage_name in active_stage_names:
            start_time = self.active_stages.pop(stage_name)

            stage_status = (
                "failed"
                if len(active_stage_names) == 1
                else "interrupted"
            )

            metadata = (
                {
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception)[:1000],
                }
                if stage_status == "failed"
                else {"interrupted": True}
            )

            self.stages[stage_name] = {
                "status": stage_status,
                "duration_seconds": round(now - start_time, 4),
                "metadata": metadata,
            }

        return self.save()
