from __future__ import annotations

from pathlib import Path

import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy.pool import StaticPool

MIGRATIONS = Path(__file__).parent / "migrations"


def make_engine(path: Path | str) -> sa.Engine:
    if str(path) == ":memory:":
        eng = sa.create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    else:
        eng = sa.create_engine(f"sqlite:///{Path(path).as_posix()}")

    @sa.event.listens_for(eng, "connect")
    def _pragmas(dbapi_conn, _record):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA foreign_keys=ON")
        cur.execute("PRAGMA busy_timeout=5000")
        cur.close()

    return eng


def alembic_config() -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(MIGRATIONS))
    return cfg


def migrate(engine: sa.Engine) -> None:
    cfg = alembic_config()
    with engine.begin() as conn:
        cfg.attributes["connection"] = conn
        command.upgrade(cfg, "head")
