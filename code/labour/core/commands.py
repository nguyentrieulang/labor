"""Lệnh trên chat và kiểm quyền từng lệnh (LLD 11)."""

from __future__ import annotations

from typing import Literal

from labour.core.templates import refusal, render
from labour.ports.audit import Audit
from labour.ports.models import Group, MessageEvent, Outgoing, RoleView, User
from labour.ports.repo import Store

PERMS: dict[str, Literal["owner", "member"]] = {
    "baomat": "owner", "gemini": "owner", "thanhvien": "owner",
    "vai": "member", "skills": "member", "status": "member",
}
LEVELS = ("noi_bo", "thoai_mai")


def _role_line(v: RoleView, prefix: str = "") -> str:
    reviewer = " (reviewer)" if v.is_reviewer else ""
    skills = ", ".join(v.skills) or "không"
    return f"{prefix}@{v.bot} – [{v.role_name}]{reviewer} – {v.provider} – skill: {skills} – lời giao: “{v.quote or ''}”"


class Commands:
    def __init__(self, store: Store, audit: Audit):
        self.store, self.audit = store, audit

    async def dispatch(self, group: Group, user: User, e: MessageEvent) -> list[Outgoing]:
        cmd = e.command or ""
        perm = PERMS.get(cmd)
        if perm is None:
            return []
        with self.store.read() as s:
            system_bot = self.store.bots.by_id(s, group.system_bot_id).username

        def say(code: str, text: str) -> list[Outgoing]:
            return [Outgoing(e.chat_id, system_bot, text, code, e.message_id)]

        if perm == "owner" and user.id != group.owner_user_id:
            return say("T13", refusal("chi_chu_nhom"))
        code, text = await getattr(self, f"_{cmd}")(group, user, e)
        return say(code, text)

    async def _baomat(self, group: Group, user: User, e: MessageEvent) -> tuple[str, str]:
        level = e.args[0].lower() if e.args else None
        if level not in LEVELS:
            return "S_LEVEL", render("S_LEVEL", level=group.security_level)
        async with self.store.write() as s:
            self.store.groups.set_security_level(s, group.id, level)
        self.audit.write("security_level_changed", group_id=group.id, old=group.security_level, new=level,
                         by_user_id=user.id)
        return "S_LEVEL", render("S_LEVEL", level=level)

    async def _gemini(self, group: Group, user: User, e: MessageEvent) -> tuple[str, str]:
        if group.security_level == "noi_bo":
            return "T13", refusal("chi_trong_thoai_mai")
        return "T13", refusal("provider_chua_ho_tro")

    async def _thanhvien(self, group: Group, user: User, e: MessageEvent) -> tuple[str, str]:
        action = e.args[0].lower() if e.args else None
        hint = "S_MEMBER", render("S_MEMBER", name="?", role="reply vào tin của người đó rồi gõ /thanhvien them | bo")
        if action == "bot":
            action = "bo"
        if action not in ("them", "bo") or e.reply_to_message_id is None:
            return hint
        async with self.store.write() as s:
            row = self.store.log.get(s, group.id, e.reply_to_message_id)
            target = self.store.users.by_id(s, row.sender_id) if row and row.sender_kind == "user" and row.sender_id else None
            if target is None or not target.active:
                return hint
            if target.id == group.owner_user_id:
                return "S_MEMBER", render("S_MEMBER", name=target.display_name, role="chủ nhóm – không đổi")
            role = "thanh_vien" if action == "them" else "da_bo"
            self.store.members.set_role(s, group.id, target.id, role)
        self.audit.write("member_added" if action == "them" else "member_removed", group_id=group.id,
                         user_id=target.id, by_user_id=user.id)
        return "S_MEMBER", render("S_MEMBER", name=target.display_name,
                                  role="thành viên" if action == "them" else "đã bỏ khỏi nhóm")

    async def _vai(self, group: Group, user: User, e: MessageEvent) -> tuple[str, str]:
        bot = next((a.lstrip("@").lower() for a in e.args if a.startswith("@")), None)
        all_groups = any(a.lower() == "tatca" for a in e.args)
        with self.store.read() as s:
            if all_groups:
                gids = self.store.members.groups_of(s, user.id)
                bots = [bot] if bot else sorted({v.bot for gid in gids for v in self.store.roles.active_for_group(s, gid)})
                lines = [_role_line(v, f"{title}: ") for b in bots for title, v in self.store.roles.active_for_bot(s, b, gids)]
            else:
                lines = [_role_line(v) for v in self.store.roles.active_for_group(s, group.id) if bot in (None, v.bot)]
        if not lines:
            return "S_NO_ROLE", render("S_NO_ROLE")
        return "S_ROLES", render("S_ROLES", lines="\n".join(lines))

    async def _skills(self, group: Group, user: User, e: MessageEvent) -> tuple[str, str]:
        with self.store.read() as s:
            usable = self.store.skills.usable(s, group.security_level)
            roles = self.store.roles.active_for_group(s, group.id)
        lines = []
        if usable:
            lines.append("Dùng được: " + ", ".join(f"{n}@{v}" for n, v in usable))
        lines += [f"@{r.bot}: {', '.join(r.skills)}" for r in roles if r.skills]
        if not lines:
            return "S_NO_SKILL", render("S_NO_SKILL")
        return "S_SKILLS", render("S_SKILLS", lines="\n".join(lines))

    async def _status(self, group: Group, user: User, e: MessageEvent) -> tuple[str, str]:
        with self.store.read() as s:
            n = self.store.threads.open_count(s, group.id)
            c = self.store.turns.counts(s, group.id)
            cost = self.store.turns.cost_today(s, group.id)
        return "S_STATUS", render("S_STATUS", n=n, cho=c.get("cho", 0), dang_chay=c.get("dang_chay", 0),
                                  cost=f"{cost:.2f}")
