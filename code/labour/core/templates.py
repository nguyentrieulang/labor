"""Mẫu tin cố định (LLD 8.1). Ở nhóm Nội bộ chỉ được gửi tin dựng từ các mẫu này."""

from __future__ import annotations

from string import Formatter

from labour.core.text import safe_basename

TEMPLATES: dict[str, str] = {
    "T01": "[{vai}] Đã trả lời – xem {path}",
    "T02": "[{vai}] Hỏi @{bot} ({n}/3) – câu hỏi: {path}",
    "T03": "[Hệ thống] @{owner} cần quyết định ({ly_do_ma}) – xem {path}",
    "T04": "[{vai}] Xong {k} file → nhờ @{reviewer} review (vòng {r}/3): {paths}",
    "T05": "[{vai}] Vòng {r}/3: CHƯA ĐẠT – {k} góp ý: {path}",
    "T06": "[{vai}] Đã sửa theo góp ý vòng {r_cu} → review lại (vòng {r}/3): {paths}",
    "T07": "ĐẠT – {paths} · duyệt: {who} · {r} vòng",
    "T08": "[{vai}] Đã soạn bản quyết định: {path} – reply “ok” để chốt",
    "T09": "[Hệ thống] Đã chốt quyết định giải pháp – phiên bản {n}",
    "T10": "[Hệ thống] Lượt của @{bot} lỗi ({error_code}) – reply “chạy lại” để thử lại",
    "T11": "[Hệ thống] Claude hết hạn mức đến {gio}. Provider được phép: {ds}",
    "T12": "[Hệ thống] File quyết định bị sửa ngoài hệ thống – đã khôi phục phiên bản {n}",
    "T13": "[Hệ thống] {ma_tu_choi}",
    "T14": "[{vai}] Tôi nhận vai {vai}{co_reviewer} – lời giao: “{trich}”",
    "T15": "[Hệ thống] Đã đóng việc #{thread_id} vì có việc mới – huỷ {k} lượt chờ",
    "S_REGISTERED": "[Hệ thống] Đã đăng ký nhóm – mức Nội bộ. Đổi: /baomat thoai_mai. Thư mục: {workspace}",
    "S_NEED_SUPERGROUP": "[Hệ thống] Labour chỉ chạy trong siêu nhóm (supergroup). Chuyển nhóm: Cài đặt nhóm → "
                         "Chat history for new members → Visible, rồi gõ lại /start",
    "S_BOT_RIGHTS": "[Hệ thống] Thiếu quyền: {details}",
    "S_LEVEL": "[Hệ thống] Mức bảo mật của nhóm: {level}",
    "S_MEMBER": "[Hệ thống] Thành viên {name}: {role}",
    "S_SKILL_LATER": "[Hệ thống] Quản lý skill chưa có ở bản này",
    "S_ROLES": "[Hệ thống] Vai trong nhóm:\n{lines}",
    "S_NO_ROLE": "[Hệ thống] Chưa có vai nào",
    "S_SKILLS": "[Hệ thống] Skill:\n{lines}",
    "S_NO_SKILL": "[Hệ thống] Chưa có skill",
    "S_STATUS": "[Hệ thống] Thread mở: {n} · lượt chờ: {cho} · đang chạy: {dang_chay} · chi phí hôm nay: ${cost}",
}

REFUSALS: dict[str, str] = {
    "chi_chu_nhom": "Lệnh này chỉ dành cho chủ nhóm",
    "provider_chua_ho_tro": "Provider chưa hỗ trợ ở bản này",
    "provider_khong_duoc_phep": "Provider không được phép ở mức bảo mật này",
    "noi_bo_khong_nhan_file": "Nhóm Nội bộ không nhận file qua Telegram",
    "bot_chua_co_vai": "@{bot} chưa có vai",
    "skill_khong_dung_duoc": "Skill không dùng được ở nhóm này",
    "dang_cho_xac_nhan_vai": "Đang chờ xác nhận vai",
    "chi_trong_thoai_mai": "Lệnh này chỉ dùng ở nhóm Thoải mái",
}


def _fields(tpl: str) -> set[str]:
    return {name for _, name, _, _ in Formatter().parse(tpl) if name}


def render(code: str, **vars: object) -> str:
    tpl = TEMPLATES[code]
    missing = _fields(tpl) - vars.keys()
    if missing:
        raise KeyError(f"{code} thiếu biến {sorted(missing)}")
    if "path" in vars:
        vars["path"] = safe_basename(str(vars["path"]))
    if "paths" in vars:
        p = vars["paths"]
        items = [p] if isinstance(p, str) else list(p)  # type: ignore[arg-type]
        vars["paths"] = ", ".join(safe_basename(str(x)) for x in items)
    return tpl.format(**vars)


def refusal(code: str, **vars: object) -> str:
    return render("T13", ma_tu_choi=REFUSALS[code].format(**vars))
