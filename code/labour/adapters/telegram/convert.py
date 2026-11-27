"""Chuyển Message của aiogram thành MessageEvent (LLD 12)."""

from __future__ import annotations

from aiogram.types import Message

from labour.ports.models import IncomingFile, MessageEvent


def to_event(m: Message, via_bot: str, pool: set[str]) -> MessageEvent | None:
    if m.from_user is None and m.migrate_to_chat_id is None:
        return None
    text = m.text or m.caption or ""
    entities = m.entities if m.text else m.caption_entities
    mentions: list[str] = []
    for ent in entities or []:
        if ent.type == "mention":
            name = ent.extract_from(text).lstrip("@").lower()
            if name in pool and name not in mentions:
                mentions.append(name)

    command = target = None
    args: tuple[str, ...] = ()
    if text.startswith("/"):
        head, *rest = text.split()
        command, _, tgt = head[1:].partition("@")
        command = command.lower()
        target = tgt.lower() or None
        args = tuple(rest)

    file = None
    if m.document is not None:
        file = IncomingFile(m.document.file_name or "file", m.document.file_size or 0, m.document.file_id)

    r = m.reply_to_message
    reply_author = r.from_user if r is not None else None
    reply_to_user_id = reply_author.id if reply_author is not None and not reply_author.is_bot else None

    return MessageEvent(
        chat_id=m.chat.id,
        message_id=m.message_id,
        via_bot=via_bot,
        chat_type=m.chat.type,  # type: ignore[arg-type]
        sender_user_id=m.from_user.id if m.from_user else None,
        sender_is_bot=bool(m.from_user and m.from_user.is_bot),
        text=text,
        mentions=tuple(mentions),
        reply_to_message_id=m.reply_to_message.message_id if m.reply_to_message else None,
        file=file,
        is_command=command is not None,
        command=command,
        args=args,
        command_target=target,
        chat_title=m.chat.title,
        migrate_to_chat_id=m.migrate_to_chat_id,
        reply_to_user_id=reply_to_user_id,
    )
