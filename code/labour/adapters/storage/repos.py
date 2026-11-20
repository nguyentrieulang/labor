"""Store (một khoá ghi – LLD 4) và repository theo bảng."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.orm import Session

from labour.adapters.storage.models import (
    BotRow, GroupLogRow, GroupMemberRow, GroupRow, PendingConfirmationRow, PinRow,
    ProcessedUpdateRow, RoleAssignmentRow, RoleSkillRow, SkillRow, ThreadRow, TurnRow, UserRow,
)
from labour.ports.models import Bot, Group, LogRow, RoleView, User
from labour.ports.repo import BotSeed, UserSeed

VN = timedelta(hours=7)


def _iso(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _user(r: UserRow) -> User:
    return User(r.id, r.tg_user_id, r.display_name or "", r.is_admin, r.can_create_group, r.active)


def _bot(r: BotRow) -> Bot:
    return Bot(r.id, r.username, r.token_env, r.tg_bot_id, r.can_read_all)


def _group(r: GroupRow) -> Group:
    return Group(r.id, r.tg_chat_id, r.title or "", r.owner_user_id, r.security_level, Path(r.workspace_path),
                 r.system_bot_id, r.allowed_providers, r.gemini_enabled, r.cli_turn_cap, r.status)


class UsersRepo:
    def sync_from_config(self, s: Session, cfgs: list[UserSeed]) -> None:
        wanted = {c.tg_user_id: c for c in cfgs}
        for row in s.scalars(sa.select(UserRow)):
            c = wanted.pop(row.tg_user_id, None)
            if c is None:
                row.active = False
            else:
                row.display_name, row.is_admin, row.can_create_group, row.active = c.name, c.admin, c.can_create_group, True
        for c in wanted.values():
            s.add(UserRow(tg_user_id=c.tg_user_id, display_name=c.name, is_admin=c.admin,
                          can_create_group=c.can_create_group, active=True))
        s.flush()

    def by_tg(self, s: Session, tg_user_id: int | None) -> User | None:
        if tg_user_id is None:
            return None
        r = s.scalar(sa.select(UserRow).where(UserRow.tg_user_id == tg_user_id, UserRow.active.is_(True)))
        return _user(r) if r else None

    def by_id(self, s: Session, id: int) -> User | None:
        r = s.get(UserRow, id)
        return _user(r) if r else None


class BotsRepo:
    def sync_from_config(self, s: Session, cfgs: list[BotSeed]) -> None:
        existing = {r.username: r for r in s.scalars(sa.select(BotRow))}
        for c in cfgs:
            if c.username in existing:
                existing[c.username].token_env = c.token_env
            else:
                s.add(BotRow(username=c.username, token_env=c.token_env))
        s.flush()

    def by_username(self, s: Session, u: str) -> Bot | None:
        r = s.scalar(sa.select(BotRow).where(BotRow.username == u.lower()))
        return _bot(r) if r else None

    def by_id(self, s: Session, id: int) -> Bot:
        return _bot(s.get_one(BotRow, id))

    def all(self, s: Session) -> list[Bot]:
        return [_bot(r) for r in s.scalars(sa.select(BotRow).order_by(BotRow.id))]

    def set_identity(self, s: Session, username: str, tg_bot_id: int, can_read_all: bool) -> None:
        r = s.scalar(sa.select(BotRow).where(BotRow.username == username))
        if r:
            r.tg_bot_id, r.can_read_all = tg_bot_id, can_read_all


class GroupsRepo:
    def by_chat(self, s: Session, chat_id: int) -> Group | None:
        r = s.scalar(sa.select(GroupRow).where(GroupRow.tg_chat_id == chat_id))
        return _group(r) if r else None

    def by_id(self, s: Session, id: int) -> Group | None:
        r = s.get(GroupRow, id)
        return _group(r) if r else None

    def create(self, s: Session, tg_chat_id: int, title: str, owner_user_id: int,
               workspace_path: Path | str, system_bot_id: int) -> Group:
        r = GroupRow(tg_chat_id=tg_chat_id, title=title, owner_user_id=owner_user_id, security_level="noi_bo",
                     workspace_path=str(workspace_path), system_bot_id=system_bot_id, gemini_enabled=False,
                     status="active")
        s.add(r)
        s.flush()
        return _group(r)

    def set_workspace(self, s: Session, group_id: int, path: Path | str) -> None:
        s.get_one(GroupRow, group_id).workspace_path = str(path)

    def set_security_level(self, s: Session, group_id: int, level: str) -> None:
        r = s.get_one(GroupRow, group_id)
        r.security_level = level
        if level == "noi_bo":
            r.gemini_enabled = False
        s.flush()

    def migrate_chat(self, s: Session, old_chat_id: int, new_chat_id: int) -> bool:
        r = s.scalar(sa.select(GroupRow).where(GroupRow.tg_chat_id == old_chat_id))
        if r is None:
            return False
        r.tg_chat_id = new_chat_id
        s.flush()
        return True

    def all_active(self, s: Session) -> list[Group]:
        return [_group(r) for r in s.scalars(sa.select(GroupRow).where(GroupRow.status == "active"))]


class MembersRepo:
    def ensure(self, s: Session, group_id: int, user_id: int) -> bool:
        r = s.get(GroupMemberRow, (group_id, user_id))
        if r is None:
            s.add(GroupMemberRow(group_id=group_id, user_id=user_id, role="thanh_vien"))
            s.flush()
            return True
        return r.role != "da_bo"

    def add(self, s: Session, group_id: int, user_id: int, role: str) -> None:
        s.add(GroupMemberRow(group_id=group_id, user_id=user_id, role=role))
        s.flush()

    def set_role(self, s: Session, group_id: int, user_id: int, role: str) -> None:
        r = s.get(GroupMemberRow, (group_id, user_id))
        if r is None:
            self.add(s, group_id, user_id, role)
        else:
            r.role = role
            s.flush()

    def role_of(self, s: Session, group_id: int, user_id: int) -> str | None:
        r = s.get(GroupMemberRow, (group_id, user_id))
        return r.role if r else None

    def groups_of(self, s: Session, user_id: int) -> list[int]:
        q = sa.select(GroupMemberRow.group_id).where(GroupMemberRow.user_id == user_id, GroupMemberRow.role != "da_bo")
        return list(s.scalars(q))


class ProcessedRepo:
    def insert_if_absent(self, s: Session, chat_id: int, message_id: int) -> bool:
        res = s.execute(sa.insert(ProcessedUpdateRow).prefix_with("OR IGNORE")
                        .values(chat_id=chat_id, message_id=message_id, created_at=_iso(datetime.now(UTC))))
        return res.rowcount == 1

    def purge_older_than(self, s: Session, days: int) -> int:
        cut = _iso(datetime.now(UTC) - timedelta(days=days))
        return s.execute(sa.delete(ProcessedUpdateRow).where(ProcessedUpdateRow.created_at < cut)).rowcount


class LogRepo:
    def add(self, s: Session, group_id: int, tg_msg_id: int, sender_kind: str, sender_id: int | None, kind: str,
            text: str, reply_to: int | None, thread_id: int | None = None, template_code: str | None = None) -> int:
        r = GroupLogRow(group_id=group_id, tg_msg_id=tg_msg_id, sender_kind=sender_kind, sender_id=sender_id,
                        kind=kind, text=text, reply_to_tg_msg_id=reply_to, thread_id=thread_id,
                        template_code=template_code)
        s.add(r)
        s.flush()
        return r.id

    def get(self, s: Session, group_id: int, tg_msg_id: int) -> LogRow | None:
        r = s.scalar(sa.select(GroupLogRow).where(GroupLogRow.group_id == group_id, GroupLogRow.tg_msg_id == tg_msg_id))
        return LogRow(r.sender_kind, r.sender_id, r.kind, r.template_code, r.thread_id) if r else None


class PendingRepo:
    def open_by_msg(self, s: Session, group_id: int, tg_msg_id: int) -> str | None:
        return s.scalar(sa.select(PendingConfirmationRow.kind).where(
            PendingConfirmationRow.group_id == group_id, PendingConfirmationRow.tg_msg_id == tg_msg_id,
            PendingConfirmationRow.status == "cho"))


class PinsRepo:
    def get(self, s: Session, group_id: int, kind: str) -> int | None:
        r = s.get(PinRow, (group_id, kind))
        return r.tg_msg_id if r else None


class ThreadsRepo:
    def status_of(self, s: Session, thread_id: int | None) -> str | None:
        if thread_id is None:
            return None
        r = s.get(ThreadRow, thread_id)
        return r.status if r else None

    def open_count(self, s: Session, group_id: int) -> int:
        return s.scalar(sa.select(sa.func.count()).select_from(ThreadRow).where(
            ThreadRow.group_id == group_id, ThreadRow.status.in_(("dang_lam", "cho_nguoi")))) or 0


class RolesRepo:
    def _views(self, s: Session, where) -> list[tuple[int, RoleView]]:
        q = (sa.select(RoleAssignmentRow, BotRow.username)
             .join(BotRow, BotRow.id == RoleAssignmentRow.bot_id)
             .where(RoleAssignmentRow.status == "hieu_luc", where)
             .order_by(RoleAssignmentRow.group_id, RoleAssignmentRow.id))
        out = []
        for ra, username in s.execute(q):
            skills = list(s.scalars(sa.select(SkillRow.name).join(RoleSkillRow, RoleSkillRow.skill_id == SkillRow.id)
                                    .where(RoleSkillRow.role_assignment_id == ra.id).order_by(SkillRow.name)))
            out.append((ra.group_id, RoleView(username, ra.role_name, ra.is_reviewer, ra.provider, skills, ra.quote)))
        return out

    def active_for_group(self, s: Session, group_id: int) -> list[RoleView]:
        return [v for _, v in self._views(s, RoleAssignmentRow.group_id == group_id)]

    def has_active_role(self, s: Session, group_id: int, bot_username: str) -> bool:
        return any(v.bot == bot_username for v in self.active_for_group(s, group_id))

    def active_for_bot(self, s: Session, bot_username: str, group_ids: list[int]) -> list[tuple[str, RoleView]]:
        rows = self._views(s, RoleAssignmentRow.group_id.in_(group_ids))
        titles = {gid: t for gid, t in s.execute(sa.select(GroupRow.id, GroupRow.title).where(GroupRow.id.in_(group_ids)))}
        return [(titles.get(gid) or "", v) for gid, v in rows if v.bot == bot_username]


class TurnsRepo:
    def counts(self, s: Session, group_id: int) -> dict[str, int]:
        q = sa.select(TurnRow.status, sa.func.count()).where(TurnRow.group_id == group_id).group_by(TurnRow.status)
        return {st: n for st, n in s.execute(q).tuples()}

    def cost_today(self, s: Session, group_id: int) -> float:
        now_vn = datetime.now(UTC) + VN
        start = datetime(now_vn.year, now_vn.month, now_vn.day, tzinfo=UTC) - VN
        q = sa.select(sa.func.coalesce(sa.func.sum(TurnRow.cost_usd), 0.0)).where(
            TurnRow.group_id == group_id, TurnRow.finished_at >= _iso(start))
        return float(s.scalar(q) or 0.0)


class SkillsRepo:
    def usable(self, s: Session, level: str) -> list[tuple[str, str]]:
        rows = s.scalars(sa.select(SkillRow).where(SkillRow.status == "da_duyet").order_by(SkillRow.name))
        return [(r.name, r.version) for r in rows if level in (r.levels or [])]


class Store:
    def __init__(self, engine: sa.Engine):
        self.engine = engine
        self._lock = asyncio.Lock()
        self.users, self.bots, self.groups, self.members = UsersRepo(), BotsRepo(), GroupsRepo(), MembersRepo()
        self.processed, self.log, self.pending, self.pins = ProcessedRepo(), LogRepo(), PendingRepo(), PinsRepo()
        self.threads, self.roles, self.turns, self.skills = ThreadsRepo(), RolesRepo(), TurnsRepo(), SkillsRepo()

    @asynccontextmanager
    async def write(self) -> AsyncIterator[Session]:
        async with self._lock:
            with Session(self.engine, expire_on_commit=False) as s, s.begin():
                yield s

    @contextmanager
    def read(self) -> Iterator[Session]:
        with Session(self.engine) as s:
            yield s
