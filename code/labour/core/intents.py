"""Nhận diện ý của tin chủ nhóm – 12 luật tất định, xét theo thứ tự (LLD 7.3).

Từ mà bỏ dấu đổi nghĩa (đúng/dừng/dùng, bỏ/bộ, đổi/đối, vai/vài, đạt/đặt, chốt/chót, huỷ/huy động) khớp trên
chữ còn dấu `L`; chữ không dấu chỉ nhận ở dạng không lẫn được.
Luật 6–10 chỉ nhận lệnh đứng ngay đầu câu (sau phần nhắc tên bot); còn lại là giao việc.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence

from labour.core.text import flat, low, strip_mentions
from labour.ports.models import Intent, ReplyTarget

R_CONFIRM = re.compile(r"^(ok|okay|đồng ý|dong y|đúng|xác nhận|xac nhan)(\s+(rồi|roi|nhé|nhe|nha))?[\s.!]*$")
R_DAT = re.compile(r"^(ok\s+)?(đạt|dat)(\s+(rồi|roi))?[\s.!]*$")
R_MO_LAI = re.compile(r"(?<!\w)(không đạt|khong dat)(?!\w)")
# "huy" không dấu chỉ nhận khi cả câu là lệnh huỷ ("huy động…" là giao việc)
R_STOP = re.compile(r"^(dừng|huỷ|hủy|stop)\b|^huy(\s+(đi|di|nhé|nhe|việc|viec|bỏ|bo))?[\s.!]*$")
R_SKILL = re.compile(r"^(dùng|dung) (thêm |them )?skill ([a-z0-9-]{3,40})\b")
R_PROVIDER = re.compile(r"^(dùng|dung|chuyển sang|chuyen sang) (claude|grok|gemini)(\s+(nhé|nhe|nha|đi|di))?[\s.!]*$")
R_CHOT = re.compile(r"^(chốt|chot)\b")
R_ROLE_WORD = re.compile(r"^(vai trò|vai tro|vai|nhiệm vụ|nhiem vu)\b")
R_EDIT_ROLE = re.compile(r"^(thêm|bớt|bỏ|đổi|sửa|them|sua) (việc|vai|nhiệm vụ|viec|nhiem vu)\b")
_LEAD_PUNCT = " ,:;.-–"


def classify(text: str, mentions: Sequence[str], reply: ReplyTarget | None,
             has_role: Callable[[str], bool]) -> Intent:
    body = strip_mentions(text).lstrip(_LEAD_PUNCT)
    L, F = low(body), flat(body)
    M = tuple(dict.fromkeys(mentions))
    rk = reply.kind if reply else None

    if rk in ("pending_vai", "pending_chot") and R_CONFIRM.match(L):
        return Intent("xac_nhan", M, confirm_kind="vai" if rk == "pending_vai" else "chot")
    if rk == "dat_pin" and R_MO_LAI.search(L):
        return Intent("mo_lai", M)
    if rk == "msg" and reply.thread_status in ("dang_lam", "cho_nguoi") and R_DAT.match(L):
        return Intent("dat", M)
    if rk == "t10_error" and "chay lai" in F:
        return Intent("chay_lai", M)
    if reply is not None and reply.thread_id is not None and R_STOP.match(L):
        return Intent("dung", M)
    if M:
        if m := R_SKILL.search(L):
            return Intent("gan_skill", M, skill=m.group(3))
        if m := R_PROVIDER.search(L):
            return Intent("doi_provider", M, provider=m.group(2))
        if R_CHOT.search(L):
            return Intent("chot", M)
        if L.startswith("giao vai") or (R_ROLE_WORD.match(L) and any(not has_role(b) for b in M)):
            return Intent("giao_vai", M)
        if any(has_role(b) for b in M) and R_EDIT_ROLE.match(L):
            return Intent("sua_vai", M)
        return Intent("giao_viec", M)
    if reply is not None and reply.bot is not None:
        if not reply.is_system:
            return Intent("giao_viec", (reply.bot,))
        if reply.thread_id is not None:
            return Intent("giao_viec", ())
    return Intent("khong")
