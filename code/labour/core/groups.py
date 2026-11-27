"""Đăng ký nhóm bằng /start (LLD 7.2) và tạo workspace (LLD 3.3)."""

from __future__ import annotations

from pathlib import Path

from labour.core.templates import render
from labour.core.text import slugify
from labour.ports.audit import Audit
from labour.ports.channel import ChannelAdapter
from labour.ports.models import BotRights, MessageEvent, Outgoing, User
from labour.ports.repo import Store

WORKSPACE_DIRS = ("input", "templates", "output", "review", "thao-luan", "decisions")
CHI_DAN = "# Chỉ dẫn nhóm\n"


class GroupService:
    def __init__(self, store: Store, channel: ChannelAdapter, audit: Audit, workspaces_dir: Path, data_dir: Path,
                 pool: list[str]):
        self.store, self.channel, self.audit = store, channel, audit
        self.workspaces_dir, self.data_dir, self.pool = Path(workspaces_dir), Path(data_dir), list(pool)

    def create_dirs(self, group_id: int, slug: str) -> Path:
        ws = self.workspaces_dir / f"{slug}-{group_id}"
        for d in WORKSPACE_DIRS:
            (ws / d).mkdir(parents=True, exist_ok=True)
        gdir = self.data_dir / "groups" / str(group_id)
        gdir.mkdir(parents=True, exist_ok=True)
        chi_dan = gdir / "chi-dan.md"
        if not chi_dan.exists():
            chi_dan.write_text(CHI_DAN, encoding="utf-8")
        return ws

    def _deny(self, e: MessageEvent, why: str) -> list[Outgoing]:
        self.audit.write("update_rejected", chat_id=e.chat_id, reason="start_denied", detail=why)
        return []

    async def register(self, e: MessageEvent, user: User | None) -> list[Outgoing]:
        if e.chat_type != "supergroup":  # 1.1b: nhóm thường không có số tin chung cho mọi bot
            return self._deny(e, "chat_type")
        if user is None or not user.can_create_group:
            return self._deny(e, "no_permission")
        if e.command_target is not None and e.command_target not in self.pool:
            return self._deny(e, "foreign_bot")
        with self.store.read() as s:
            if self.store.groups.by_chat(s, e.chat_id) is not None:
                return self._deny(e, "already_registered")
        rights = await self._all_rights(e.chat_id)
        system_bot = e.command_target or self._pick_system_bot(rights) or e.via_bot

        async with self.store.write() as s:
            if self.store.groups.by_chat(s, e.chat_id) is not None:
                return self._deny(e, "already_registered")
            bot = self.store.bots.by_username(s, system_bot)
            if bot is None:
                return self._deny(e, "unknown_bot")
            g = self.store.groups.create(s, e.chat_id, e.chat_title or "nhom", user.id, "", bot.id)
            ws = self.create_dirs(g.id, slugify(e.chat_title or "nhom"))
            self.store.groups.set_workspace(s, g.id, ws)
            self.store.members.add(s, g.id, user.id, "chu")
        self.audit.write("group_registered", group_id=g.id, chat_id=e.chat_id, owner_user_id=user.id,
                         system_bot=system_bot)

        out = [Outgoing(e.chat_id, system_bot, render("S_REGISTERED", workspace=ws), "S_REGISTERED", e.message_id)]
        problems = self._rights_problems(rights, system_bot)
        if problems:
            out.append(Outgoing(e.chat_id, system_bot, render("S_BOT_RIGHTS", details="; ".join(problems)),
                                "S_BOT_RIGHTS"))
        return out

    async def _all_rights(self, chat_id: int) -> dict[str, BotRights | None]:
        rights: dict[str, BotRights | None] = {}
        for b in self.pool:
            try:
                rights[b] = await self.channel.bot_rights(chat_id, b)
            except Exception:  # noqa: BLE001 – lỗi mạng không được chặn việc đăng ký
                rights[b] = None
        return rights

    def _pick_system_bot(self, rights: dict[str, BotRights | None]) -> str | None:
        """/start không kèm tên bot: bot đầu tiên (theo thứ tự config) là admin có quyền ghim, rồi bot đầu tiên có trong nhóm."""
        for ok in (lambda r: r.is_admin and r.can_pin, lambda r: r.in_group):
            for b in self.pool:
                r = rights.get(b)
                if r is not None and ok(r):
                    return b
        return None

    def _rights_problems(self, rights: dict[str, BotRights | None], system_bot: str) -> list[str]:
        problems = []
        for b in self.pool:
            r = rights.get(b)
            if r is None:
                problems.append(f"@{b}: không kiểm được quyền")
                continue
            if b == system_bot:
                if not r.is_admin:
                    problems.append(f"@{b}: bot hệ thống cần là admin")
                elif not r.can_pin:
                    problems.append(f"@{b}: bot hệ thống cần quyền ghim tin")
            elif r.in_group and not r.can_read_all and not r.is_admin:
                problems.append(f"@{b}: cần tắt privacy mode hoặc là admin")
        return problems
