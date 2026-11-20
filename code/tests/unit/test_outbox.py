import asyncio

import pytest

from labour.core.outbox import Outbox, PolicyViolation, split_text
from labour.ports.models import Outgoing
from tests.fakes import FakeChannel


class Clock:
    def __init__(self):
        self.t = 100.0
        self.sleeps: list[float] = []

    def __call__(self):
        return self.t

    async def sleep(self, s):
        self.sleeps.append(s)


def make(store, ch=None):
    ch = ch or FakeChannel()
    c = Clock()
    return Outbox(ch, store, 3.0, clock=c, sleep=c.sleep), ch, c


async def test_spacing_per_chat(seeded):
    ob, ch, c = make(seeded)
    await ob.send(Outgoing(-1, "labour_bot1", "a"), None)
    await ob.send(Outgoing(-1, "labour_bot1", "b"), None)
    assert c.sleeps == [3.0] and len(ch.sent) == 2


async def test_different_chats_not_delayed(seeded):
    ob, ch, c = make(seeded)
    await ob.send(Outgoing(-1, "labour_bot1", "a"), None)
    await ob.send(Outgoing(-2, "labour_bot1", "b"), None)
    assert c.sleeps == []


async def test_retry_after(seeded):
    ch = FakeChannel()
    ch.rate_limit_once = 2.0
    ob, ch, c = make(seeded, ch)
    mid = await ob.send(Outgoing(-1, "labour_bot1", "a"), None)
    assert c.sleeps == [2.0] and ch.sent[-1].message_id == mid


async def test_split_long_message(seeded):
    ob, ch, _ = make(seeded)
    text = "\n\n".join(["x" * 2000] * 4) + "\n\n" + "y" * 900
    await ob.send(Outgoing(-1, "labour_bot1", text, reply_to=5), None)
    assert len(ch.sent) == 3 and all(len(s.text) <= 4096 for s in ch.sent)
    assert "".join(s.text for s in ch.sent).replace("\n", "") == text.replace("\n", "")
    assert [s.reply_to for s in ch.sent] == [5, None, None]


async def test_long_message_parts_not_interleaved(seeded):
    class Yielding(FakeChannel):
        async def send_text(self, chat_id, bot, text, reply_to=None):
            await asyncio.sleep(0)
            return await super().send_text(chat_id, bot, text, reply_to)

    ob, ch, _ = make(seeded, Yielding())
    long = "\n\n".join(["x" * 3000] * 3)
    await asyncio.gather(ob.send(Outgoing(-1, "labour_bot1", long), None),
                         ob.send(Outgoing(-1, "labour_bot2", "ngắn"), None))
    bots = [s.bot for s in ch.sent]
    assert bots in (["labour_bot1"] * 3 + ["labour_bot2"], ["labour_bot2"] + ["labour_bot1"] * 3)


def test_split_hard_cuts_huge_paragraph():
    parts = split_text("z" * 9000)
    assert [len(p) for p in parts] == [4096, 4096, 808]


async def test_logs_with_template_code(seeded, group):
    ob, ch, _ = make(seeded)
    mid = await ob.send(Outgoing(group.tg_chat_id, "labour_bot1", "[Hệ thống] x", template_code="T13"), group.id)
    with seeded.read() as s:
        row = seeded.log.get(s, group.id, mid)
    assert row.kind == "template" and row.template_code == "T13" and row.sender_kind == "bot"


async def test_noi_bo_rejects_untemplated(seeded, group):
    ob, ch, _ = make(seeded)
    with pytest.raises(PolicyViolation):
        await ob.send(Outgoing(group.tg_chat_id, "labour_bot1", "nguyên văn tài liệu"), group.id)
    with pytest.raises(PolicyViolation):
        await ob.send(Outgoing(group.tg_chat_id, "labour_bot1", "x", template_code="T99"), group.id)
    assert ch.sent == []


async def test_thoai_mai_allows_chat(seeded, group):
    async with seeded.write() as s:
        seeded.groups.set_security_level(s, group.id, "thoai_mai")
    ob, ch, _ = make(seeded)
    await ob.send(Outgoing(group.tg_chat_id, "labour_bot2", "nội dung tự do"), group.id)
    assert len(ch.sent) == 1


async def test_pin(seeded):
    ob, ch, _ = make(seeded)
    mid = await ob.send(Outgoing(-1, "labour_bot1", "a", pin=True), None)
    assert ch.pinned == [(-1, "labour_bot1", mid)]
