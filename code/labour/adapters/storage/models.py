"""Lược đồ CSDL – LLD 4.1 (16 bảng) và 4.2 (chỉ mục)."""

from __future__ import annotations

from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NOW_SQL = sa.text("(strftime('%Y-%m-%dT%H:%M:%SZ','now'))")


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _in(col: str, *values: str, nullable: bool = False) -> sa.CheckConstraint:
    vals = ",".join(f"'{v}'" for v in values)
    cond = f"{col} IN ({vals})"
    if nullable:
        cond = f"{col} IS NULL OR {cond}"
    return sa.CheckConstraint(cond, name=col)


class Base(DeclarativeBase):
    metadata = sa.MetaData(naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_N_name)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


class _Created:
    created_at: Mapped[str] = mapped_column(sa.Text, server_default=NOW_SQL, default=now_iso)


class _Updated(_Created):
    updated_at: Mapped[str] = mapped_column(sa.Text, server_default=NOW_SQL, default=now_iso, onupdate=now_iso)


class UserRow(_Created, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_user_id: Mapped[int] = mapped_column(sa.BigInteger, unique=True)
    display_name: Mapped[str | None] = mapped_column(sa.Text)
    is_admin: Mapped[bool] = mapped_column(default=False)
    can_create_group: Mapped[bool] = mapped_column(default=False)
    active: Mapped[bool] = mapped_column(default=True)


class BotRow(_Created, Base):
    __tablename__ = "bots"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.Text, unique=True)
    token_env: Mapped[str] = mapped_column(sa.Text)
    tg_bot_id: Mapped[int | None] = mapped_column(sa.BigInteger)
    can_read_all: Mapped[bool | None] = mapped_column()


class GroupRow(_Updated, Base):
    __tablename__ = "groups"
    __table_args__ = (_in("security_level", "noi_bo", "thoai_mai"), _in("status", "active", "archived"))
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_chat_id: Mapped[int] = mapped_column(sa.BigInteger, unique=True)
    title: Mapped[str | None] = mapped_column(sa.Text)
    owner_user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"))
    security_level: Mapped[str] = mapped_column(sa.Text, default="noi_bo")
    workspace_path: Mapped[str] = mapped_column(sa.Text)
    system_bot_id: Mapped[int] = mapped_column(sa.ForeignKey("bots.id"))
    allowed_providers: Mapped[list | None] = mapped_column(sa.JSON)
    gemini_enabled: Mapped[bool] = mapped_column(default=False)
    cli_turn_cap: Mapped[int | None] = mapped_column()
    status: Mapped[str] = mapped_column(sa.Text, default="active")


class GroupMemberRow(_Created, Base):
    __tablename__ = "group_members"
    __table_args__ = (
        _in("role", "chu", "thanh_vien", "da_bo"),
        sa.Index("ix_one_owner", "group_id", unique=True, sqlite_where=sa.text("role = 'chu'")),
    )
    group_id: Mapped[int] = mapped_column(sa.ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"), primary_key=True)
    role: Mapped[str] = mapped_column(sa.Text)
    joined_at: Mapped[str] = mapped_column(sa.Text, server_default=NOW_SQL, default=now_iso)


class RoleAssignmentRow(_Updated, Base):
    __tablename__ = "role_assignments"
    __table_args__ = (
        _in("provider", "claude", "grok", "gemini"),
        _in("status", "cho_xac_nhan", "hieu_luc", "thay_the"),
        sa.CheckConstraint("quote IS NULL OR length(quote) <= 300", name="quote_len"),
        sa.Index("ix_one_active_role", "group_id", "bot_id", unique=True, sqlite_where=sa.text("status = 'hieu_luc'")),
        sa.Index("ix_role_assignments_group_status", "group_id", "status"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(sa.ForeignKey("groups.id"))
    bot_id: Mapped[int] = mapped_column(sa.ForeignKey("bots.id"))
    role_name: Mapped[str] = mapped_column(sa.Text)
    instructions: Mapped[str] = mapped_column(sa.Text)
    source_text: Mapped[str] = mapped_column(sa.Text)
    source_tg_msg_id: Mapped[int | None] = mapped_column(sa.BigInteger)
    quote: Mapped[str | None] = mapped_column(sa.Text)
    provider: Mapped[str] = mapped_column(sa.Text, default="claude")
    is_reviewer: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(sa.Text)
    version: Mapped[int] = mapped_column(default=1)


class SkillRow(_Updated, Base):
    __tablename__ = "skills"
    __table_args__ = (sa.UniqueConstraint("name", "version"), _in("status", "cho_duyet", "da_duyet", "ngung"))
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.Text)
    version: Mapped[str] = mapped_column(sa.Text)
    description: Mapped[str | None] = mapped_column(sa.Text)
    levels: Mapped[list] = mapped_column(sa.JSON, default=list)
    tools: Mapped[list] = mapped_column(sa.JSON, default=list)
    status: Mapped[str] = mapped_column(sa.Text, default="cho_duyet")
    path: Mapped[str] = mapped_column(sa.Text)
    sha256: Mapped[str | None] = mapped_column(sa.Text)
    check_report: Mapped[dict | None] = mapped_column(sa.JSON)
    approved_by: Mapped[int | None] = mapped_column(sa.ForeignKey("users.id"))
    approved_at: Mapped[str | None] = mapped_column(sa.Text)


class RoleSkillRow(_Created, Base):
    __tablename__ = "role_skills"
    role_assignment_id: Mapped[int] = mapped_column(sa.ForeignKey("role_assignments.id"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(sa.ForeignKey("skills.id"), primary_key=True)


class AgentSessionRow(_Created, Base):
    __tablename__ = "agent_sessions"
    group_id: Mapped[int] = mapped_column(sa.ForeignKey("groups.id"), primary_key=True)
    bot_id: Mapped[int] = mapped_column(sa.ForeignKey("bots.id"), primary_key=True)
    provider: Mapped[str] = mapped_column(sa.Text)
    session_id: Mapped[str] = mapped_column(sa.Text)
    fingerprint: Mapped[str] = mapped_column(sa.Text)
    last_used_at: Mapped[str] = mapped_column(sa.Text, default=now_iso)


class ThreadRow(_Updated, Base):
    __tablename__ = "threads"
    __table_args__ = (
        _in("status", "dang_lam", "cho_nguoi", "dat", "huy"),
        _in("wait_reason", "ask_cap", "review_cap", "cli_cap", "escalate", "no_reviewer", "error", nullable=True),
        _in("closed_reason", "thay_the", "chu_dung", nullable=True),
        sa.Index("ix_threads_group_status", "group_id", "status"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(sa.ForeignKey("groups.id"))
    root_tg_msg_id: Mapped[int] = mapped_column(sa.BigInteger)
    status: Mapped[str] = mapped_column(sa.Text, default="dang_lam")
    wait_reason: Mapped[str | None] = mapped_column(sa.Text)
    waiting_bot_id: Mapped[int | None] = mapped_column(sa.ForeignKey("bots.id"))
    closed_reason: Mapped[str | None] = mapped_column(sa.Text)
    ask_count: Mapped[int] = mapped_column(default=0)
    review_round: Mapped[int] = mapped_column(default=0)
    cli_turns: Mapped[int] = mapped_column(default=0)
    cli_turn_cap: Mapped[int] = mapped_column()
    dat_tg_msg_id: Mapped[int | None] = mapped_column(sa.BigInteger)
    approved_by: Mapped[str | None] = mapped_column(sa.Text)


class TurnRow(_Updated, Base):
    __tablename__ = "turns"
    __table_args__ = (
        _in("kind", "thuong", "ask", "tra_loi_ask", "review", "sua", "chot", "dien_giai_vai"),
        _in("status", "cho", "dang_chay", "xong", "loi", "huy"),
        sa.Index("ix_turns_sched", "status", "group_id", "queued_at"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    thread_id: Mapped[int | None] = mapped_column(sa.ForeignKey("threads.id"))
    group_id: Mapped[int] = mapped_column(sa.ForeignKey("groups.id"))
    bot_id: Mapped[int] = mapped_column(sa.ForeignKey("bots.id"))
    kind: Mapped[str] = mapped_column(sa.Text)
    status: Mapped[str] = mapped_column(sa.Text, default="cho")
    parent_turn_id: Mapped[int | None] = mapped_column(sa.ForeignKey("turns.id"))
    trigger_tg_msg_id: Mapped[int | None] = mapped_column(sa.BigInteger)
    input_text: Mapped[str | None] = mapped_column(sa.Text)
    pid: Mapped[int | None] = mapped_column()
    signal: Mapped[dict | None] = mapped_column(sa.JSON)
    files_changed: Mapped[list | None] = mapped_column(sa.JSON)
    error_code: Mapped[str | None] = mapped_column(sa.Text)
    cost_usd: Mapped[float | None] = mapped_column()
    num_turns: Mapped[int | None] = mapped_column()
    duration_ms: Mapped[int | None] = mapped_column()
    queued_at: Mapped[str] = mapped_column(sa.Text, default=now_iso)
    started_at: Mapped[str | None] = mapped_column(sa.Text)
    finished_at: Mapped[str | None] = mapped_column(sa.Text)


class ReviewRow(_Updated, Base):
    __tablename__ = "reviews"
    __table_args__ = (sa.UniqueConstraint("thread_id", "round"), _in("verdict", "dat", "chua_dat", nullable=True))
    id: Mapped[int] = mapped_column(primary_key=True)
    thread_id: Mapped[int] = mapped_column(sa.ForeignKey("threads.id"))
    round: Mapped[int] = mapped_column()
    files: Mapped[list] = mapped_column(sa.JSON)
    author_bot_id: Mapped[int] = mapped_column(sa.ForeignKey("bots.id"))
    reviewer_bot_id: Mapped[int | None] = mapped_column(sa.ForeignKey("bots.id"))
    verdict: Mapped[str | None] = mapped_column(sa.Text)
    notes_path: Mapped[str | None] = mapped_column(sa.Text)


class DecisionVersionRow(_Created, Base):
    __tablename__ = "decision_versions"
    __table_args__ = (sa.UniqueConstraint("group_id", "version"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(sa.ForeignKey("groups.id"))
    version: Mapped[int] = mapped_column()
    sha256: Mapped[str] = mapped_column(sa.Text)
    original_path: Mapped[str] = mapped_column(sa.Text)
    source_path: Mapped[str] = mapped_column(sa.Text)
    confirmed_by: Mapped[int | None] = mapped_column(sa.ForeignKey("users.id"))
    confirm_tg_msg_id: Mapped[int | None] = mapped_column(sa.BigInteger)


class GroupLogRow(_Created, Base):
    __tablename__ = "group_log"
    __table_args__ = (
        _in("sender_kind", "user", "bot", "system"),
        _in("kind", "chat", "template", "command"),
        sa.Index("ix_group_log_msg", "group_id", "tg_msg_id", unique=True),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(sa.ForeignKey("groups.id"))
    thread_id: Mapped[int | None] = mapped_column(sa.ForeignKey("threads.id"))
    tg_msg_id: Mapped[int] = mapped_column(sa.BigInteger)
    sender_kind: Mapped[str] = mapped_column(sa.Text)
    sender_id: Mapped[int | None] = mapped_column()
    kind: Mapped[str] = mapped_column(sa.Text)
    text: Mapped[str] = mapped_column(sa.Text, default="")
    reply_to_tg_msg_id: Mapped[int | None] = mapped_column(sa.BigInteger)
    template_code: Mapped[str | None] = mapped_column(sa.Text)


class PendingConfirmationRow(_Updated, Base):
    __tablename__ = "pending_confirmations"
    __table_args__ = (
        _in("kind", "vai", "chot"),
        _in("status", "cho", "da_xac_nhan", "het_han", "thay_the"),
        sa.Index("ix_pending_group_msg", "group_id", "tg_msg_id"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(sa.ForeignKey("groups.id"))
    kind: Mapped[str] = mapped_column(sa.Text)
    tg_msg_id: Mapped[int] = mapped_column(sa.BigInteger)
    payload: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    status: Mapped[str] = mapped_column(sa.Text, default="cho")
    expires_at: Mapped[str] = mapped_column(sa.Text)


class ProcessedUpdateRow(_Created, Base):
    __tablename__ = "processed_updates"
    chat_id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True)
    message_id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True)


class PinRow(_Created, Base):
    __tablename__ = "pins"
    __table_args__ = (_in("kind", "vai", "dat"),)
    group_id: Mapped[int] = mapped_column(sa.ForeignKey("groups.id"), primary_key=True)
    kind: Mapped[str] = mapped_column(sa.Text, primary_key=True)
    tg_msg_id: Mapped[int] = mapped_column(sa.BigInteger)
    bot_id: Mapped[int] = mapped_column(sa.ForeignKey("bots.id"))
