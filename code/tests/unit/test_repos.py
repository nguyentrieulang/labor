import asyncio
import json
from datetime import UTC, datetime

import pytest

from labour.adapters.storage.audit import AuditJsonl
from labour.app.config import UserCfg


async def test_write_lock_serializes(store):
    order = []

    async def w(tag):
        async with store.write():
            order.append(tag + "+")
            await asyncio.sleep(0.01)
            order.append(tag + "-")

    await asyncio.gather(w("a"), w("b"))
    assert order in (["a+", "a-", "b+", "b-"], ["b+", "b-", "a+", "a-"])


async def test_write_rolls_back_on_error(seeded):
    with pytest.raises(RuntimeError):
        async with seeded.write() as s:
            seeded.processed.insert_if_absent(s, -1, 1)
            raise RuntimeError
    async with seeded.write() as s:
        assert seeded.processed.insert_if_absent(s, -1, 1) is True


async def test_processed_insert_once(store):
    async with store.write() as s:
        assert store.processed.insert_if_absent(s, -100, 5) is True
        assert store.processed.insert_if_absent(s, -100, 5) is False


async def test_users_sync_deactivates_removed(store):
    async with store.write() as s:
        store.users.sync_from_config(s, [UserCfg(tg_user_id=1, name="A"), UserCfg(tg_user_id=2, name="B")])
        store.users.sync_from_config(s, [UserCfg(tg_user_id=1, name="A")])
        assert store.users.by_tg(s, 2) is None and store.users.by_tg(s, 1) is not None


async def test_members_removed_user_not_readded(seeded, group, user2):
    async with seeded.write() as s:
        seeded.members.set_role(s, group.id, user2.id, "da_bo")
        assert seeded.members.ensure(s, group.id, user2.id) is False


async def test_members_ensure_adds_new(seeded, group):
    async with seeded.write() as s:
        u = seeded.users.by_tg(s, 333)
        assert seeded.members.ensure(s, group.id, u.id) is True
        assert seeded.members.role_of(s, group.id, u.id) == "thanh_vien"


async def test_security_level_back_to_noi_bo_clears_gemini(seeded, group):
    from labour.adapters.storage.models import GroupRow

    async with seeded.write() as s:
        seeded.groups.set_security_level(s, group.id, "thoai_mai")
        s.get(GroupRow, group.id).gemini_enabled = True
        seeded.groups.set_security_level(s, group.id, "noi_bo")
        g = seeded.groups.by_id(s, group.id)
        assert g.security_level == "noi_bo" and g.gemini_enabled is False


async def test_migrate_chat(seeded, group):
    async with seeded.write() as s:
        assert seeded.groups.migrate_chat(s, group.tg_chat_id, -100999) is True
        assert seeded.groups.by_chat(s, -100999).id == group.id
        assert seeded.groups.migrate_chat(s, -1, -2) is False


async def test_log_add_and_get(seeded, group):
    async with seeded.write() as s:
        seeded.log.add(s, group.id, 50, "bot", 1, "template", "x", None, template_code="T10")
        row = seeded.log.get(s, group.id, 50)
        assert row.template_code == "T10" and row.sender_kind == "bot"
        assert seeded.log.get(s, group.id, 51) is None


def test_audit_rejects_content_fields(tmp_path):
    a = AuditJsonl(tmp_path, clock=lambda: datetime(2026, 11, 19, tzinfo=UTC))
    a.write("turn_finished", group_id=7)
    lines = (tmp_path / "audit-2026-11.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1 and json.loads(lines[0]) == {"ts": "2026-11-19T00:00:00Z", "event": "turn_finished", "group_id": 7}
    with pytest.raises(ValueError):
        a.write("x", text="nội dung")
