import pytest

from labour.adapters.storage.db import make_engine
from labour.adapters.storage.models import Base
from labour.adapters.storage.repos import Store
from labour.app.config import BotCfg, UserCfg

POOL = ["labour_bot1", "labour_bot2", "labour_bot3", "labour_bot4"]
USERS = [
    UserCfg(tg_user_id=111, name="Chủ", admin=True, can_create_group=True),
    UserCfg(tg_user_id=222, name="Thành viên"),
    UserCfg(tg_user_id=333, name="Mới"),
]


@pytest.fixture
def store():
    eng = make_engine(":memory:")
    Base.metadata.create_all(eng)
    return Store(eng)


@pytest.fixture
async def seeded(store):
    async with store.write() as s:
        store.users.sync_from_config(s, USERS)
        store.bots.sync_from_config(s, [BotCfg(username=b, token_env=f"BOT{i}_TOKEN") for i, b in enumerate(POOL, 1)])
    return store


@pytest.fixture
async def group(seeded, tmp_path):
    store = seeded
    async with store.write() as s:
        owner = store.users.by_tg(s, 111)
        g = store.groups.create(s, -100, "Nhóm thử", owner.id, tmp_path / "ws", store.bots.by_username(s, "labour_bot1").id)
        store.members.add(s, g.id, owner.id, "chu")
        store.members.add(s, g.id, store.users.by_tg(s, 222).id, "thanh_vien")
    return g


class App:
    def __init__(self, store, tmp_path):
        from labour.core.commands import Commands
        from labour.core.groups import GroupService
        from labour.core.ingest import Ingest
        from tests.fakes import FakeAudit, FakeChannel, FakeOutbox

        self.store = store
        self.audit = FakeAudit()
        self.channel = FakeChannel()
        self.outbox = FakeOutbox()
        self.handled = []

        async def record(group, thread_id, e, intent):
            self.handled.append(intent.kind)
            return []

        kinds = ["xac_nhan", "mo_lai", "dat", "chay_lai", "dung", "gan_skill", "doi_provider", "chot",
                 "giao_vai", "sua_vai", "giao_viec", "khong"]
        groups = GroupService(store, self.channel, self.audit, tmp_path / "ws", tmp_path / "data", POOL)
        self.ingest = Ingest(store, self.audit, self.outbox, groups, Commands(store, self.audit),
                             handlers={k: record for k in kinds})

    def log_count(self, message_id=None, sender=None):
        import sqlalchemy as sa

        from labour.adapters.storage.models import GroupLogRow, UserRow

        q = sa.select(sa.func.count()).select_from(GroupLogRow)
        if message_id is not None:
            q = q.where(GroupLogRow.tg_msg_id == message_id)
        if sender is not None:
            q = q.join(UserRow, UserRow.id == GroupLogRow.sender_id).where(
                GroupLogRow.sender_kind == "user", UserRow.tg_user_id == sender)
        with self.store.read() as s:
            return s.scalar(q)

    def group_count(self):
        import sqlalchemy as sa

        from labour.adapters.storage.models import GroupRow

        with self.store.read() as s:
            return s.scalar(sa.select(sa.func.count()).select_from(GroupRow))

    def last_rejection(self):
        ev = [f for e, f in self.audit.events if e == "update_rejected"]
        return ev[-1]["reason"] if ev else None


@pytest.fixture
async def app(seeded, group, tmp_path):
    return App(seeded, tmp_path)


@pytest.fixture
async def user2(seeded):
    with seeded.read() as s:
        return seeded.users.by_tg(s, 222)
