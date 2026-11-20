"""Audit jsonl theo tháng (LLD 4.3). Không bao giờ ghi nội dung (SEC-06)."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

CONTENT_FIELDS = frozenset({"text", "content", "reply", "question", "instructions"})


class AuditJsonl:
    def __init__(self, dir: Path, clock: Callable[[], datetime] = lambda: datetime.now(UTC)):
        self.dir = Path(dir)
        self.clock = clock

    def write(self, event: str, **fields: object) -> None:
        bad = CONTENT_FIELDS & fields.keys()
        if bad:
            raise ValueError(f"audit không được ghi nội dung: {sorted(bad)}")
        now = self.clock().astimezone(UTC)
        line = {"ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "event": event, **fields}
        self.dir.mkdir(parents=True, exist_ok=True)
        with (self.dir / f"audit-{now:%Y-%m}.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False, default=str) + "\n")
