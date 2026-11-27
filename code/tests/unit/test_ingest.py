import asyncio

from labour.adapters.storage.models import PendingConfirmationRow, ThreadRow
from labour.core.templates import TEMPLATES, refusal
from labour.ports.models import BotRights, IncomingFile
from tests.fakes import ev

B1 = ("labour_bot1",)


async def test_same_message_from_four_bots_concurrently(app):
    await asyncio.gather(*[app.ingest.on_event(ev(message_id=7, via_bot=f"labour_bot{i}", text="hi"))
                           for i in range(1, 5)])
    assert app.log_count(message_id=7) == 1


async def test_bot_messages_ignored(app):
    await app.ingest.on_event(ev(sender_user_id=None, sender_is_bot=True, text="x", message_id=8))
    assert app.log_count(message_id=8) == 0


async def test_unknown_user_silent(app):
    await app.ingest.on_event(ev(sender_user_id=999, text="@labour_bot1 làm đi", mentions=B1))
    assert app.outbox.sent == [] and app.last_rejection() == "unknown_user"


async def test_unknown_group_silent(app):
    await app.ingest.on_event(ev(chat_id=-555, text="@labour_bot1 làm đi", mentions=B1))
    assert app.outbox.sent == [] and app.last_rejection() == "unknown_group"


async def test_channel_rejected(app):
    await app.ingest.on_event(ev(chat_type="channel", text="x"))
    assert app.last_rejection() == "chat_type"


async def test_private_start_ignored_and_no_group_created(app):
    await app.ingest.on_event(ev(chat_id=111, chat_type="private", command="start"))
    assert app.group_count() == 1 and app.outbox.sent == [] and app.last_rejection() == "private"


async def test_private_skill_from_admin_routed(app):
    await app.ingest.on_event(ev(chat_id=111, chat_type="private", command="skill", args=("nap",)))
    assert app.outbox.sent[-1].text == TEMPLATES["S_SKILL_LATER"]


async def test_private_skill_from_non_admin_rejected(app):
    await app.ingest.on_event(ev(chat_id=222, chat_type="private", sender_user_id=222, command="skill"))
    assert app.outbox.sent == [] and app.last_rejection() == "private"


async def test_start_in_new_group_registers(app):
    await app.ingest.on_event(ev(chat_id=-777, command="start", chat_title="Nhóm mới"))
    assert app.group_count() == 2 and app.outbox.sent[0].template_code == "S_REGISTERED"


async def test_member_message_logged_only(app):
    await app.ingest.on_event(ev(sender_user_id=222, text="@labour_bot1 làm đi", mentions=B1))
    assert app.handled == [] and app.log_count(sender=222) == 1


async def test_owner_intent_classified_before_attach(app):
    seen = []
    app.ingest.attach = lambda s, g, e, intent: seen.append(intent.kind) or None
    await app.ingest.on_event(ev(text="@labour_bot1 soạn bảng", mentions=B1))
    assert seen == ["giao_viec"] and app.handled == ["giao_viec"]


async def test_attach_thread_id_is_logged(app, group):
    async with app.store.write() as s:
        t = ThreadRow(group_id=group.id, root_tg_msg_id=1, cli_turn_cap=12)
        s.add(t)
        s.flush()
        tid = t.id
    app.ingest.attach = lambda s, g, e, intent: tid
    await app.ingest.on_event(ev(message_id=40, text="@labour_bot1 soạn", mentions=B1))
    with app.store.read() as s:
        assert app.store.log.get(s, group.id, 40).thread_id == tid


async def test_reply_to_pending_confirmation(app, group):
    async with app.store.write() as s:
        s.add(PendingConfirmationRow(group_id=group.id, kind="vai", tg_msg_id=60, expires_at="2099-01-01T00:00:00Z"))
        app.store.log.add(s, group.id, 60, "bot", group.system_bot_id, "template", "x", None, template_code="S_X")
    await app.ingest.on_event(ev(message_id=61, text="ok", reply_to_message_id=60))
    assert app.handled == ["xac_nhan"]


async def test_reply_to_t10(app, group):
    async with app.store.write() as s:
        app.store.log.add(s, group.id, 70, "bot", group.system_bot_id, "template", "x", None, template_code="T10")
    await app.ingest.on_event(ev(message_id=71, text="chạy lại", reply_to_message_id=70))
    assert app.handled == ["chay_lai"]


async def test_new_config_user_becomes_member(app, group):
    await app.ingest.on_event(ev(sender_user_id=333, text="chào"))
    with app.store.read() as s:
        u = app.store.users.by_tg(s, 333)
        assert app.store.members.role_of(s, group.id, u.id) == "thanh_vien"


async def test_removed_member_rejected(app, group, user2):
    async with app.store.write() as s:
        app.store.members.set_role(s, group.id, user2.id, "da_bo")
    await app.ingest.on_event(ev(sender_user_id=222, text="chào"))
    assert app.last_rejection() == "removed_member" and app.log_count(sender=222) == 0


async def test_migrate_to_supergroup_keeps_group(app, group):
    await app.ingest.on_event(ev(chat_type="group", migrate_to_chat_id=-100999, sender_user_id=None))
    with app.store.read() as s:
        assert app.store.groups.by_chat(s, -100999).id == group.id


async def test_command_routed_and_logged(app):
    await app.ingest.on_event(ev(message_id=90, command="status", text="/status"))
    assert app.outbox.sent[-1].template_code == "S_STATUS" and app.log_count(message_id=90) == 1


async def test_file_in_noi_bo_refused(app):
    await app.ingest.on_event(ev(file=IncomingFile("a.docx", 10, "f1"), text=""))
    assert app.outbox.sent[-1].text == refusal("noi_bo_khong_nhan_file")
    assert any(e == "file_rejected" for e, _ in app.audit.events)


async def test_command_for_foreign_bot_ignored(app, group):
    await app.ingest.on_event(ev(message_id=95, command="baomat", args=("thoai_mai",), command_target="bot_khac",
                                 text="/baomat@bot_khac thoai_mai"))
    with app.store.read() as s:
        assert app.store.groups.by_id(s, group.id).security_level == "noi_bo"
    assert app.outbox.sent == [] and app.last_rejection() == "foreign_bot"


async def test_command_for_pool_bot_handled(app):
    await app.ingest.on_event(ev(message_id=96, command="status", command_target="labour_bot3", text="/status@labour_bot3"))
    assert app.outbox.sent[-1].template_code == "S_STATUS"


async def test_send_failure_does_not_drop_later_messages(app, monkeypatch):
    calls = []

    async def flaky(o, group_id, thread_id=None):
        calls.append(o.template_code)
        if len(calls) == 1:
            raise RuntimeError("network")
        return 1

    monkeypatch.setattr(app.outbox, "send", flaky)
    app.channel.rights["labour_bot1"] = BotRights(in_group=True, is_admin=False, can_pin=False, can_read_all=True)
    await app.ingest.on_event(ev(chat_id=-778, command="start", command_target="labour_bot1", chat_title="Nhóm B"))
    assert calls == ["S_REGISTERED", "S_BOT_RIGHTS"]
    assert any(e == "send_failed" and f["error"] == "RuntimeError" for e, f in app.audit.events)


async def test_non_owner_cannot_create_turns_even_with_mention(app):
    await app.ingest.on_event(ev(sender_user_id=222, text="@labour_bot1 dừng", mentions=B1))
    assert app.handled == []


# --- 1.1b: chỉ nhận siêu nhóm. Ở nhóm thường mỗi bot tự đánh số tin, nên không chống trùng theo message_id được.

async def test_basic_group_start_answered_once_and_not_registered(app):
    for i in range(1, 5):  # 4 bot cùng nhận, mỗi bot một số tin khác nhau
        await app.ingest.on_event(ev(chat_id=-777, chat_type="group", message_id=10 + i, via_bot=f"labour_bot{i}",
                                     command="start", chat_title="Nhóm thường"))
    assert app.group_count() == 1
    assert [o.template_code for o in app.outbox.sent] == ["S_NEED_SUPERGROUP"]
    assert app.outbox.sent[0].bot == "labour_bot1" and app.outbox.sent[0].text == TEMPLATES["S_NEED_SUPERGROUP"]
    assert app.last_rejection() == "basic_group"


async def test_basic_group_start_with_target_answered_by_that_bot(app):
    for i in range(1, 5):
        await app.ingest.on_event(ev(chat_id=-777, chat_type="group", message_id=20 + i, via_bot=f"labour_bot{i}",
                                     command="start", command_target="labour_bot3"))
    assert [(o.bot, o.template_code) for o in app.outbox.sent] == [("labour_bot3", "S_NEED_SUPERGROUP")]


async def test_basic_group_start_from_user_without_permission_silent(app):
    await app.ingest.on_event(ev(chat_id=-777, chat_type="group", sender_user_id=222, command="start"))
    assert app.outbox.sent == [] and app.group_count() == 1 and app.last_rejection() == "basic_group"


async def test_basic_group_messages_not_logged_even_if_ids_collide(app, group):
    # nhóm đã đăng ký (dữ liệu cũ) nhưng là nhóm thường: không xử lý, không ghi group_log, không lỗi
    for i in range(1, 5):
        await app.ingest.on_event(ev(chat_id=group.tg_chat_id, chat_type="group", message_id=7, via_bot=f"labour_bot{i}",
                                     command="status", text="/status"))
    assert app.outbox.sent == [] and app.log_count(message_id=7) == 0
    assert [e for e, f in app.audit.events if f.get("reason") == "basic_group"] == ["update_rejected"]
