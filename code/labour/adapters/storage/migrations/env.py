from alembic import context

from labour.adapters.storage.models import Base

target_metadata = Base.metadata
config = context.config


def run() -> None:
    conn = config.attributes.get("connection")
    if conn is None:
        from labour.adapters.storage.db import make_engine

        url = config.get_main_option("sqlalchemy.url") or "sqlite:///labour.db"
        eng = make_engine(url.removeprefix("sqlite:///"))
        with eng.begin() as c:
            _configure(c)
        return
    _configure(conn)


def _configure(conn) -> None:
    context.configure(connection=conn, target_metadata=target_metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


run()
