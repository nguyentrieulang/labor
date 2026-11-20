"""Kiểu dữ liệu dùng chung giữa core và adapter (LLD 5)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ChatType = Literal["private", "group", "supergroup", "channel"]


@dataclass(frozen=True)
class IncomingFile:
    name: str
    size: int
    tg_file_id: str


@dataclass(frozen=True)
class MessageEvent:
    chat_id: int
    message_id: int
    via_bot: str
    chat_type: ChatType
    sender_user_id: int | None
    sender_is_bot: bool
    text: str
    mentions: tuple[str, ...]
    reply_to_message_id: int | None
    file: IncomingFile | None
    is_command: bool
    command: str | None
    args: tuple[str, ...]
    command_target: str | None = None
    chat_title: str | None = None
    migrate_to_chat_id: int | None = None


@dataclass(frozen=True)
class User:
    id: int
    tg_user_id: int
    display_name: str
    is_admin: bool
    can_create_group: bool
    active: bool


@dataclass(frozen=True)
class Bot:
    id: int
    username: str
    token_env: str
    tg_bot_id: int | None
    can_read_all: bool | None


@dataclass(frozen=True)
class Group:
    id: int
    tg_chat_id: int
    title: str
    owner_user_id: int
    security_level: str
    workspace_path: Path
    system_bot_id: int
    allowed_providers: list[str] | None
    gemini_enabled: bool
    cli_turn_cap: int | None
    status: str


@dataclass(frozen=True)
class BotRights:
    in_group: bool
    is_admin: bool
    can_pin: bool
    can_read_all: bool


@dataclass(frozen=True)
class Outgoing:
    chat_id: int
    bot: str
    text: str
    template_code: str | None = None
    reply_to: int | None = None
    pin: bool = False


@dataclass(frozen=True)
class ReplyTarget:
    kind: Literal["pending_vai", "pending_chot", "dat_pin", "t10_error", "msg"]
    thread_id: int | None
    thread_status: str | None
    bot: str | None
    is_system: bool


IntentKind = Literal[
    "xac_nhan", "mo_lai", "dat", "chay_lai", "dung", "gan_skill",
    "doi_provider", "chot", "giao_vai", "sua_vai", "giao_viec", "khong",
]


@dataclass(frozen=True)
class Intent:
    kind: IntentKind
    bots: tuple[str, ...] = ()
    provider: str | None = None
    skill: str | None = None
    confirm_kind: Literal["vai", "chot"] | None = None


@dataclass(frozen=True)
class LogRow:
    sender_kind: str
    sender_id: int | None
    kind: str
    template_code: str | None
    thread_id: int | None


@dataclass(frozen=True)
class RoleView:
    bot: str
    role_name: str
    is_reviewer: bool
    provider: str
    skills: list[str]
    quote: str | None
