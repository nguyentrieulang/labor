import json
from pathlib import Path

from labour.app.config import load_config
from labour.app.wiring import build_app, read_env_file
from labour.core.templates import TEMPLATES
from tests.fakes import FakeChannel, ev

EX = Path(__file__).parents[2] / "config.example.yaml"


def config(tmp_path):
    y = EX.read_text(encoding="utf-8")
    y = y.replace("C:/Works/Labour/data", (tmp_path / "data").as_posix())
    y = y.replace("C:/Works/Labour/workspaces", (tmp_path / "ws").as_posix())
    y = y.replace("outbox_min_interval_s: 3", "outbox_min_interval_s: 0")
    p = tmp_path / "config.yaml"
    p.write_text(y, encoding="utf-8")
    return load_config(p, {"APPDATA": "C:/x"})


async def test_build_app_with_fake_channel(tmp_path):
    cfg = config(tmp_path)
    ch = FakeChannel()
    app = await build_app(cfg, {}, ch)
    await app.ingest.on_event(ev(chat_id=-42, sender_user_id=123456789, command="start", chat_title="Thử"))
    assert ch.sent[0].text.startswith("[Hệ thống] Đã đăng ký nhóm – mức Nội bộ")
    assert (tmp_path / "data" / "labour.db").is_file()
    await app.ingest.on_event(ev(chat_id=-42, message_id=2, sender_user_id=123456789, command="status"))
    assert ch.sent[-1].text.startswith(TEMPLATES["S_STATUS"].split("{")[0])
    lines = [json.loads(x) for x in (tmp_path / "data" / "audit").glob("*.jsonl").__next__().read_text(
        encoding="utf-8").splitlines()]
    assert "group_registered" in [x["event"] for x in lines]


async def test_build_app_twice_reuses_db(tmp_path):
    cfg = config(tmp_path)
    await build_app(cfg, {}, FakeChannel())
    app = await build_app(cfg, {}, FakeChannel())
    with app.store.read() as s:
        assert len(app.store.bots.all(s)) == 4


def test_read_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("# chú thích\nBOT1_TOKEN=abc\nBOT2_TOKEN = \"x=y\"\n\n", encoding="utf-8")
    assert read_env_file(p) == {"BOT1_TOKEN": "abc", "BOT2_TOKEN": "x=y"}
    assert read_env_file(tmp_path / "none") == {}
