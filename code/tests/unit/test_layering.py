from pathlib import Path

CORE = Path(__file__).parents[2] / "labour" / "core"


def test_core_imports_only_ports():
    files = list(CORE.rglob("*.py"))
    assert files
    for f in files:
        src = f.read_text(encoding="utf-8")
        assert "labour.adapters" not in src and "labour.app" not in src, f
