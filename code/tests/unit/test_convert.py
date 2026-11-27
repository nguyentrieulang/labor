from aiogram.types import Message

from labour.adapters.telegram.channel import TelegramChannel
from labour.adapters.telegram.convert import to_event

POOL = {"labour_bot1", "labour_bot2", "labour_bot3", "labour_bot4"}
USER = {"id": 111, "is_bot": False, "first_name": "A"}
GROUP = {"id": -100, "type": "supergroup", "title": "Nhóm thử"}


def msg(**kw) -> Message:
    base = {"message_id": 5, "date": 1763500000, "chat": GROUP, "from": USER}
    base.update(kw)
    return Message.model_validate(base)


def mention_entities(text: str, *names: str) -> list[dict]:
    out = []
    for n in names:
        i = text.index("@" + n)
        off = len(text[:i].encode("utf-16-le")) // 2
        out.append({"type": "mention", "offset": off, "length": len(n) + 1})
    return out


def test_to_event_mentions_in_order_only_pool():
    text = "Đạt 😀 @labour_bot2 và @someone rồi @Labour_Bot1"
    e = to_event(msg(text=text, entities=mention_entities(text, "labour_bot2", "someone", "Labour_Bot1")),
                 "labour_bot3", POOL)
    assert e.mentions == ("labour_bot2", "labour_bot1") and e.via_bot == "labour_bot3"
    assert e.is_command is False and e.chat_type == "supergroup" and e.chat_title == "Nhóm thử"


def test_to_event_command_with_target():
    e = to_event(msg(text="/start@Labour_Bot1"), "labour_bot2", POOL)
    assert e.command == "start" and e.command_target == "labour_bot1" and e.args == ()


def test_to_event_command_args():
    e = to_event(msg(text="/vai @labour_bot2 tatca"), "labour_bot1", POOL)
    assert e.command == "vai" and e.command_target is None and e.args == ("@labour_bot2", "tatca")


def test_to_event_caption_used_as_text():
    cap = "@labour_bot1 xem file"
    e = to_event(msg(document={"file_id": "F1", "file_unique_id": "U1", "file_name": "a.docx", "file_size": 10},
                     caption=cap, caption_entities=mention_entities(cap, "labour_bot1")), "labour_bot1", POOL)
    assert e.text == cap and e.mentions == ("labour_bot1",)
    assert e.file.name == "a.docx" and e.file.size == 10 and e.file.tg_file_id == "F1"


def test_to_event_forwarded_is_normal():
    e = to_event(msg(text="chuyển tiếp", forward_origin={"type": "hidden_user", "date": 1763500000,
                                                          "sender_user_name": "X"}), "labour_bot1", POOL)
    assert e.text == "chuyển tiếp" and e.sender_user_id == 111


def test_to_event_private_chat_type():
    e = to_event(msg(chat={"id": 111, "type": "private"}, text="/skill nap"), "labour_bot1", POOL)
    assert e.chat_type == "private" and e.command == "skill"


def test_to_event_migrate():
    e = to_event(msg(migrate_to_chat_id=-100999), "labour_bot1", POOL)
    assert e.migrate_to_chat_id == -100999


def test_to_event_reply_id():
    e = to_event(msg(text="ok", reply_to_message={"message_id": 3, "date": 1763500000, "chat": GROUP}),
                 "labour_bot1", POOL)
    assert e.reply_to_message_id == 3


def test_to_event_reply_author_id():  # 1.1c: lấy người viết tin gốc từ Telegram
    e = to_event(msg(text="/thanhvien them", reply_to_message={
        "message_id": 30, "date": 1763500000, "chat": GROUP, "text": "Test",
        "from": {"id": 222, "is_bot": False, "first_name": "B", "username": "ntlang"}}), "labour_bot1", POOL)
    assert e.reply_to_message_id == 30 and e.reply_to_user_id == 222 and e.reply_to_username == "ntlang"


def test_to_event_reply_to_bot_has_no_author_id():
    e = to_event(msg(text="ok", reply_to_message={
        "message_id": 31, "date": 1763500000, "chat": GROUP,
        "from": {"id": 9, "is_bot": True, "first_name": "Bot"}}), "labour_bot1", POOL)
    assert e.reply_to_message_id == 31 and e.reply_to_user_id is None


def test_to_event_from_bot():
    e = to_event(msg(text="x", **{"from": {"id": 9, "is_bot": True, "first_name": "B"}}), "labour_bot1", POOL)
    assert e.sender_is_bot is True


def test_edited_message_not_dispatched():
    ch = TelegramChannel({"labour_bot1": "123456:" + "A" * 35}, 30)

    async def on_event(e):
        pass

    dp = ch._build_dispatcher(on_event)
    assert dp.edited_message.handlers == [] and len(dp.message.handlers) == 1
