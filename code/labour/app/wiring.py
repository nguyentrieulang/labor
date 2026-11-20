"""Ghép adapter vào core."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from labour.adapters.storage.audit import AuditJsonl
from labour.adapters.storage.db import make_engine, migrate
from labour.adapters.storage.repos import Store
from labour.app.config import AppConfig
from labour.core.commands import Commands
from labour.core.groups import GroupService
from labour.core.ingest import Ingest
from labour.core.outbox import Outbox
from labour.ports.channel import ChannelAdapter


@dataclass
class App:
    cfg: AppConfig
    store: Store
    ingest: Ingest
    outbox: Outbox
    channel: ChannelAdapter
    audit: AuditJsonl


def read_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


async def build_app(cfg: AppConfig, env: Mapping[str, str], channel: ChannelAdapter) -> App:
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    cfg.workspaces_dir.mkdir(parents=True, exist_ok=True)
    engine = make_engine(cfg.data_dir / "labour.db")
    migrate(engine)
    store = Store(engine)
    audit = AuditJsonl(cfg.data_dir / "audit")
    async with store.write() as s:
        store.users.sync_from_config(s, cfg.users)
        store.bots.sync_from_config(s, cfg.bots)
        store.processed.purge_older_than(s, 7)
    pool = [b.username for b in cfg.bots]
    outbox = Outbox(channel, store, cfg.limits.outbox_min_interval_s)
    groups = GroupService(store, channel, audit, cfg.workspaces_dir, cfg.data_dir, pool)
    ingest = Ingest(store, audit, outbox, groups, Commands(store, audit))
    return App(cfg, store, ingest, outbox, channel, audit)
