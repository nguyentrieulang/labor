"""Đọc config.yaml + biến môi trường (LLD 3.1)."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator


class ConfigError(Exception):
    pass


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class BotCfg(_Frozen):
    username: str
    token_env: str

    @field_validator("username")
    @classmethod
    def _lower(cls, v: str) -> str:
        return v.strip().lstrip("@").lower()


class UserCfg(_Frozen):
    tg_user_id: int
    name: str
    admin: bool = False
    can_create_group: bool = False


class Limits(_Frozen):
    max_concurrent_turns: int = 3
    turn_timeout_s: int = 900
    ask_cap: int = 3
    review_cap: int = 3
    cli_turn_cap_default: int = 12
    file_in_max_mb: int = 20
    outbox_min_interval_s: float = 3.0


class ClaudeCfg(_Frozen):
    exe: Path
    pinned_version: str
    model_default: str
    model_light: str
    max_agent_turns: int


class AppConfig(_Frozen):
    data_dir: Path
    workspaces_dir: Path
    bots: list[BotCfg]
    poll_timeout_s: int
    users: list[UserCfg]
    limits: Limits
    claude: ClaudeCfg
    providers: dict[str, list[str]]


_ENV_VAR = re.compile(r"%([A-Za-z_][A-Za-z0-9_]*)%")


def _expand(s: str, env: Mapping[str, str]) -> str:
    def sub(m: re.Match[str]) -> str:
        name = m.group(1)
        if name not in env:
            raise ConfigError(f"thiếu biến môi trường {name} (dùng trong claude.exe)")
        return env[name]

    return _ENV_VAR.sub(sub, s)


def load_config(path: Path, env: Mapping[str, str]) -> AppConfig:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as e:
        raise ConfigError(f"không đọc được {path}: {e}") from e
    try:
        inst, tg, claude = raw["instance"], raw["telegram"], dict(raw["claude"])
        claude["exe"] = _expand(str(claude["exe"]), env)
        cfg = AppConfig(
            data_dir=inst["data_dir"],
            workspaces_dir=inst["workspaces_dir"],
            bots=tg["bots"],
            poll_timeout_s=tg.get("poll_timeout_s", 30),
            users=raw["users"],
            limits=raw.get("limits") or {},
            claude=claude,
            providers=raw["providers"],
        )
    except (KeyError, TypeError) as e:
        raise ConfigError(f"thiếu khoá bắt buộc trong {path}: {e}") from e
    except ValidationError as e:
        raise ConfigError(f"cấu hình sai trong {path}: {e}") from e

    seen: set[str] = set()
    for b in cfg.bots:
        if b.username in seen:
            raise ConfigError(f"username bot trùng: {b.username}")
        seen.add(b.username)
    if "grok" in cfg.providers.get("noi_bo", []):
        raise ConfigError("providers.noi_bo không được chứa grok (AD-21)")
    return cfg


def bot_tokens(cfg: AppConfig, env: Mapping[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for b in cfg.bots:
        tok = env.get(b.token_env)
        if not tok:
            raise ConfigError(f"thiếu token của @{b.username}: biến {b.token_env}")
        out[b.username] = tok
    return out
