"""Diagrams for the LLD. Reuses svgkit from ../hld-src. Run: python -X utf8 lld_diagrams.py"""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hld-src"))
from svgkit import *

OUT = os.path.join(HERE, "img"); os.makedirs(OUT, exist_ok=True)
D = {}


def ent(x, y, w, name, attrs, kind="n"):
    h = 34 + 16 * len(attrs) + 8
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#ffffff" stroke="{ACC if kind=="core" else EDGE}" stroke-width="{2 if kind=="core" else 1.2}"/>',
         f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="6" fill="{ACC_FILL if kind=="core" else EXT_FILL}"/>',
         t(x + w / 2, y + 19, name, 13, 700)]
    for i, a in enumerate(attrs):
        s.append(t(x + 10, y + 46 + 16 * i, a, 11.5, 400, "start", QUIET))
    return "\n".join(s), h


# ---------- L1 modules ----------
b = []
b.append(box(380, 60, 340, 56, "labour.app", ["khởi động, đọc config, ghép nối, vòng đời"]))
b.append(container(20, 140, 1080, 236, "labour.core – nghiệp vụ, chỉ phụ thuộc labour.ports"))
core = [("ingest", ["khử trùng lặp, truy cập"]), ("intents", ["nhận diện ý của chủ nhóm"]),
        ("groups", ["nhóm, thành viên, vai"]), ("threads", ["Thread, đếm, review"]), ("scheduler", ["hàng đợi nhóm, worker"]),
        ("policy", ["mức bảo mật, mẫu tin"]), ("decisions", ["chốt, bản gốc, băm"]), ("skills", ["thư viện, gắn vai"]),
        ("commands", ["lệnh chat, kiểm quyền"]), ("outbox", ["gửi tin, ghim, giãn nhịp"])]
for i, (n, l) in enumerate(core):
    b.append(box(36 + (i % 5) * 212, 176 + (i // 5) * 96, 196, 72, n, l, "core"))
b.append(box(380, 400, 340, 56, "labour.ports", ["Protocol + dataclass dùng chung"], "core"))
b.append(container(20, 480, 1080, 120, "Adapter (triển khai ports)"))
ad = [("channels.telegram", ["aiogram 3"]), ("runtimes.claude_code", ["claude.exe -p"]), ("unsupported (grok, gemini)", ["bản đầu: trả UNSUPPORTED"]),
      ("storage", ["SQLAlchemy, Alembic, jsonl"]), ("workspace", ["thư mục, luật, MCP cfg"])]
for i, (n, l) in enumerate(ad):
    b.append(box(36 + i * 212, 516, 196, 64, n, l))
b.append(box(800, 630, 300, 64, "labour.tools.docx_mcp", ["tiến trình MCP stdio riêng mỗi lượt"], "core"))
b.append(line([(550, 116), (550, 140)]))
b.append(line([(550, 376), (550, 400)]))
b.append(line([(550, 480), (550, 456)], "triển khai", 560, 472, lanchor="start"))
b.append(line([(442, 580), (442, 662), (800, 662)], "claude.exe gọi qua --mcp-config", 600, 655))
D["l1_modules"] = svg(1120, 720, "\n".join(b), "Hình 1. Các gói và module",
                      "Mũi tên = phụ thuộc; core không import adapter; docx_mcp chạy thành tiến trình con của claude.exe")

# ---------- L2 ERD ----------
b = []
T = [
    ("users", 20, 70, ["id PK", "tg_user_id UQ", "is_admin, can_create_group"], "n"),
    ("bots", 20, 190, ["id PK", "username UQ, token_env"], "n"),
    ("groups", 290, 70, ["id PK, tg_chat_id UQ", "owner_user_id → users", "security_level, workspace_path", "allowed_providers, cli_turn_cap"], "core"),
    ("group_members", 20, 300, ["(group_id, user_id) PK", "role: chu | thanh_vien"], "n"),
    ("role_assignments", 560, 70, ["id PK, group_id, bot_id", "role_name, instructions, quote", "provider, is_reviewer", "status, version"], "core"),
    ("skills", 830, 70, ["id PK, (name, version) UQ", "levels, tools, status", "sha256, approved_by"], "n"),
    ("role_skills", 830, 210, ["(role_assignment_id,", " skill_id) PK"], "n"),
    ("agent_sessions", 830, 320, ["(group_id, bot_id) PK", "provider, session_id", "fingerprint"], "n"),
    ("threads", 290, 250, ["id PK, group_id", "status, wait_reason, waiting_bot", "ask_count, review_round", "cli_turns (giữ chỗ)"], "core"),
    ("turns", 560, 250, ["id PK, thread_id, bot_id", "kind, status, pid", "signal JSON, files JSON", "error_code, cost_usd"], "core"),
    ("reviews", 560, 430, ["id PK, thread_id, round", "files, author_bot_id", "reviewer_bot_id, verdict"], "n"),
    ("decision_versions", 290, 430, ["id PK, group_id, version", "sha256, original_path", "confirmed_by"], "n"),
    ("group_log", 20, 430, ["id PK, group_id, thread_id", "tg_msg_id, sender", "kind, text"], "n"),
    ("pending_confirmations", 830, 430, ["id PK, group_id, kind", "tg_msg_id, payload", "status, expires_at"], "n"),
    ("processed_updates", 20, 560, ["(chat_id, message_id) PK"], "n"),
    ("pins", 290, 560, ["(group_id, kind) PK", "tg_msg_id, bot_id"], "n"),
]
for n, x, y, a, k in T:
    s, h = ent(x, y, 250, n, a, k); b.append(s)
D["l2_erd"] = svg(1100, 650, "\n".join(b), "Hình 2. Lược đồ CSDL (SQLite, MVP)",
                  "Khoá ngoại ghi trong ô (→); chi tiết cột ở mục 4. Xanh = bảng lõi")

# ---------- L3 turn sequence ----------
D["l3_turn"] = sequence(
    [("sch", "Scheduler", "worker"), ("rt", "ClaudeCodeRuntime", None), ("ws", "WorkspaceStore", "data/ + workspace"),
     ("cli", "claude.exe -p", "tiến trình con"), ("mcp", "docx_mcp", "tiến trình con"), ("th", "Threads + Policy", None)],
    [("m", "sch", "ws", "kiểm băm decisions/ với bản gốc", False),
     ("m", "sch", "rt", "run(TurnRequest) – đã giữ khoá nhóm + suất đồng thời", False),
     ("m", "rt", "ws", "ghi system.md, settings.json, mcp.json của lượt", False),
     ("m", "rt", "cli", "spawn trong Job Object; prompt qua stdin; cwd = workspace", False),
     ("m", "cli", "mcp", "khởi động theo --mcp-config (gốc = workspace)", False),
     ("m", "cli", "mcp", "docx_read / docx_build (tự kiểm đường dẫn)", False),
     ("m", "cli", "rt", "JSON kết quả: structured_output, session_id, cost, denials", True),
     ("m", "rt", "ws", "liệt kê file đổi trong output/, review/", False),
     ("m", "rt", "sch", "TurnResult (ok | loi + error_code)", True),
     ("m", "sch", "th", "handle_result: kiểm tín hiệu → lượt mới / leo thang / review / đạt", False),
     ("self", "sch", "nhả khoá nhóm; lấy lượt kế tiếp"),
     ("note", "sch", "th", "Quá giờ → huỷ Job Object (giết cả cây tiến trình), lượt = loi, không tự chạy lại")],
    1160, "Hình 3. Chạy một lượt agent")

# ---------- L4 turn states ----------
b = []
b.append('<circle cx="50" cy="150" r="9" fill="#1f2937"/>')
b.append(box(130, 120, 160, 60, "cho", ["trong hàng đợi nhóm"]))
b.append(box(420, 120, 170, 60, "dang_chay", ["có pid, started_at"], "core"))
b.append(box(720, 50, 150, 60, "xong", ["có signal"]))
b.append(box(720, 190, 150, 60, "loi", ["error_code"]))
b.append(box(130, 270, 160, 56, "huy", ["chủ nhóm dừng"]))
b.append(line([(59, 150), (130, 150)]))
b.append(line([(290, 150), (420, 150)], "khoá nhóm rảnh +\nsuất đồng thời", 355, 128))
b.append(line([(590, 140), (720, 80)], "thoát, JSON hợp lệ", 655, 70, lanchor="end"))
b.append(line([(590, 165), (720, 220)], "lỗi CLI / sai schema /\nquá giờ / khởi động lại", 700, 262, lanchor="end"))
b.append(line([(210, 180), (210, 270)], "dừng / huỷ", 220, 230, lanchor="start"))
b.append(line([(505, 180), (505, 298), (290, 298)], "dừng: kill", 400, 292))
b.append(line([(795, 250), (795, 360), (100, 360), (100, 168), (130, 168)], "chủ nhóm “chạy lại” → tạo lượt MỚI", 450, 378))
D["l4_turn_state"] = svg(900, 400, "\n".join(b), "Hình 4. Trạng thái của một lượt (Turn)",
                         "Không có đường tự động từ loi về cho: chạy lại luôn tạo lượt mới do chủ nhóm yêu cầu")

chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
for name, s in D.items():
    p = os.path.join(OUT, name + ".svg"); open(p, "w", encoding="utf-8").write(s)
    w = int(re.search(r'width="(\d+)"', s).group(1)); h = int(re.search(r'height="(\d+)"', s).group(1))
    html = os.path.join(OUT, name + ".html")
    open(html, "w", encoding="utf-8").write(f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;padding:0;overflow:hidden}}</style>{s}')
    png = os.path.join(OUT, name + ".png")
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--screenshot={png}",
                    f"--window-size={w},{h}", "--force-device-scale-factor=2", "file:///" + html.replace("\\", "/")],
                   capture_output=True, timeout=60)
    print(name, w, h, os.path.exists(png))
