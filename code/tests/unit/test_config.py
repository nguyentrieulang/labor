from pathlib import Path

import pytest

from labour.app.config import ConfigError, bot_tokens, load_config

EX = Path(__file__).parents[2] / "config.example.yaml"
ENV = {"APPDATA": r"C:\Users\x\AppData\Roaming", **{f"BOT{i}_TOKEN": f"t{i}" for i in range(1, 5)}}


def test_load_example_values():
    c = load_config(EX, ENV)
    assert c.limits.max_concurrent_turns == 3 and c.limits.cli_turn_cap_default == 12
    assert c.limits.ask_cap == 3 and c.limits.review_cap == 3 and c.limits.turn_timeout_s == 900
    assert c.providers["noi_bo"] == ["claude"]
    assert c.claude.pinned_version == "2.1.328"
    assert str(c.claude.exe).startswith(r"C:\Users\x\AppData\Roaming")
    assert [b.username for b in c.bots] == ["labour_bot1", "labour_bot2", "labour_bot3", "labour_bot4"]


def test_missing_token_names_the_variable():
    c = load_config(EX, ENV)
    with pytest.raises(ConfigError, match="BOT2_TOKEN"):
        bot_tokens(c, {k: v for k, v in ENV.items() if k != "BOT2_TOKEN"})


def test_noi_bo_must_not_allow_grok(tmp_path):  # AD-21
    y = EX.read_text(encoding="utf-8").replace("noi_bo: [claude]", "noi_bo: [claude, grok]")
    p = tmp_path / "c.yaml"
    p.write_text(y, encoding="utf-8")
    with pytest.raises(ConfigError, match="grok"):
        load_config(p, ENV)


def test_duplicate_bot_username(tmp_path):
    y = EX.read_text(encoding="utf-8").replace("username: labour_bot2", "username: labour_bot1")
    p = tmp_path / "c.yaml"
    p.write_text(y, encoding="utf-8")
    with pytest.raises(ConfigError, match="labour_bot1"):
        load_config(p, ENV)


def test_bot_username_lowercased(tmp_path):
    y = EX.read_text(encoding="utf-8").replace("username: labour_bot2", "username: \"@Labour_Bot2\"")
    p = tmp_path / "c.yaml"
    p.write_text(y, encoding="utf-8")
    c = load_config(p, ENV)
    assert c.bots[1].username == "labour_bot2" and "labour_bot2" in bot_tokens(c, ENV)


def test_duplicate_bot_username_ignores_case(tmp_path):
    y = EX.read_text(encoding="utf-8").replace("username: labour_bot2", "username: LABOUR_BOT1")
    p = tmp_path / "c.yaml"
    p.write_text(y, encoding="utf-8")
    with pytest.raises(ConfigError, match="labour_bot1"):
        load_config(p, ENV)


def test_missing_section(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("instance: {data_dir: a, workspaces_dir: b}\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(p, ENV)
