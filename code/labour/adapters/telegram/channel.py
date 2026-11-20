"""ChannelAdapter trên aiogram 3: một Dispatcher, n Bot, long polling (LLD 12)."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import FSInputFile, Message, ReplyParameters

from labour.adapters.telegram.convert import to_event
from labour.ports.channel import RateLimited
from labour.ports.models import BotRights, IncomingFile, MessageEvent

log = logging.getLogger(__name__)

OnEvent = Callable[[MessageEvent], Awaitable[None]]


class TelegramChannel:
    def __init__(self, tokens: dict[str, str], poll_timeout_s: int):
        self.bots: dict[str, Bot] = {u.lower(): Bot(t) for u, t in tokens.items()}
        self.poll_timeout_s = poll_timeout_s
        self._ids: dict[str, tuple[int, bool]] = {}
        self._by_tg_id: dict[int, str] = {}

    async def identities(self) -> dict[str, tuple[int, bool]]:
        for username, bot in self.bots.items():
            me = await bot.get_me()
            if (me.username or "").lower() != username:
                log.warning("token của @%s thuộc bot @%s", username, me.username)
            self._ids[username] = (me.id, bool(me.can_read_all_group_messages))
            self._by_tg_id[me.id] = username
        return dict(self._ids)

    def _build_dispatcher(self, on_event: OnEvent) -> Dispatcher:
        dp = Dispatcher()
        pool = set(self.bots)

        @dp.message()
        async def _on_message(message: Message, bot: Bot) -> None:
            via = self._by_tg_id.get(bot.id) or next(u for u, b in self.bots.items() if b is bot)
            e = to_event(message, via, pool)
            if e is None:
                return
            try:
                await on_event(e)
            except Exception:
                log.exception("lỗi xử lý tin chat=%s msg=%s", e.chat_id, e.message_id)

        return dp

    async def start(self, on_event: OnEvent) -> None:
        if not self._ids:
            await self.identities()
        dp = self._build_dispatcher(on_event)
        await dp.start_polling(*self.bots.values(), polling_timeout=self.poll_timeout_s, handle_as_tasks=True,
                               allowed_updates=["message"])

    async def send_text(self, chat_id: int, bot: str, text: str, reply_to: int | None = None) -> int:
        rp = ReplyParameters(message_id=reply_to, allow_sending_without_reply=True) if reply_to else None
        try:
            m = await self.bots[bot].send_message(chat_id, text, reply_parameters=rp)
        except TelegramRetryAfter as e:
            raise RateLimited(float(e.retry_after)) from e
        return m.message_id

    async def edit_text(self, chat_id: int, bot: str, message_id: int, text: str) -> None:
        try:
            await self.bots[bot].edit_message_text(text=text, chat_id=chat_id, message_id=message_id)
        except TelegramRetryAfter as e:
            raise RateLimited(float(e.retry_after)) from e

    async def pin(self, chat_id: int, bot: str, message_id: int) -> None:
        await self.bots[bot].pin_chat_message(chat_id, message_id, disable_notification=True)

    async def unpin(self, chat_id: int, bot: str, message_id: int) -> None:
        await self.bots[bot].unpin_chat_message(chat_id, message_id=message_id)

    async def send_file(self, chat_id: int, bot: str, path: Path, caption: str) -> int:
        try:
            m = await self.bots[bot].send_document(chat_id, FSInputFile(path), caption=caption)
        except TelegramRetryAfter as e:
            raise RateLimited(float(e.retry_after)) from e
        return m.message_id

    async def download(self, bot: str, f: IncomingFile, dest: Path) -> None:
        await self.bots[bot].download(f.tg_file_id, destination=dest)

    async def bot_rights(self, chat_id: int, bot: str) -> BotRights:
        if bot not in self._ids:
            await self.identities()
        tg_id, can_read_all = self._ids[bot]
        cm = await self.bots[bot].get_chat_member(chat_id, tg_id)
        status = cm.status
        in_group = status not in ("left", "kicked")
        is_admin = status in ("administrator", "creator")
        can_pin = status == "creator" or bool(getattr(cm, "can_pin_messages", False))
        return BotRights(in_group=in_group, is_admin=is_admin, can_pin=can_pin, can_read_all=can_read_all)

    async def close(self) -> None:
        for b in self.bots.values():
            await b.session.close()
