import pytest

from labour.core.templates import REFUSALS, TEMPLATES, refusal, render


def test_all_templates_present():
    for code in [f"T{i:02d}" for i in range(1, 16)]:
        assert code in TEMPLATES


def test_render_t02_sanitizes_path():
    assert render("T02", vai="Phân tích", bot="labour_bot2", n=1, path="thao-luan/t3/9-ask-labour_bot2.md") == \
        "[Phân tích] Hỏi @labour_bot2 (1/3) – câu hỏi: 9-ask-labour_bot2.md"


def test_render_paths_list():
    assert render("T07", paths=["output/a b.docx", "output/c.docx"], who="@labour_bot3", r=2) == \
        "ĐẠT – a_b.docx, c.docx · duyệt: @labour_bot3 · 2 vòng"


def test_refusal():
    assert refusal("chi_chu_nhom") == "[Hệ thống] Lệnh này chỉ dành cho chủ nhóm"
    assert refusal("bot_chua_co_vai", bot="labour_bot2") == "[Hệ thống] @labour_bot2 chưa có vai"
    assert set(REFUSALS) >= {"chi_chu_nhom", "provider_chua_ho_tro", "provider_khong_duoc_phep",
                             "noi_bo_khong_nhan_file", "bot_chua_co_vai", "skill_khong_dung_duoc",
                             "dang_cho_xac_nhan_vai", "chi_trong_thoai_mai"}


def test_render_missing_var_raises():
    with pytest.raises(KeyError):
        render("T01", vai="X")


def test_render_unknown_code_raises():
    with pytest.raises(KeyError):
        render("T99")


def test_t14():
    assert render("T14", vai="Phản biện", co_reviewer=" (reviewer)", trich="phản biện bản nháp") == \
        "[Phản biện] Tôi nhận vai Phản biện (reviewer) – lời giao: “phản biện bản nháp”"
