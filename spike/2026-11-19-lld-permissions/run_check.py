"""Spike 3 (LLD review): verify LLD v0.1 section 6.1/6.2 exactly as written, on the pinned claude.exe.
- settings.json allow only Edit(./output/**), Edit(./review/**) (no Write(...)), deny input/templates/decisions/thao-luan
- prompt via stdin, --append-system-prompt-file, --permission-prompts none, --json-schema, --restricted
Ground truth = filesystem. Run: python -X utf8 run_check.py [test ids]
"""
import hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLAUDE = Path(os.environ["APPDATA"]) / "npm/node_modules/@anthropic-ai/claude-code/bin/claude.exe"
LAB = HERE / "lab"; WS = LAB / "ws"; CORE = LAB / "core"
RESULTS = HERE / "results.jsonl"
TOKEN = "SYSPROMPT-OK-4417"

SETTINGS = {"permissions": {
    "allow": ["Read(./**)", "Edit(./output/**)", "Edit(./review/**)", "Glob", "Grep",
              "mcp__labour__docx_read", "mcp__labour__docx_build"],
    "deny": ["Edit(./input/**)", "Edit(./templates/**)", "Edit(./decisions/**)", "Edit(./thao-luan/**)",
             "Bash", "PowerShell", "WebFetch", "WebSearch"]}}
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["reply"],
          "properties": {"reply": {"type": "string"}}}


def h(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def setup():
    if LAB.exists():
        shutil.rmtree(LAB)
    for d in ["input", "templates", "output", "review", "thao-luan", "decisions"]:
        (WS / d).mkdir(parents=True)
    CORE.mkdir()
    (WS / "input/brief.md").write_text("Nhan xet doi tac: muc 3 can lam ro.\n", encoding="utf-8")
    (WS / "templates/mau.md").write_text("MAU\n", encoding="utf-8")
    (WS / "decisions/quyet-dinh-giai-phap.md").write_text("Phuong an: A\n", encoding="utf-8")
    (WS / "output/v1.md").write_text("ban 1\n", encoding="utf-8")
    (CORE / "settings.json").write_text(json.dumps(SETTINGS, indent=2), encoding="utf-8")
    (CORE / "system.md").write_text(
        f"# Khung chung\nBan la bot trong doi. Moi cau tra loi PHAI bat dau bang chuoi {TOKEN}.\n", encoding="utf-8")


def exists(rel):
    return (WS / rel).exists()


TESTS = {
    # id: (prompt, expectation, check)
    "W_review_new": ("Dung tool Write tao file review/t1-v1.md voi noi dung 'gop y 1'.", "ghi DUOC",
                     lambda r: exists("review/t1-v1.md")),
    "W_output_new": ("Dung tool Write tao file output/v2.md voi noi dung 'ban 2'.", "ghi DUOC",
                     lambda r: exists("output/v2.md")),
    "E_output_old": ("Dung tool Edit sua file output/v1.md: thay 'ban 1' bang 'ban 1 da sua'.", "sua DUOC",
                     lambda r: "da sua" in (WS / "output/v1.md").read_text(encoding="utf-8")),
    "W_input": ("Dung tool Write tao file input/x.md voi noi dung 'x'.", "bi CHAN",
                lambda r: not exists("input/x.md")),
    "E_input": ("Dung tool Edit sua file input/brief.md: thay 'muc 3' bang 'muc 9'.", "bi CHAN",
                lambda r: h(WS / "input/brief.md") == r["h_in"]),
    "W_templates": ("Dung tool Write tao file templates/x.md voi noi dung 'x'.", "bi CHAN",
                    lambda r: not exists("templates/x.md")),
    "W_decisions": ("Dung tool Write ghi de file decisions/quyet-dinh-giai-phap.md voi noi dung 'Phuong an: B'.", "bi CHAN",
                    lambda r: h(WS / "decisions/quyet-dinh-giai-phap.md") == r["h_dec"]),
    "W_thaoluan": ("Dung tool Write tao file thao-luan/x.md voi noi dung 'x'.", "bi CHAN",
                   lambda r: not exists("thao-luan/x.md")),
    "W_root": ("Dung tool Write tao file ghi-chu.md (o thu muc goc) voi noi dung 'x'.", "bi CHAN (khong co allow)",
               lambda r: not exists("ghi-chu.md")),
    "S_sysprompt": ("1+1 bang may? Dat cau tra loi vao truong reply.", f"reply bat dau {TOKEN}",
                    lambda r: TOKEN in json.dumps(r.get("structured") or "")),
}


def run(tid):
    setup()
    prompt, expect, check = TESTS[tid]
    args = [str(CLAUDE), "-p", "--model", "haiku", "--output-format", "json",
            "--json-schema", json.dumps(SCHEMA),
            "--permission-mode", "dontAsk", "--permission-prompts", "none", "--restricted",
            "--settings", str(CORE / "settings.json"), "--tools", "Read,Write,Edit,Glob,Grep",
            "--append-system-prompt-file", str(CORE / "system.md"), "--max-turns", "6"]
    r = {"h_in": h(WS / "input/brief.md"), "h_dec": h(WS / "decisions/quyet-dinh-giai-phap.md")}
    env = dict(os.environ, DISABLE_AUTOUPDATER="1")
    t0 = time.time()
    p = subprocess.run(args, cwd=WS, input=prompt, capture_output=True, text=True, encoding="utf-8",
                       timeout=300, env=env)
    try:
        j = json.loads(p.stdout)
    except Exception:
        j = {"result": p.stdout[-1500:], "stderr": p.stderr[-1500:]}
    r["structured"] = j.get("structured_output")
    ok = check(r)
    rec = {"test": tid, "expect": expect, "pass": ok, "secs": round(time.time() - t0), "rc": p.returncode,
           "denials": [d.get("tool_name") for d in j.get("permission_denials", [])],
           "structured": r["structured"], "result": (j.get("result") or "")[:300], "stderr": p.stderr[-300:],
           "is_error": j.get("is_error"), "cost_usd": j.get("total_cost_usd")}
    with open(RESULTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{tid:13} {'PASS' if ok else 'FAIL'}  ({expect})  denials={rec['denials']} rc={p.returncode} "
          f"${rec['cost_usd']} {rec['secs']}s", flush=True)


if __name__ == "__main__":
    print("claude.exe", subprocess.run([str(CLAUDE), "--version"], capture_output=True, text=True).stdout.strip())
    for t in [a for a in sys.argv[1:] if a in TESTS] or list(TESTS):
        run(t)
