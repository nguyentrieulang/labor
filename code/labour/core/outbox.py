"""Hàng tin ra (LLD 12). Lớp chặn cuối của nhóm Nội bộ: chỉ gửi tin có mã mẫu (LLD 8.1, AD-14)."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable

from labour.core.templates import TEMPLATES
from labour.ports.channel import ChannelAdapter, RateLimited
from labour.ports.models import Outgoing
from labour.ports.repo import Store

TG_MAX = 4096
MAX_RETRIES = 3


class PolicyViolation(Exception):
    pass


def split_text(text: str, limit: int = TG_MAX) -> list[str]:
    parts: list[str] = []
    cur = ""
    for para in text.split("\n\n"):
        while len(para) > limit:
            if cur:
                parts.append(cur)
                cur = ""
            parts.append(para[:limit])
            para = para[limit:]
        cand = f"{cur}\n\n{para}" if cur else para
        if len(cand) <= limit:
            cur = cand
        else:
            parts.append(cur)
            cur = para
    if cur:
        parts.append(cur)
    return parts or [""]


class Outbox:
    def __init__(self, channel: ChannelAdapter, store: Store, min_interval_s: float,
                 clock: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], Awaitable[None]] = asyncio.sleep):
        self.channel, self.store, self.min_interval_s = channel, store, min_interval_s
        self.clock, self.sleep = clock, sleep
        self._locks: dict[int, asyncio.Lock] = {}
        self._last: dict[int, float] = {}

    def _check_policy(self, o: Outgoing, group_id: int | None) -> None:
        if group_id is None:
            return
        with self.store.read() as s:
            g = self.store.groups.by_id(s, group_id)
        if g is not None and g.security_level == "noi_bo" and o.template_code not in TEMPLATES:
            raise PolicyViolation(f"nhóm Nội bộ {group_id}: tin không có mã mẫu hợp lệ ({o.template_code!r})")

    async def _send_one(self, o: Outgoing, text: str, reply_to: int | None) -> int:
        last = self._last.get(o.chat_id)
        if last is not None:
            wait = self.min_interval_s - (self.clock() - last)
            if wait > 0:
                await self.sleep(wait)
        for attempt in range(MAX_RETRIES + 1):
            try:
                mid = await self.channel.send_text(o.chat_id, o.bot, text, reply_to)
                break
            except RateLimited as e:
                if attempt == MAX_RETRIES:
                    raise
                await self.sleep(e.retry_after)
        self._last[o.chat_id] = self.clock()
        return mid

    async def send(self, o: Outgoing, group_id: int | None, thread_id: int | None = None) -> int:
        """Tin dài hơn TG_MAX được chia theo đoạn; khoá chat giữ suốt mọi phần để tin khác không chen vào giữa."""
        self._check_policy(o, group_id)
        parts = split_text(o.text) if len(o.text) > TG_MAX else [o.text]
        mid = 0
        async with self._locks.setdefault(o.chat_id, asyncio.Lock()):
            for i, part in enumerate(parts):
                mid = await self._send_one(o, part, o.reply_to if i == 0 else None)
                if group_id is not None:
                    async with self.store.write() as s:
                        bot = self.store.bots.by_username(s, o.bot)
                        self.store.log.add(s, group_id, mid, "bot", bot.id if bot else None,
                                           "template" if o.template_code else "chat", part,
                                           o.reply_to if i == 0 else None, thread_id=thread_id,
                                           template_code=o.template_code)
            if o.pin:
                await self.channel.pin(o.chat_id, o.bot, mid)
        return mid
