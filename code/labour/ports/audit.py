from typing import Protocol


class Audit(Protocol):
    def write(self, event: str, **fields: object) -> None: ...
