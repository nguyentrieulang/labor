from datetime import UTC, datetime

import pytest

from labour.adapters.storage.models import RoleAssignmentRow, ThreadRow, TurnRow
from labour.core.commands import Commands
from labour.core.templates import TEMPLATES, refusal, render
from tests.fakes import FakeAudit, ev


@pytest.fixture
def cmds(seeded):
    return Commands(seeded, FakeAudit())


def users(store):
    with store.read() as s:
        return store.users.by_tg(s, 111), store.users.by_tg(s, 222)


def level(store, g):
    with store.read() as s:
        return store.groups.by_id(s, g.id).security_level


async def add_role(store, g, bot, **kw):
    async with store.write() as s:
        b = store.bots.by_username(s, bot)
        s.add(RoleAssignmentRow(group_id=g.id, bot_id=b.id, role_name=kw.get("role_name", "Phân tích"),
                                instructions=kw.get("instructions", "x"), source_text="s",
                                quote=kw.get("quote", "phân tích yêu cầu"), provider="claude",
                                is_reviewer=kw.get("is_reviewer", False), status="hieu_luc", version=1))


async def run(cmds, g, u, command, *args, **kw):
    return await cmds.dispatch(g, u, ev(chat_id=g.tg_chat_id, message_id=kw.pop("message_id", 9), command=command,
                                        args=args, **kw))


@pytest.mark.parametrize("command,args", [("baomat", ("thoai_mai",)), ("gemini", ("bat",)), ("thanhvien", ("bot",))])
async def test_member_cannot_run_owner_commands(cmds, seeded, group, command, args):
    _, u2 = users(seeded)
    out = await run(cmds, group, u2, command, *args)
    assert [o.text for o in out] == [refusal("chi_chu_nhom")] and out[0].template_code == "T13"
    assert level(seeded, group) == "noi_bo"


async def test_owner_baomat_thoai_mai(cmds, seeded, group):
    owner, _ = users(seeded)
    out = await run(cmds, group, owner, "baomat", "thoai_mai")
    assert out[0].text == render("S_LEVEL", level="thoai_mai") and level(seeded, group) == "thoai_mai"
    assert out[0].bot == "labour_bot1" and out[0].reply_to == 9
    assert cmds.audit.events[-1][0] == "security_level_changed"


async def test_baomat_bad_arg_shows_current(cmds, seeded, group):
    owner, _ = users(seeded)
    out = await run(cmds, group, owner, "baomat", "mo_toang")
    assert out[0].text == render("S_LEVEL", level="noi_bo") and level(seeded, group) == "noi_bo"


async def test_gemini_in_noi_bo_refused(cmds, seeded, group):
    owner, _ = users(seeded)
    assert (await run(cmds, group, owner, "gemini", "bat"))[0].text == refusal("chi_trong_thoai_mai")


async def test_gemini_unsupported_in_thoai_mai(cmds, seeded, group):
    owner, _ = users(seeded)
    async with seeded.write() as s:
        seeded.groups.set_security_level(s, group.id, "thoai_mai")
        g = seeded.groups.by_id(s, group.id)
    assert (await run(cmds, g, owner, "gemini", "bat"))[0].text == refusal("provider_chua_ho_tro")


async def test_vai_never_shows_instructions(cmds, seeded, group):
    _, u2 = users(seeded)
    await add_role(seeded, group, "labour_bot2", instructions="BÍ-MẬT-XYZ", quote="phân tích yêu cầu", is_reviewer=True)
    out = await run(cmds, group, u2, "vai")
    assert out[0].template_code == "S_ROLES"
    assert "phân tích yêu cầu" in out[0].text and "BÍ-MẬT-XYZ" not in out[0].text
    assert "@labour_bot2 – [Phân tích] (reviewer) – claude – skill: không" in out[0].text


async def test_vai_filter_by_bot(cmds, seeded, group):
    owner, _ = users(seeded)
    await add_role(seeded, group, "labour_bot2")
    await add_role(seeded, group, "labour_bot3", role_name="Review")
    out = await run(cmds, group, owner, "vai", "@labour_bot3")
    assert "@labour_bot3" in out[0].text and "@labour_bot2" not in out[0].text


async def test_vai_tatca_only_groups_of_member(cmds, seeded, group, tmp_path):
    owner, u2 = users(seeded)
    async with seeded.write() as s:
        other = seeded.groups.create(s, -300, "Nhóm khác", owner.id, tmp_path / "o", group.system_bot_id)
        seeded.members.add(s, other.id, owner.id, "chu")
    await add_role(seeded, group, "labour_bot2", role_name="Ở nhóm thử")
    await add_role(seeded, other, "labour_bot2", role_name="Ở nhóm khác")
    out_owner = await run(cmds, group, owner, "vai", "@labour_bot2", "tatca")
    out_u2 = await run(cmds, group, u2, "vai", "@labour_bot2", "tatca")
    assert "Nhóm khác: " in out_owner[0].text and "Nhóm thử: " in out_owner[0].text
    assert "Nhóm khác" not in out_u2[0].text and "Ở nhóm thử" in out_u2[0].text


async def test_vai_empty(cmds, seeded, group):
    owner, _ = users(seeded)
    assert (await run(cmds, group, owner, "vai"))[0].text == TEMPLATES["S_NO_ROLE"]


@pytest.mark.parametrize("word", ["bo", "bot"])
async def test_thanhvien_bo_by_reply(cmds, seeded, group, word):
    # 1.1c: người cần đổi lấy từ reply_to_message.from.id của Telegram, không tra group_log
    owner, u2 = users(seeded)
    out = await run(cmds, group, owner, "thanhvien", word, reply_to_message_id=77, reply_to_user_id=222)
    with seeded.read() as s:
        assert seeded.members.role_of(s, group.id, u2.id) == "da_bo"
    assert out[0].template_code == "S_MEMBER"
    out = await run(cmds, group, owner, "thanhvien", "them", reply_to_message_id=88, reply_to_user_id=222)
    with seeded.read() as s:
        assert seeded.members.role_of(s, group.id, u2.id) == "thanh_vien"


async def test_thanhvien_them_by_reply_to_message_sent_after_removal(cmds, seeded, group):
    # lỗi nghiệm thu 1.1b: tin của người đã bỏ không có trong group_log, vẫn phải thêm lại được
    owner, u2 = users(seeded)
    async with seeded.write() as s:
        seeded.members.set_role(s, group.id, u2.id, "da_bo")
    out = await run(cmds, group, owner, "thanhvien", "them", reply_to_message_id=999, reply_to_user_id=222)
    with seeded.read() as s:
        assert seeded.members.role_of(s, group.id, u2.id) == "thanh_vien"
    assert out[0].text == render("S_MEMBER", name=u2.display_name, role="thành viên")


async def test_thanhvien_without_reply_shows_hint(cmds, seeded, group):
    owner, _ = users(seeded)
    out = await run(cmds, group, owner, "thanhvien", "bo")
    assert "reply vào tin" in out[0].text and "them | bo" in out[0].text


@pytest.mark.parametrize("reply_user", [None, 999])  # reply vào tin của bot / người không có trong config
async def test_thanhvien_reply_to_bot_or_stranger_shows_hint(cmds, seeded, group, reply_user):
    owner, _ = users(seeded)
    out = await run(cmds, group, owner, "thanhvien", "bo", reply_to_message_id=50, reply_to_user_id=reply_user)
    assert "reply vào tin" in out[0].text


async def test_thanhvien_cannot_remove_owner(cmds, seeded, group):
    owner, _ = users(seeded)
    await run(cmds, group, owner, "thanhvien", "bot", reply_to_message_id=78, reply_to_user_id=111)
    with seeded.read() as s:
        assert seeded.members.role_of(s, group.id, owner.id) == "chu"


async def test_skill_in_group_ignored(cmds, seeded, group):
    owner, _ = users(seeded)
    assert await run(cmds, group, owner, "skill", "nap") == []
    assert await run(cmds, group, owner, "khonglenh") == []


async def test_skills_empty(cmds, seeded, group):
    owner, _ = users(seeded)
    assert (await run(cmds, group, owner, "skills"))[0].text == TEMPLATES["S_NO_SKILL"]


async def test_status_counts(cmds, seeded, group):
    owner, _ = users(seeded)
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    async with seeded.write() as s:
        t = ThreadRow(group_id=group.id, root_tg_msg_id=1, cli_turn_cap=12)
        s.add(t)
        s.flush()
        bot = group.system_bot_id
        s.add_all([TurnRow(thread_id=t.id, group_id=group.id, bot_id=bot, kind="thuong", status="cho"),
                   TurnRow(thread_id=t.id, group_id=group.id, bot_id=bot, kind="thuong", status="cho"),
                   TurnRow(thread_id=t.id, group_id=group.id, bot_id=bot, kind="thuong", status="dang_chay"),
                   TurnRow(thread_id=t.id, group_id=group.id, bot_id=bot, kind="thuong", status="xong",
                           cost_usd=0.25, finished_at=now)])
    out = await run(cmds, group, owner, "status")
    assert out[0].text == render("S_STATUS", n=1, cho=2, dang_chay=1, cost="0.25")
