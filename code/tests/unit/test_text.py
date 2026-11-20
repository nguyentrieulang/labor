from labour.core.text import flat, low, safe_basename, slugify, strip_mentions


def test_flat_and_low():
    assert flat("  Đạt!  ") == "dat!" and low("OK  Đạt") == "ok đạt"
    assert flat("dừng") == flat("dùng") == flat("đúng") == "dung"  # vì vậy intents dùng low() cho các từ này


def test_low_nfc():
    decomposed = "Đa\u0323t"  # "Đạt" dạng tổ hợp (NFD)
    assert low(decomposed) == "đạt"


def test_strip_mentions():
    assert strip_mentions("@labour_bot1  @labour_bot2 làm đi @x") == "làm đi @x"


def test_slugify():
    assert slugify("Phản hồi đối tác X") == "phan-hoi-doi-tac-x" and slugify("!!!") == "nhom"
    assert len(slugify("a" * 100)) == 40


def test_safe_basename():
    assert safe_basename("output/Bí mật: giá 5 tỷ.docx") == "B__m_t__gi__5_t_.docx"
    assert safe_basename("output\\sub\\x.md") == "x.md"
    long = safe_basename("output/" + "a" * 100 + ".docx")
    assert len(long) == 60 and long.endswith(".docx")
