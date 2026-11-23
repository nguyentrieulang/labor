import pytest

from labour.core.intents import classify
from labour.ports.models import ReplyTarget

P = ReplyTarget("pending_vai", None, None, "labour_bot1", True)
PC = ReplyTarget("pending_chot", None, None, "labour_bot1", True)
D = ReplyTarget("dat_pin", 31, "dat", "labour_bot1", True)
E = ReplyTarget("t10_error", 31, "dang_lam", "labour_bot1", True)


def T(st):
    return ReplyTarget("msg", 31, st, "labour_bot2", False)


B1, B2, B3 = "labour_bot1", "labour_bot2", "labour_bot3"

CASES = [
    # 1 xác nhận – cả câu
    ("ok", [], P, set(), "xac_nhan"), ("OK.", [], P, set(), "xac_nhan"), ("Đồng ý", [], P, set(), "xac_nhan"),
    ("dong y", [], P, set(), "xac_nhan"), ("đúng rồi", [], P, set(), "xac_nhan"), ("ok nhé", [], P, set(), "xac_nhan"),
    ("xac nhan", [], PC, set(), "xac_nhan"),
    ("dừng", [], P, set(), "khong"),                                  # không được hiểu là xác nhận
    ("đúng rồi nhưng khoan đã", [], P, set(), "khong"),
    ("ok", [], T("dang_lam"), set(), "giao_viec"),                    # không phải tin chờ xác nhận
    # 2 mở lại
    ("không đạt, sửa mục 3", [], D, set(), "mo_lai"), ("khong dat", [], D, set(), "mo_lai"),
    # 3 đạt
    ("Đạt!", [], T("dang_lam"), set(), "dat"), ("Dat!", [], T("dang_lam"), set(), "dat"),
    ("ok đạt", [], T("cho_nguoi"), set(), "dat"), ("đạt rồi", [], T("dang_lam"), set(), "dat"),
    ("đạt", [], T("dat"), set(), "giao_viec"),                        # Thread đã đạt
    ("đặt lại tên file", [], T("dang_lam"), set(), "giao_viec"),
    ("đặt", [], T("dang_lam"), set(), "giao_viec"),                   # đặt ≠ đạt
    # 4 chạy lại
    ("chạy lại", [], E, set(), "chay_lai"), ("chay lai", [], E, set(), "chay_lai"),
    # 5 dừng
    ("dừng lại", [], T("dang_lam"), set(), "dung"), ("Huỷ", [], T("cho_nguoi"), set(), "dung"),
    ("hủy", [], T("dang_lam"), set(), "dung"), ("huy", [], T("dang_lam"), set(), "dung"),
    ("STOP", [], T("dang_lam"), set(), "dung"),
    ("dung lai", [], T("dang_lam"), set(), "giao_viec"),              # "dung" không dấu: không đoán là dừng
    # 6 gán skill
    ("@labour_bot2 dùng thêm skill bao-cao-doi-tac", [B2], None, {B2}, "gan_skill"),
    ("@labour_bot2 dung them skill bao-cao-doi-tac", [B2], None, {B2}, "gan_skill"),
    # 7 đổi provider
    ("dùng claude", [B2], T("dang_lam"), {B2}, "doi_provider"),       # không bị luật 5 bắt
    ("@labour_bot2 chuyển sang gemini", [B2], None, {B2}, "doi_provider"),
    ("@labour_bot2 chuyen sang gemini", [B2], None, {B2}, "doi_provider"),
    # 8 chốt
    ("@labour_bot1 chốt phương án B", [B1], None, {B1}, "chot"),
    ("@labour_bot1 chot phuong an B", [B1], None, {B1}, "chot"),
    # 9 giao vai
    ("@labour_bot1 giao vai: phân tích yêu cầu", [B1], None, {B1}, "giao_vai"),
    ("@labour_bot1 giao vai: phan tich yeu cau", [B1], None, {B1}, "giao_vai"),
    ("@labour_bot3 nhiệm vụ của bạn là review", [B3], None, set(), "giao_vai"),
    ("@labour_bot3 nhiem vu cua ban la review", [B3], None, set(), "giao_vai"),
    ("@labour_bot3 giao vài việc nhỏ", [B3], None, set(), "giao_viec"),        # vài ≠ vai
    # 10 sửa vai
    ("@labour_bot2 thêm việc phản biện", [B2], T("dang_lam"), {B2}, "sua_vai"),
    ("@labour_bot2 them viec phan bien", [B2], None, {B2}, "sua_vai"),
    ("@labour_bot2 bỏ việc dịch", [B2], None, {B2}, "sua_vai"),
    ("@labour_bot2 sửa vai: review kỹ hơn", [B2], None, {B2}, "sua_vai"),
    ("@labour_bot2 xem bộ hồ sơ vai trò", [B2], None, {B2}, "giao_viec"),      # bộ ≠ bỏ
    ("@labour_bot2 đối chiếu việc A với B", [B2], None, {B2}, "giao_viec"),    # đối ≠ đổi
    ("@labour_bot2 bo viec dich", [B2], None, {B2}, "giao_viec"),              # "bo" không dấu: mơ hồ
    ("@labour_bot2, thêm việc phản biện", [B2], None, {B2}, "sua_vai"),
    # lệnh 6–10 phải đứng đầu câu; nằm giữa câu là giao việc (review 1.1, B1)
    ("@labour_bot1 nhờ bot tóm tắt công việc tuần này", [B1], None, {B1}, "giao_viec"),
    ("@labour_bot1 thêm phần kết luận vào báo cáo công việc", [B1], None, {B1}, "giao_viec"),
    ("@labour_bot1 đổi font cho bảng nhiệm vụ", [B1], None, {B1}, "giao_viec"),
    ("@labour_bot1 dùng claude viết lại đoạn 2", [B1], None, {B1}, "giao_viec"),
    ("@labour_bot1 viết lại mục chốt số liệu", [B1], None, {B1}, "giao_viec"),
    ("@labour_bot3 đổi font cho bảng nhiệm vụ", [B3], None, set(), "giao_viec"),
    ("@labour_bot2 viết hướng dẫn dùng skill bao-cao", [B2], None, {B2}, "giao_viec"),
    ("@labour_bot2 dùng gemini nhé", [B2], None, {B2}, "doi_provider"),
    # review 1.1a: chữ không dấu / chữ gần giống không được đoán thành dừng, mở lại, chốt
    ("huy động thêm dữ liệu từ phòng B", [], T("dang_lam"), set(), "giao_viec"),   # huy động ≠ huỷ
    ("@labour_bot2 huy động thêm dữ liệu", [B2], T("dang_lam"), {B2}, "giao_viec"),
    ("huy đi", [], T("dang_lam"), set(), "dung"), ("huy viec", [], T("dang_lam"), set(), "dung"),
    ("hủy, làm cái khác", [], T("dang_lam"), set(), "dung"),                      # có dấu: vẫn nhận đầu câu
    ("không đặt tên file kiểu này nữa nhé", [], D, set(), "giao_viec"),            # đặt ≠ đạt: không mở lại
    ("bản này không đạt", [], D, set(), "mo_lai"),
    ("@labour_bot1 chót lại số liệu", [B1], None, {B1}, "giao_viec"),              # chót ≠ chốt
    ("@labour_bot1 chọt vào mục 2", [B1], None, {B1}, "giao_viec"),
    # 11 giao việc
    ("@labour_bot1 soạn bảng phản hồi từ input/nhan-xet.docx", [B1], None, {B1}, "giao_viec"),
    ("@labour_bot1 @labour_bot2 cùng xem mục 4", [B1, B2], None, {B1, B2}, "giao_viec"),
    ("làm tiếp đi", [], T("dang_lam"), {B2}, "giao_viec"),
    # 12 không
    ("hôm nay trời đẹp", [], None, set(), "khong"),
    ("ok", [], None, set(), "khong"),
]


@pytest.mark.parametrize("text,mentions,reply,roles,kind", CASES)
def test_classify(text, mentions, reply, roles, kind):
    assert classify(text, mentions, reply, lambda b: b in roles).kind == kind


def test_cases_are_many():
    assert len(CASES) >= 40


def test_confirm_kind():
    assert classify("ok", [], P, lambda b: False).confirm_kind == "vai"
    assert classify("ok", [], PC, lambda b: False).confirm_kind == "chot"


def test_giao_viec_bots_in_mention_order():
    assert classify("@b2 @b1 @b2 xem", ["b2", "b1", "b2"], None, lambda b: True).bots == ("b2", "b1")


def test_reply_to_bot_message_targets_that_bot():
    assert classify("làm tiếp đi", [], T("dang_lam"), lambda b: True).bots == ("labour_bot2",)


def test_reply_to_system_message_in_thread_has_no_bot():
    r = ReplyTarget("msg", 31, "cho_nguoi", "labour_bot1", True)
    i = classify("trả lời: chọn phương án A", [], r, lambda b: True)
    assert i.kind == "giao_viec" and i.bots == ()


def test_reply_to_system_message_outside_thread_is_nothing():
    r = ReplyTarget("msg", None, None, "labour_bot1", True)
    assert classify("cảm ơn", [], r, lambda b: True).kind == "khong"


def test_skill_and_provider_values():
    assert classify("@b dùng skill bao-cao", ["b"], None, lambda b: True).skill == "bao-cao"
    assert classify("@b chuyển sang Grok", ["b"], None, lambda b: True).provider == "grok"
