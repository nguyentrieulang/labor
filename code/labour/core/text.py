"""Chuẩn hoá chữ tiếng Việt cho luật nhận diện ý và tên file/thư mục."""

from __future__ import annotations

import re
import unicodedata

_WS = re.compile(r"\s+")
_LEADING_MENTIONS = re.compile(r"^(\s*@\w+)+\s*")


def low(s: str) -> str:
    return _WS.sub(" ", unicodedata.normalize("NFC", s).lower()).strip()


def flat(s: str) -> str:
    d = unicodedata.normalize("NFD", low(s).replace("đ", "d"))
    return unicodedata.normalize("NFC", "".join(ch for ch in d if unicodedata.category(ch) != "Mn"))


def strip_mentions(s: str) -> str:
    return _LEADING_MENTIONS.sub("", s, count=1)


def slugify(s: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", flat(s)).strip("-")[:max_len].strip("-")
    return slug or "nhom"


def safe_basename(path: str, max_len: int = 60) -> str:
    base = re.split(r"[\\/]", path)[-1]
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", base)
    if len(safe) <= max_len:
        return safe
    stem, dot, ext = safe.rpartition(".")
    if dot and 0 < len(ext) < 10:
        return stem[: max_len - len(ext) - 1] + "." + ext
    return safe[:max_len]
