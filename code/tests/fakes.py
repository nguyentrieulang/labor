from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from labour.ports.channel import RateLimited
from labour.ports.models import BotRights, IncomingFile, MessageEvent, Outgoing


@dataclass
class Sent:
    chat_id: int
    bot: str
    text: str
    reply_to: int | None
    message_id: int


class FakeChannel:
    def __init__(self, rights: dict[str, BotRights] | None = None):
        self.sent: list[Sent] = []
        self.pinned: list[tuple[int, str, int]] = []
        self.rights = rights or {}
        self.rate_limit_once: float | None = None
        self._next = 1000
        self.on_event = None

    async def start(self, on_event) -> None:
        self.on_event = on_event

    async def send_text(self, chat_id, bot, text, reply_to=None) -> int:
        if self.rate_limit_once is not None:
            ra, self.rate_limit_once = self.rate_limit_once, None
            raise RateLimited(ra)
        self._next += 1
        self.sent.append(Sent(chat_id, bot, text, reply_to, self._next))
        return self._next

    async def edit_text(self, chat_id, bot, message_id, text) -> None: ...

    async def pin(self, chat_id, bot, message_id) -> None:
        self.pinned.append((chat_id, bot, message_id))

    async def unpin(self, chat_id, bot, message_id) -> None: ...

    async def send_file(self, chat_id, bot, path: Path, caption) -> int:
        raise NotImplementedError

    async def download(self, bot, f: IncomingFile, dest: Path) -> None:
        raise NotImplementedError

    async def bot_rights(self, chat_id, bot) -> BotRights:
        return self.rights.get(bot, BotRights(in_group=True, is_admin=True, can_pin=True, can_read_all=True))


@dataclass
class FakeOutbox:
    sent: list[Outgoing] = field(default_factory=list)
    _next: int = 5000

    async def send(self, o: Outgoing, group_id, thread_id=None) -> int:
        self.sent.append(o)
        self._next += 1
        return self._next


class FakeAudit:
    def __init__(self):
        self.events: list[tuple[str, dict]] = []

    def write(self, event: str, **fields) -> None:
        self.events.append((event, fields))


def ev(**kw) -> MessageEvent:
    base = dict(chat_id=-100, message_id=1, via_bot="labour_bot1", chat_type="group", sender_user_id=111,
                sender_is_bot=False, text="", mentions=(), reply_to_message_id=None, file=None, is_command=False,
                command=None, args=())
    base.update(kw)
    if base.get("command") and "is_command" not in kw:
        base["is_command"] = True
    return MessageEvent(**base)
