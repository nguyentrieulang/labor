"""Kiểm với Telegram thật. Cần TG_TEST_TOKEN_1, TG_TEST_TOKEN_2, TG_TEST_CHAT (bot 1 là admin của nhóm thử)."""

import os

import pytest
from aiogram import Bot

from labour.adapters.telegram.channel import TelegramChannel

NEED = ("TG_TEST_TOKEN_1", "TG_TEST_TOKEN_2", "TG_TEST_CHAT")
pytestmark = pytest.mark.skipif(not all(os.environ.get(k) for k in NEED), reason="thiếu biến TG_TEST_*")


@pytest.fixture
async def ch():
    tokens = {}
    for k in ("TG_TEST_TOKEN_1", "TG_TEST_TOKEN_2"):
        async with Bot(os.environ[k]) as b:
            tokens[(await b.get_me()).username.lower()] = os.environ[k]
    c = TelegramChannel(tokens, 5)
    await c.identities()
    yield c
    await c.close()


async def test_send_edit_pin_unpin(ch):
    chat = int(os.environ["TG_TEST_CHAT"])
    b1 = next(iter(ch.bots))
    mid = await ch.send_text(chat, b1, "[Hệ thống] kiểm thử tích hợp")
    await ch.edit_text(chat, b1, mid, "[Hệ thống] kiểm thử tích hợp (đã sửa)")
    await ch.pin(chat, b1, mid)
    await ch.unpin(chat, b1, mid)


async def test_bot_rights(ch):
    chat = int(os.environ["TG_TEST_CHAT"])
    for b in ch.bots:
        assert (await ch.bot_rights(chat, b)).in_group
