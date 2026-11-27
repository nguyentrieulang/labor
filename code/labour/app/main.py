"""Khởi động dịch vụ: python -X utf8 -m labour.app [config.yaml]"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

from labour.adapters.telegram.channel import TelegramChannel
from labour.app.config import ConfigError, bot_tokens, load_config
from labour.app.wiring import build_app, read_env_file

log = logging.getLogger("labour")


async def run(cfg_path: Path) -> None:
    env = {**os.environ, **read_env_file(cfg_path.parent / ".env")}
    cfg = load_config(cfg_path, env)
    channel = TelegramChannel(bot_tokens(cfg, env), cfg.poll_timeout_s)
    app = await build_app(cfg, env, channel)
    try:
        ids = await channel.identities()
        async with app.store.write() as s:
            for username, (tg_id, can_read_all) in ids.items():
                app.store.bots.set_identity(s, username, tg_id, can_read_all)
        for username, (_, can_read_all) in ids.items():
            if not can_read_all:
                log.warning("@%s chưa tắt privacy mode – chỉ thấy tin nhắc tên / lệnh, trừ khi là admin nhóm", username)
        app.audit.write("startup", bots=sorted(ids), version="1.1b")
        log.info("Labour đã chạy với %d bot", len(ids))
        await channel.start(app.ingest.on_event)
    finally:
        app.audit.write("shutdown")
        await channel.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cfg_path = Path(sys.argv[1] if len(sys.argv) > 1 else "config.yaml").resolve()
    try:
        asyncio.run(run(cfg_path))
    except ConfigError as e:
        log.error("Cấu hình lỗi: %s", e)
        sys.exit(2)
    except KeyboardInterrupt:
        pass
