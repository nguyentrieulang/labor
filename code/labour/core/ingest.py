"""Đường đi của một tin (LLD 7.1). Không await lượt AI; gửi tin chỉ sau khi transaction đã commit."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from labour.core.commands import Commands
from labour.core.groups import GroupService
from labour.core.intents import classify
from labour.core.outbox import PolicyViolation
from labour.core.templates import TEMPLATES, refusal
from labour.ports.audit import Audit
from labour.ports.models import Group, Intent, MessageEvent, Outgoing, ReplyTarget
from labour.ports.repo import Session, Store

Handler = Callable[[Group, int | None, MessageEvent, Intent], Awaitable[list[Outgoing]]]
Attacher = Callable[[Session, Group, MessageEvent, Intent], int | None]


def null_attacher(s: Session, group: Group, e: MessageEvent, intent: Intent) -> int | None:
    return None


class Ingest:
    def __init__(self, store: Store, audit: Audit, outbox: Any, groups: GroupService, commands: Commands,
                 attach: Attacher = null_attacher, handlers: dict[str, Handler] | None = None):
        self.store, self.audit, self.outbox = store, audit, outbox
        self.groups, self.commands, self.attach = groups, commands, attach
        self.handlers: dict[str, Handler] = handlers or {}

    async def _unhandled(self, group: Group, thread_id: int | None, e: MessageEvent, intent: Intent) -> list[Outgoing]:
        self.audit.write("intent_unhandled", group_id=group.id, kind=intent.kind)
        return []

    def _reject(self, e: MessageEvent, reason: str) -> None:
        self.audit.write("update_rejected", chat_id=e.chat_id, reason=reason)

    def resolve_reply(self, s: Session, group: Group, reply_to: int | None) -> ReplyTarget | None:
        if reply_to is None:
            return None
        st = self.store
        row = st.log.get(s, group.id, reply_to)
        thread_id = row.thread_id if row else None
        bot = is_system = None
        if row and row.sender_kind == "bot" and row.sender_id is not None:
            bot = st.bots.by_id(s, row.sender_id).username
            is_system = row.sender_id == group.system_bot_id and row.kind == "template"
        pending = st.pending.open_by_msg(s, group.id, reply_to)
        if pending is not None:
            kind = "pending_vai" if pending == "vai" else "pending_chot"
        elif st.pins.get(s, group.id, "dat") == reply_to:
            kind = "dat_pin"
        elif row and row.template_code == "T10":
            kind = "t10_error"
        else:
            kind = "msg"
        return ReplyTarget(kind, thread_id, st.threads.status_of(s, thread_id), bot, bool(is_system))

    async def on_event(self, e: MessageEvent) -> None:
        st = self.store
        if e.migrate_to_chat_id is not None:
            async with st.write() as s:
                moved = st.groups.migrate_chat(s, e.chat_id, e.migrate_to_chat_id)
            if moved:
                self.audit.write("group_migrated", old_chat_id=e.chat_id, new_chat_id=e.migrate_to_chat_id)
            return
        if e.chat_type == "group":
            await self._basic_group(e)
            return

        action: tuple | None = None
        async with st.write() as s:
            if not st.processed.insert_if_absent(s, e.chat_id, e.message_id):
                return
            if e.sender_is_bot:
                return
            if e.is_command and e.command_target is not None and e.command_target not in self.groups.pool:
                self._reject(e, "foreign_bot")
                return
            user = st.users.by_tg(s, e.sender_user_id)
            if e.chat_type == "private":
                if user and user.is_admin and e.command == "skill":
                    action = ("skill",)
                else:
                    self._reject(e, "private")
                    return
            elif e.chat_type not in ("group", "supergroup"):
                self._reject(e, "chat_type")
                return
            else:
                group = st.groups.by_chat(s, e.chat_id)
                if e.command == "start":
                    action = ("start", user)
                elif user is None:
                    self._reject(e, "unknown_user")
                    return
                elif group is None:
                    self._reject(e, "unknown_group")
                    return
                elif not st.members.ensure(s, group.id, user.id):
                    self._reject(e, "removed_member")
                    return
                elif e.file is not None:
                    st.log.add(s, group.id, e.message_id, "user", user.id, "chat", e.text, e.reply_to_message_id)
                    action = ("file", group)
                elif e.is_command:
                    st.log.add(s, group.id, e.message_id, "user", user.id, "command", e.text, e.reply_to_message_id)
                    action = ("command", group, user)
                elif user.id != group.owner_user_id:
                    reply = self.resolve_reply(s, group, e.reply_to_message_id)
                    st.log.add(s, group.id, e.message_id, "user", user.id, "chat", e.text, e.reply_to_message_id,
                               thread_id=reply.thread_id if reply else None)
                    return
                else:
                    reply = self.resolve_reply(s, group, e.reply_to_message_id)
                    intent = classify(e.text, e.mentions, reply,
                                      lambda b: st.roles.has_active_role(s, group.id, b))
                    thread_id = self.attach(s, group, e, intent)
                    st.log.add(s, group.id, e.message_id, "user", user.id, "chat", e.text, e.reply_to_message_id,
                               thread_id=thread_id)
                    action = ("intent", group, thread_id, intent)

        await self._act(e, action)

    async def _basic_group(self, e: MessageEvent) -> None:
        """Nhóm thường: mỗi bot tự đánh số tin, nên không chống trùng theo message_id được (1.1b).
        Không xử lý, không ghi group_log. Chỉ một bot (bot được gọi, hoặc bot đầu tiên trong config) ghi audit
        và trả lời /start của người được tạo nhóm, để không ra 4 tin."""
        if e.sender_is_bot or e.via_bot != (e.command_target or self.groups.pool[0]):
            return
        self._reject(e, "basic_group")
        if e.command != "start":
            return
        with self.store.read() as s:
            user = self.store.users.by_tg(s, e.sender_user_id)
        if user is None or not user.can_create_group:
            return
        o = Outgoing(e.chat_id, e.via_bot, TEMPLATES["S_NEED_SUPERGROUP"], "S_NEED_SUPERGROUP", e.message_id)
        try:
            await self.outbox.send(o, None)
        except Exception as ex:  # noqa: BLE001
            self.audit.write("send_failed", group_id=None, template=o.template_code, error=type(ex).__name__)

    async def _act(self, e: MessageEvent, action: tuple | None) -> None:
        if action is None:
            return
        kind = action[0]
        group: Group | None = None
        if kind == "skill":
            out = [Outgoing(e.chat_id, e.via_bot, TEMPLATES["S_SKILL_LATER"], "S_SKILL_LATER", e.message_id)]
        elif kind == "start":
            out = await self.groups.register(e, action[1])
            if out:
                with self.store.read() as s:
                    group = self.store.groups.by_chat(s, e.chat_id)
        elif kind == "file":
            group = action[1]
            out = self._file(group, e)
        elif kind == "command":
            group = action[1]
            out = await self.commands.dispatch(group, action[2], e)
        else:
            _, group, thread_id, intent = action
            out = await self.handlers.get(intent.kind, self._unhandled)(group, thread_id, e, intent)
        gid = group.id if group else None
        for o in out:
            try:
                await self.outbox.send(o, gid)
            except PolicyViolation:
                self.audit.write("message_blocked", group_id=gid, template=o.template_code)
            except Exception as ex:  # noqa: BLE001 – một tin lỗi không được bỏ các tin sau
                self.audit.write("send_failed", group_id=gid, template=o.template_code, error=type(ex).__name__)

    def _file(self, group: Group, e: MessageEvent) -> list[Outgoing]:
        if group.security_level == "noi_bo":
            self.audit.write("file_rejected", group_id=group.id, size=e.file.size if e.file else None)
            with self.store.read() as s:
                bot = self.store.bots.by_id(s, group.system_bot_id).username
            return [Outgoing(e.chat_id, bot, refusal("noi_bo_khong_nhan_file"), "T13", e.message_id)]
        self.audit.write("file_pending", group_id=group.id)  # nhận file nhóm Thoải mái: P4
        return []
