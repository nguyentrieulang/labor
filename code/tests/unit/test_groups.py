import pytest

from labour.core.groups import WORKSPACE_DIRS, GroupService
from labour.core.templates import render
from labour.ports.models import BotRights
from tests.conftest import POOL
from tests.fakes import FakeAudit, FakeChannel, ev


@pytest.fixture
def svc(seeded, tmp_path):
    ch = FakeChannel()
    return GroupService(seeded, ch, FakeAudit(), tmp_path / "ws", tmp_path / "data", POOL)


def owner(store):
    with store.read() as s:
        return store.users.by_tg(s, 111)


def start(**kw):
    return ev(chat_id=-200, command="start", chat_title="Phản hồi đối tác X", **kw)


async def test_start_registers_noi_bo_and_creates_dirs(svc, seeded, tmp_path):
    out = await svc.register(start(), owner(seeded))
    with seeded.read() as s:
        g = seeded.groups.by_chat(s, -200)
        assert seeded.members.role_of(s, g.id, owner(seeded).id) == "chu"
    assert g.security_level == "noi_bo"
    assert g.workspace_path == tmp_path / "ws" / f"phan-hoi-doi-tac-x-{g.id}"
    assert all((g.workspace_path / d).is_dir() for d in WORKSPACE_DIRS)
    assert (tmp_path / "data" / "groups" / str(g.id) / "chi-dan.md").is_file()
    assert out[0].text == render("S_REGISTERED", workspace=g.workspace_path)
    assert out[0].template_code == "S_REGISTERED" and len(out) == 1
    assert svc.audit.events[-1][0] == "group_registered"


async def test_start_without_permission_silent(svc, seeded):
    with seeded.read() as s:
        u2 = seeded.users.by_tg(s, 222)
    assert await svc.register(start(sender_user_id=222), u2) == []
    assert await svc.register(start(sender_user_id=999), None) == []
    with seeded.read() as s:
        assert seeded.groups.by_chat(s, -200) is None


async def test_start_in_private_silent(svc, seeded):
    assert await svc.register(ev(chat_id=111, chat_type="private", command="start"), owner(seeded)) == []


async def test_start_twice_is_silent(svc, seeded):
    await svc.register(start(), owner(seeded))
    assert await svc.register(start(message_id=2), owner(seeded)) == []


async def test_start_addressed_to_foreign_bot_silent(svc, seeded):
    assert await svc.register(start(command_target="other_bot"), owner(seeded)) == []


async def test_system_bot_is_command_target(svc, seeded):
    out = await svc.register(start(via_bot="labour_bot3", command_target="labour_bot2"), owner(seeded))
    with seeded.read() as s:
        g = seeded.groups.by_chat(s, -200)
        assert seeded.bots.by_id(s, g.system_bot_id).username == "labour_bot2"
    assert out[0].bot == "labour_bot2"


NOT_ADMIN = BotRights(in_group=True, is_admin=False, can_pin=False, can_read_all=True)
NOT_IN_GROUP = BotRights(in_group=False, is_admin=False, can_pin=False, can_read_all=True)


def system_bot_of(store):
    with store.read() as s:
        return store.bots.by_id(s, store.groups.by_chat(s, -200).system_bot_id).username


async def test_missing_rights_reported(svc, seeded):
    svc.channel.rights["labour_bot2"] = BotRights(in_group=True, is_admin=False, can_pin=False, can_read_all=False)
    svc.channel.rights["labour_bot1"] = NOT_ADMIN
    out = await svc.register(start(command_target="labour_bot1"), owner(seeded))
    assert len(out) == 2 and out[1].template_code == "S_BOT_RIGHTS"
    assert "@labour_bot2" in out[1].text and "@labour_bot1" in out[1].text


async def test_bare_start_picks_first_admin_bot_not_receiving_bot(svc, seeded):  # review 1.1, B2
    svc.channel.rights["labour_bot1"] = NOT_ADMIN
    out = await svc.register(start(via_bot="labour_bot4"), owner(seeded))
    assert system_bot_of(seeded) == "labour_bot2" and out[0].bot == "labour_bot2" and len(out) == 1


async def test_bare_start_without_admin_picks_first_bot_in_group_and_reports(svc, seeded):
    svc.channel.rights.update({"labour_bot1": NOT_IN_GROUP, "labour_bot2": NOT_ADMIN,
                               "labour_bot3": NOT_ADMIN, "labour_bot4": NOT_ADMIN})
    out = await svc.register(start(via_bot="labour_bot4"), owner(seeded))
    assert system_bot_of(seeded) == "labour_bot2"
    assert "@labour_bot2: bot hệ thống cần là admin" in out[1].text


async def test_rights_check_failure_does_not_block(svc, seeded):
    async def boom(chat_id, bot):
        raise RuntimeError("network")

    svc.channel.bot_rights = boom
    out = await svc.register(start(), owner(seeded))
    assert out[0].template_code == "S_REGISTERED" and "không kiểm được" in out[1].text
