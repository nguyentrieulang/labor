"""Build the LLD .docx.  Run: python -X utf8 build_lld.py <out.docx>
Reuses the document helpers (H, P, B, T, FIG, toc, page_break) from ../hld-src/build_docx.py."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "..", "hld-src", "build_docx.py"), encoding="utf-8").read().split("# ================= COVER")[0]
__file__ = os.path.join(HERE, "build_lld.py")
exec(_src)                      # defines doc, H, P, B, T, FIG, toc, page_break, shade; IMG = HERE/img
from docx.shared import Pt, RGBColor


def CODE(text, size=8.5):
    for ln in text.strip("\n").split("\n"):
        if len(ln) > 92 and not ln.lstrip().startswith(("{", '"', "[")):
            print("LONG", len(ln), ln[:70])
        p = doc.add_paragraph()
        r = p.add_run(ln if ln else " "); r.font.name = "Consolas"; r.font.size = Pt(size)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        pf = p.paragraph_format; pf.space_after = Pt(0); pf.space_before = Pt(0); pf.left_indent = Cm(0.4)
        pPr = p._p.get_or_add_pPr(); s = OxmlElement("w:shd")
        s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), "F3F4F6"); pPr.append(s)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


# ================= COVER =================
for _ in range(5):
    doc.add_paragraph()
P("TÀI LIỆU THIẾT KẾ CHI TIẾT (LLD)", size=22, align=WD_ALIGN_PARAGRAPH.CENTER).runs[0].bold = True
P("Hệ thống Labour – Đội AI Agent trên Telegram", size=16, align=WD_ALIGN_PARAGRAPH.CENTER)
P("Yêu cầu v2.2 · Phương án A · Bản đầu (MVP) chạy trên VM Windows", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, italic=True)
doc.add_paragraph()
T(["Thuộc tính", "Giá trị"], [
    ["Phiên bản", "0.2 – đã áp góp ý review LLD v0.1"],
    ["Ngày", "19/11/2026"],
    ["Trạng thái", "Chờ review lần 2"],
    ["Tài liệu đầu vào", "HLD v0.6 (docs/2026-11-19-HLD-agent-team-v2.2-phuong-an-A-v0.6.docx); spike/2026-11-19-windows-denylist; spike/2026-11-19-docx-mcp; spike/2026-11-19-lld-permissions"],
    ["Phạm vi", "Chức năng phase M (bản đầu) của HLD: F-01..F-21, F-23..F-29. F-22 (lưu đội) và bản sản phẩm Docker chỉ ghi điểm mở rộng."],
    ["Người đọc", "Người viết mã và người review mã; người viết kế hoạch triển khai"],
    ["Tài liệu tiếp theo", "Kế hoạch triển khai (chia việc, thứ tự, tiêu chí xong từng bước)"],
], [4.5, 12.5], size=10)
page_break()
H("Mục lục", 1)
toc()
page_break()

# ================= 1 =================
H("1. Giới thiệu", 1)
H("1.1 Mục đích", 2)
P("LLD chuyển các quyết định của HLD v0.6 thành đặc tả đủ để viết mã: cấu trúc module, lược đồ CSDL, interface, "
  "lệnh gọi Claude Code, luật quyền, hợp đồng tín hiệu, mẫu tin, thuật toán xử lý tin và lượt, công cụ Word, "
  "lệnh chat, cấu hình, xử lý lỗi và bộ kiểm thử. Mọi mục đều trỏ về chức năng F-xx của HLD.")
H("1.2 Quy ước", 2)
B([("Tên mã ", "viết tiếng Anh (module, bảng, cột); giá trị liệt kê lưu trong CSDL dùng tiếng Việt không dấu như HLD (noi_bo, dang_lam…)."),
   ("Kiểu thời gian: ", "UTC, ISO 8601, lưu TEXT trong SQLite; hiển thị giờ Việt Nam (UTC+7)."),
   ("Đường dẫn ", "trong CSDL và tín hiệu luôn tương đối với gốc workspace của nhóm, dùng dấu “/”."),
   ("“Phải / không được” ", "là bắt buộc; “nên” là khuyến nghị; “[Kiểm chứng]” là giả định phải xác minh khi viết mã."),
   ("Tham chiếu: ", "F-xx = chức năng HLD mục 4; AD-xx = quyết định kiến trúc HLD mục 11; Hình HLD-n = hình trong HLD.")])
H("1.3 Bản đồ chức năng → mục LLD", 2)
T(["Chức năng (HLD)", "Mục LLD"], [
    ["F-01, F-02, F-04, F-05, F-28 – nhóm, mức bảo mật, truy cập, chủ nhóm, thành viên", "4, 7.1, 7.2, 11"],
    ["F-03 – bể bot; F-10 – định tuyến", "7.1–7.4, 12"],
    ["F-06..F-09 – vai, xác nhận, ghim, đổi provider", "7.3, 7.6, 9"],
    ["F-11, F-12, F-20 – chạy lượt, phiên, giới hạn", "5, 6, 7.5"],
    ["F-13, F-14, F-16, F-27 – hỏi nhau, leo thang, review, hiện review", "7.7, 7.8, 8"],
    ["F-15 – quyết định giải pháp", "7.9"],
    ["F-17, F-18, F-19 – file vào, giao kết quả, Gemini", "8, 12"],
    ["F-21, F-26 – audit, tra cứu", "4.3, 11"],
    ["F-23..F-25 – skill", "10"],
    ["F-29 – công cụ Word của lõi", "9"],
], [11.5, 5.5])
H("1.4 Thay đổi so với v0.1", 2)
T(["#", "Vấn đề review chỉ ra", "Sửa ở v0.2", "Mục"], [
    ["1", "Gắn Thread dùng ý định trước khi ý định được tính", "Phân loại ý trước, rồi mới gắn / mở Thread", "7.1, 7.4"],
    ["2", "/skill ở chat riêng không có đường vào; /start chat riêng có thể thành nhóm", "MessageEvent có chat_type; chat riêng chỉ nhận /skill của quản trị viên; /start chỉ group/supergroup", "5, 7.1, 11"],
    ["3", "Chủ nhóm trả lời khi Thread cho_nguoi không đưa bộ đếm về 0", "Lượt giao_viec vào Thread cho_nguoi gọi owner_replies_in trước khi tạo lượt", "7.5, 7.7"],
    ["4", "Trần 12 lượt CLI đếm lúc chạy, nhiều tin sát nhau vượt trần", "Giữ chỗ lúc tạo lượt (cùng transaction); hoàn khi lượt cho bị huỷ; ask giữ 2 suất mỗi bot", "7.5, 7.7"],
    ["5", "Grok, Gemini chưa có runtime", "UnsupportedRuntime trả UNSUPPORTED_PROVIDER; đổi provider → T13 “chưa hỗ trợ”; chính sách giữ nguyên", "6.8, 8.2, 13"],
    ["6", "Lượt diễn giải vai chờ trong on_event", "kind=dien_giai_vai đi qua scheduler, cwd data/tmp/empty, không giữ khoá nhóm", "6.7, 7.5"],
    ["7", "Sửa vai giữa chừng (R3) bị hiểu thành giao việc", "Ý sua_vai riêng: không mở Thread, không chạy lượt soạn", "7.3, 7.6"],
    ["8", "Mở Thread mới để Thread cũ vẫn dang_lam", "Mỗi nhóm tối đa một Thread mở; Thread cũ → huy, lượt cho bị huỷ, đăng T15", "7.4"],
    ["9", "Ask con lỗi / leo thang chưa rõ", "Không tạo tra_loi_ask; Thread cho_nguoi (error hoặc escalate)", "7.7"],
    ["10", "“Đạt” phụ thuộc trạng thái không có trong lược đồ", "Nhận reply “đạt” khi Thread dang_lam hoặc cho_nguoi", "7.3, 7.8"],
    ["11", "Tin xác nhận vai đăng chữ do model viết", "Mẫu T14: tên vai, cờ reviewer, trích đúng chữ chủ nhóm (lõi kiểm là chuỗi con); /vai cũng dùng chữ chủ nhóm", "7.6, 8.1, 11"],
    ["12", "Luật quyền 6.2 chưa được spike chứng minh; cờ CLI chưa kiểm", "Spike 3 chạy đúng settings.json và lệnh: 10/10 ca đạt trên 2.1.328", "6.1, 6.2"],
    ["13", "Thiếu pywin32, khoá ghi SQLite, kiểm quyền lệnh", "Thêm danh sách phụ thuộc; một khoá ghi; mọi lệnh tự kiểm quyền, có test", "2, 4, 11, 14"],
], [0.7, 5.6, 8.6, 2.1], size=8.5)

# ================= 2 =================
H("2. Cấu trúc mã nguồn", 1)
P("Một gói Python `labour` (Python 3.12, quản lý bằng uv). Quy tắc phụ thuộc giữ như HLD Hình 11: `core` chỉ import "
  "`ports`; adapter triển khai `ports`; `app` ghép nối. Công cụ Word là một chương trình riêng `labour.tools.docx_mcp`, "
  "do claude.exe khởi động mỗi lượt.")
FIG("l1_modules", "Hình 1. Các gói và module")
CODE("""
labour/
  app/            main.py (khởi động), wiring.py (tạo adapter, tiêm vào core), config.py (đọc config.yaml + .env)
  ports/          channel.py, runtime.py, repo.py, audit.py, workspace.py, skills.py, models.py (dataclass dùng chung)
  core/
    ingest.py     khử trùng lặp, kiểm soát truy cập, ghi group_log
    intents.py    nhận diện ý của tin chủ nhóm (mục 7.3)
    groups.py     đăng ký nhóm, mức bảo mật, thành viên, vai, xác nhận, ghim vai, provider
    threads.py    mở/gắn Thread, bộ đếm, ask, leo thang, review, đạt, mở lại
    scheduler.py  hàng đợi theo nhóm, khoá nhóm, suất đồng thời, khôi phục khi khởi động
    turns.py      dựng TurnRequest (ngữ cảnh, prompt), xử lý TurnResult, kiểm tín hiệu
    policy.py     mức bảo mật, danh sách provider, mẫu tin (mục 8)
    decisions.py  chốt quyết định, bản gốc, băm, khôi phục
    skills.py     nạp, kiểm tra, duyệt, gắn skill
    commands.py   phân lệnh chat + kiểm quyền từng lệnh; /vai, /skills, /status (mục 11)
    outbox.py     hàng tin ra: giãn nhịp, chia tin dài, ghim, gửi file
  adapters/
    telegram/     aiogram 3: poller nhiều bot, chuyển Update → MessageEvent, gửi tin
    claude_code/  ClaudeCodeRuntime: dựng lệnh, Job Object, đọc JSON kết quả, phân loại lỗi
    unsupported/  UnsupportedRuntime cho grok, gemini ở bản đầu (mục 6.8)
    storage/      SQLAlchemy models, Alembic migrations, AuditJsonl
    workspace/    tạo thư mục, sinh settings.json / mcp.json / system.md, liệt kê file đổi
  tools/
    docx_mcp/     server.py (MCP stdio), ops.py (thao tác python-docx), paths.py (kiểm đường dẫn)
tests/  unit/  integration/  security/  fixtures/
""")
P("Phụ thuộc (pyproject.toml): aiogram 3, SQLAlchemy 2 + aiosqlite, Alembic, pydantic 2, PyYAML, jsonschema, "
  "python-docx, pywin32 (Job Object – mục 6.1). Test: pytest, pytest-asyncio.")

# ================= 3 =================
H("3. Cấu hình và bố cục thư mục", 1)
H("3.1 config.yaml", 2)
CODE("""
instance:
  data_dir: C:/Works/Labour/data            # ngoài mọi workspace
  workspaces_dir: C:/Works/Labour/workspaces
telegram:
  bots:                                     # bể bot; token đọc từ biến môi trường
    - {username: labour_bot1, token_env: BOT1_TOKEN}
    - {username: labour_bot2, token_env: BOT2_TOKEN}
    - {username: labour_bot3, token_env: BOT3_TOKEN}
    - {username: labour_bot4, token_env: BOT4_TOKEN}
  poll_timeout_s: 30
users:
  - {tg_user_id: 123456789, name: "Chủ dự án", admin: true, can_create_group: true}
limits:
  max_concurrent_turns: 3                   # giữa các nhóm (AD-22)
  turn_timeout_s: 900
  ask_cap: 3
  review_cap: 3
  cli_turn_cap_default: 12                  # câu hỏi mở HLD – cấu hình được theo nhóm
  file_in_max_mb: 20
  outbox_min_interval_s: 3                  # mỗi chat
claude:
  exe: "%APPDATA%/npm/node_modules/@anthropic-ai/claude-code/bin/claude.exe"
  pinned_version: "2.1.328"                 # khởi động: so với `claude.exe --version`, lệch thì không chạy lượt
  model_default: sonnet
  model_light: haiku                        # lượt diễn giải vai
  max_agent_turns: 20                       # --max-turns của mỗi lượt
providers:
  noi_bo: [claude]                          # AD-21
  thoai_mai: [claude, grok, gemini]
""")
P(".env chỉ chứa bí mật: BOT1_TOKEN…BOTn_TOKEN; (bản sản phẩm) ANTHROPIC_API_KEY. Agent không đọc được .env vì file nằm "
  "ngoài workspace và lượt chạy --restricted (HLD mục 7.4).")
H("3.2 Thư mục data/ (chỉ lõi ghi)", 2)
CODE("""
data/
  labour.db                        CSDL SQLite (WAL)
  audit/audit-2026-11.jsonl        audit theo tháng, giữ ≥ 90 ngày
  skills/<tên>/<phiên bản>/        kho skill (SKILL.md + mẫu), chỉ quản trị viên
  groups/<group_id>/
    settings.json                  luật quyền của nhóm (mục 6.2)
    mcp.json                       cấu hình công cụ lõi, gốc = workspace của nhóm (mục 6.3)
    chi-dan.md                     chỉ dẫn nhóm (thay CLAUDE.md trong workspace)
    decisions/v<n>.md              bản gốc quyết định giải pháp (phiên bản n)
    turns/<turn_id>/system.md      prompt hệ thống của lượt (giữ 30 ngày để soát lỗi)
    turns/<turn_id>/result.json    JSON thô claude.exe trả về
  tmp/empty/                       thư mục trống cho lượt diễn giải vai và lượt Gemini
""")
H("3.3 Workspace của nhóm", 2)
T(["Thư mục", "Agent", "Lõi", "Nội dung"], [
    ["input/", "chỉ đọc", "ghi (file thả vào nhóm Thoải mái)", "tài liệu đầu vào"],
    ["templates/", "chỉ đọc", "—", "mẫu Word; người dùng chép tay"],
    ["output/", "ghi", "đọc", "kết quả bot soạn (docx qua công cụ lõi, md qua Write)"],
    ["review/", "ghi", "đọc", "góp ý review: review/t<thread>-v<round>.md"],
    ["thao-luan/", "chỉ đọc", "ghi", "nguyên văn reply / ask / leo thang: thao-luan/t<thread>/<turn>-<bot>.md"],
    ["decisions/", "chỉ đọc", "ghi (bản sao)", "quyet-dinh-giai-phap.md – bản sao của data/groups/<id>/decisions/v<n>.md"],
], [2.6, 2.2, 4.4, 7.8])
P("Tên thư mục workspace: slug từ tên nhóm Telegram lúc /start + “-” + group_id (ví dụ phan-hoi-doi-tac-x-7). Đổi tên nhóm "
  "Telegram sau đó không đổi thư mục.")

# ================= 4 =================
H("4. Lược đồ dữ liệu", 1)
FIG("l2_erd", "Hình 2. Lược đồ CSDL (SQLite, MVP)")
P("SQLite chạy chế độ WAL, foreign_keys=ON, busy_timeout=5000. Mọi bảng có created_at; bảng có trạng thái có updated_at. "
  "Migration bằng Alembic; đổi sang Postgres không đổi lõi (AD-06).")
P("Khoá ghi: mọi transaction ghi (ingest, scheduler, xử lý kết quả lượt, outbox ghi group_log) đi qua một asyncio.Lock "
  "duy nhất db_write trong tiến trình; đọc không cần khoá. Mỗi transaction ngắn, không await tiến trình con hay mạng bên trong.")
H("4.1 Bảng", 2)
TB = [
    ("users", [["id", "INTEGER PK", ""], ["tg_user_id", "INTEGER UQ NOT NULL", ""], ["display_name", "TEXT", ""],
               ["is_admin", "BOOL", "quản trị viên"], ["can_create_group", "BOOL", "được /start (F-01)"], ["active", "BOOL", "nạp từ config mỗi lần khởi động"]]),
    ("bots", [["id", "INTEGER PK", ""], ["username", "TEXT UQ", "không có @"], ["token_env", "TEXT", "tên biến môi trường"], ["tg_bot_id", "INTEGER", "lấy từ getMe"]]),
    ("groups", [["id", "INTEGER PK", ""], ["tg_chat_id", "INTEGER UQ", ""], ["title", "TEXT", "tên lúc /start"],
                ["owner_user_id", "FK users", ""], ["security_level", "TEXT CHECK (noi_bo, thoai_mai)", "mặc định noi_bo (AD-09)"],
                ["workspace_path", "TEXT", "tuyệt đối"], ["system_bot_id", "FK bots", "bot đăng tin [Hệ thống]: bot đã nhận /start"],
                ["allowed_providers", "JSON", "null = theo config.providers"], ["gemini_enabled", "BOOL", "chỉ có nghĩa khi thoai_mai"],
                ["cli_turn_cap", "INTEGER", "null = config"], ["status", "TEXT (active, archived)", ""]]),
    ("group_members", [["group_id, user_id", "PK, FK", ""], ["role", "TEXT (chu, thanh_vien)", "đúng một chu mỗi nhóm"], ["joined_at", "TEXT", ""]]),
    ("role_assignments", [["id", "INTEGER PK", ""], ["group_id, bot_id", "FK", ""], ["role_name", "TEXT", "tiền tố [Vai]"],
                          ["instructions", "TEXT", "do lượt diễn giải viết; chỉ vào system.md, không đăng ở nhóm Nội bộ"],
                          ["source_text, source_tg_msg_id", "TEXT, INTEGER", "đúng chữ chủ nhóm đã gõ (tin giao / sửa vai)"],
                          ["quote", "TEXT ≤ 300", "đoạn trích – lõi kiểm là chuỗi con của source_text (T14)"],
                          ["provider", "TEXT (claude, grok, gemini)", ""],
                          ["is_reviewer", "BOOL", ""], ["status", "TEXT (cho_xac_nhan, hieu_luc, thay_the)", "UQ (group_id, bot_id) khi hieu_luc"],
                          ["version", "INTEGER", "tăng mỗi lần sửa"]]),
    ("skills", [["id", "INTEGER PK", ""], ["name, version", "TEXT, UQ cặp", ""], ["description", "TEXT", ""], ["levels", "JSON", "[noi_bo, thoai_mai]"],
                ["tools", "JSON", "tên công cụ lõi cần"], ["status", "TEXT (cho_duyet, da_duyet, ngung)", ""], ["path, sha256", "TEXT", "băm cả thư mục"],
                ["check_report", "JSON", "kết quả kiểm tra tự động"], ["approved_by, approved_at", "", ""]]),
    ("role_skills", [["role_assignment_id, skill_id", "PK, FK", "skill theo tên; khi vai đổi version, lõi chép liên kết sang bản mới"]]),
    ("agent_sessions", [["group_id, bot_id", "PK", "AD: phiên theo (nhóm, bot)"], ["provider", "TEXT", ""], ["session_id", "TEXT", "từ JSON kết quả"],
                        ["fingerprint", "TEXT", "sha256(role version + skill ids + provider + decision version)"], ["last_used_at", "TEXT", ""]]),
    ("threads", [["id", "INTEGER PK", ""], ["group_id", "FK", ""], ["root_tg_msg_id", "INTEGER", "tin giao việc"], ["status", "TEXT (dang_lam, cho_nguoi, dat, huy)", ""],
                 ["wait_reason", "TEXT (ask_cap, review_cap, cli_cap, escalate, no_reviewer, error)", "khi cho_nguoi"],
                 ["waiting_bot_id", "FK bots", "bot chạy tiếp khi chủ nhóm trả lời (bot leo thang / bot hỏi)"],
                 ["closed_reason", "TEXT (thay_the, chu_dung)", "khi huy"],
                 ["ask_count, review_round", "INTEGER", "hai bộ đếm độc lập (HLD 6.7)"],
                 ["cli_turns", "INTEGER", "số lượt CLI đã giữ chỗ (tăng lúc tạo lượt, mục 7.5)"], ["cli_turn_cap", "INTEGER", "chép từ nhóm lúc mở"],
                 ["dat_tg_msg_id, approved_by", "", "tin ĐẠT, ai duyệt"]]),
    ("turns", [["id", "INTEGER PK", ""], ["thread_id, group_id, bot_id", "FK", "thread_id null với dien_giai_vai"], ["kind", "TEXT (thuong, ask, tra_loi_ask, review, sua, chot, dien_giai_vai)", ""],
               ["status", "TEXT (cho, dang_chay, xong, loi, huy)", "Hình 4"], ["parent_turn_id", "FK turns", "lượt sinh ra lượt này"],
               ["trigger_tg_msg_id", "INTEGER", ""], ["input_text", "TEXT", "tin cần xử lý"], ["pid", "INTEGER", ""],
               ["signal", "JSON", "structured_output đã kiểm"], ["files_changed", "JSON", ""], ["error_code", "TEXT", "mục 13"],
               ["cost_usd, num_turns, duration_ms", "", "từ JSON kết quả"], ["queued_at, started_at, finished_at", "TEXT", ""]]),
    ("reviews", [["id", "INTEGER PK", ""], ["thread_id, round", "", "UQ cặp"], ["files", "JSON", "từ request_review"], ["author_bot_id", "FK bots", "bot đã ghi các file đó"],
                 ["reviewer_bot_id", "FK bots", "null nếu chủ nhóm duyệt"], ["verdict", "TEXT (dat, chua_dat, null)", ""], ["notes_path", "TEXT", "review/…md"]]),
    ("decision_versions", [["id", "INTEGER PK", ""], ["group_id, version", "UQ", ""], ["sha256", "TEXT", ""], ["original_path", "TEXT", "data/groups/<id>/decisions/v<n>.md"],
                           ["source_path", "TEXT", "output/de-xuat-quyet-dinh.md lúc chốt"], ["confirmed_by, confirm_tg_msg_id", "", ""]]),
    ("group_log", [["id", "INTEGER PK", ""], ["group_id, thread_id", "FK", "thread null nếu chưa gắn"], ["tg_msg_id", "INTEGER", ""],
                   ["sender_kind", "TEXT (user, bot, system)", ""], ["sender_id", "INTEGER", ""], ["kind", "TEXT (chat, template, command)", ""],
                   ["text", "TEXT", "đúng chữ đã hiện trên Telegram"], ["reply_to_tg_msg_id", "INTEGER", "để gắn Thread"]]),
    ("pending_confirmations", [["id", "INTEGER PK", ""], ["group_id", "FK", ""], ["kind", "TEXT (vai, chot)", ""], ["tg_msg_id", "INTEGER", "tin chờ reply “ok”"],
                               ["payload", "JSON", "id vai / id lượt soạn quyết định"], ["status", "TEXT (cho, da_xac_nhan, het_han, thay_the)", ""], ["expires_at", "TEXT", "24 giờ"]]),
    ("processed_updates", [["chat_id, message_id", "PK", "khử trùng lặp; xoá bản ghi > 7 ngày"]]),
    ("pins", [["group_id, kind", "PK (kind: vai, dat)", ""], ["tg_msg_id, bot_id", "", "bot đã gửi tin (để sửa / gỡ)"]]),
]
for name, rows in TB:
    P(name, bold_prefix="")
    T(["Cột", "Kiểu / ràng buộc", "Ghi chú"], rows, [4.6, 5.6, 6.8], size=8.5)
H("4.2 Chỉ mục", 2)
B(["turns(status, group_id, queued_at) – scheduler lấy lượt kế tiếp.",
   "group_log(group_id, tg_msg_id) UQ – tra Thread theo tin reply.",
   "threads(group_id, status); role_assignments(group_id, status); pending_confirmations(group_id, tg_msg_id)."])
H("4.3 Bản ghi audit (jsonl)", 2)
P("Một dòng mỗi sự kiện. Không bao giờ ghi nội dung tài liệu; chỉ đường dẫn, băm và số đo (F-21, SEC-06).")
CODE("""
{"ts":"2026-11-19T08:15:02Z","event":"turn_finished","group_id":7,"thread_id":31,"turn_id":204,
 "bot":"labour_bot3","kind":"sua","provider":"claude","model":"sonnet","status":"xong","error_code":null,
 "signal":{"ask":0,"request_review":true,"verdict":null,"files":["output/phan_hoi_v2.docx"]},
 "files_changed":[{"path":"output/phan_hoi_v2.docx","sha256":"…"}],"skills":["docx@1.0.0"],
 "denials":[],"cost_usd":0.08,"num_turns":6,"duration_ms":28140,"claude_version":"2.1.328"}
""")
P("Các event: update_rejected, group_registered, member_added, role_proposed, role_confirmed, provider_changed, turn_queued, "
  "turn_started, turn_finished, turn_cancelled, signal_rejected, thread_state, thread_closed, decision_confirmed, decision_restored, skill_loaded, "
  "skill_approved, skill_retired, file_received, file_rejected, message_sent, startup, shutdown.", bold_prefix="")

# ================= 5 =================
H("5. Interface (labour.ports)", 1)
P("Viết bằng typing.Protocol và dataclass(frozen=True). Core chỉ thấy các kiểu dưới đây.")
CODE("""
@dataclass(frozen=True)
class MessageEvent:                      # do ChannelAdapter tạo
    chat_id: int; message_id: int; via_bot: str          # bot nhận update
    chat_type: Literal["private", "group", "supergroup", "channel"]
    sender_user_id: int | None; sender_is_bot: bool
    text: str; mentions: list[str]                        # username bot theo thứ tự xuất hiện
    reply_to_message_id: int | None
    file: IncomingFile | None                             # name, size, tg_file_id
    is_command: bool; command: str | None; args: list[str]

class ChannelAdapter(Protocol):
    async def start(self, on_event: Callable[[MessageEvent], Awaitable[None]]) -> None
    async def send_text(self, chat_id: int, bot: str, text: str, reply_to: int | None = None) -> int   # → message_id
    async def edit_text(self, chat_id: int, bot: str, message_id: int, text: str) -> None
    async def pin(self, chat_id: int, bot: str, message_id: int) -> None
    async def unpin(self, chat_id: int, bot: str, message_id: int) -> None
    async def send_file(self, chat_id: int, bot: str, path: Path, caption: str) -> int
    async def download(self, bot: str, f: IncomingFile, dest: Path) -> None

@dataclass(frozen=True)
class TurnRequest:
    turn_id: int; group_id: int; bot: str; provider: str; model: str
    workspace: Path                                        # cwd; dien_giai_vai = data/tmp/empty
    settings_path: Path; mcp_config_path: Path | None
    system_prompt_path: Path; prompt: str                 # prompt đi qua stdin
    session_id: str | None; signal_schema: dict; timeout_s: int; max_agent_turns: int
    tools: list[str]                                       # ["Read","Write","Edit","Glob","Grep"] hoặc []

@dataclass(frozen=True)
class TurnResult:
    ok: bool; error_code: str | None; error_detail: str | None
    signal: dict | None; text: str | None; session_id: str | None
    cost_usd: float | None; num_turns: int | None; duration_ms: int
    denials: list[dict]; raw_path: Path; quota_reset_at: datetime | None

class AgentRuntime(Protocol):
    name: str                                              # "claude" | "grok" | "gemini"
    async def run(self, req: TurnRequest, on_spawn: Callable[[int], None]) -> TurnResult
    async def kill(self, turn_id: int) -> None
    def version(self) -> str

class WorkspaceStore(Protocol):
    def create(self, group_id: int, slug: str) -> Path
    def write_turn_files(self, group, turn_id, system_prompt: str) -> tuple[Path, Path, Path]
    def snapshot(self, ws: Path) -> dict[str, str]          # path → sha256 cho output/, review/
    def diff(self, before: dict, after: dict) -> list[str]
    def write_text(self, ws: Path, rel: str, text: str) -> None   # chỉ lõi, thao-luan/
    def copy_decision(self, group_id: int, version: int) -> None
    def hash_decision_copy(self, group_id: int) -> str | None

class SkillStore(Protocol):
    def scan(self) -> list[SkillDir]
    def check(self, d: SkillDir) -> CheckReport
    def read_skill_md(self, name: str, version: str) -> str
""")
P("Repository: một lớp mỗi bảng (UsersRepo, GroupsRepo, …) với phương thức theo nhu cầu của core; mọi thao tác thay đổi "
  "trạng thái Thread + tạo lượt mới chạy trong một transaction.")

# ================= 6 =================
H("6. Chạy Claude Code (ClaudeCodeRuntime)", 1)
FIG("l3_turn", "Hình 3. Chạy một lượt agent")
H("6.1 Lệnh", 2)
P("Lõi gọi thẳng claude.exe (không qua claude.ps1 / claude.cmd), cwd = workspace của nhóm, prompt qua stdin để tránh "
  "giới hạn 32 767 ký tự của dòng lệnh Windows.")
CODE("""
claude.exe -p
  --model <sonnet|haiku>
  --output-format json
  --json-schema <chuỗi JSON của schema tín hiệu, mục 7.10>
  --permission-mode dontAsk --permission-prompts none
  --restricted
  --settings data/groups/<id>/settings.json
  --tools Read,Write,Edit,Glob,Grep              # lượt diễn giải vai / Gemini: --tools ""
  --mcp-config data/groups/<id>/mcp.json --strict-mcp-config
  --append-system-prompt-file data/groups/<id>/turns/<turn_id>/system.md
  --max-turns <limits.max_agent_turns>
  [--resume <session_id>]
Môi trường: DISABLE_AUTOUPDATER=1 (tên có trong claude.exe 2.1.328); không truyền token bot hay biến .env nào.
""")
P("Đã kiểm trên claude.exe 2.1.328 (spike/2026-11-19-lld-permissions): `-p` không kèm prompt đọc prompt từ stdin; "
  "--append-system-prompt-file, --permission-prompts none, --json-schema, --restricted, --settings và --tools chạy cùng nhau "
  "đúng như khối trên. Đổi pinned_version thì chạy lại bộ này (14.3).")
B([("Job Object: ", "tiến trình con được gán vào một Windows Job Object có JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE (pywin32). "
    "Đóng handle = giết cả cây (claude.exe + docx_mcp). Labour chết thì cây con cũng chết."),
   ("Quá giờ: ", "asyncio.wait_for(turn_timeout_s) → đóng Job → error_code TIMEOUT."),
   ("Kiểm phiên bản: ", "khi khởi động chạy `claude.exe --version`; khác pinned_version → không nhận lượt nào, báo quản trị viên (AD-20).")])
H("6.2 Luật quyền settings.json (sinh cho từng nhóm)", 2)
CODE("""
{
  "permissions": {
    "allow": ["Read(./**)", "Edit(./output/**)", "Edit(./review/**)", "Glob", "Grep",
              "mcp__labour__docx_read", "mcp__labour__docx_build"],
    "deny":  ["Edit(./input/**)", "Edit(./templates/**)", "Edit(./decisions/**)", "Edit(./thao-luan/**)",
              "Bash", "PowerShell", "WebFetch", "WebSearch"]
  }
}
""")
P("Spike 3 chạy đúng file trên (prompt qua stdin, chế độ dontAsk) – 10/10 ca đạt, kiểm bằng hệ thống file:")
T(["Thao tác của agent", "Kết quả"], [
    ["Write file mới review/…, output/…; Edit file có sẵn trong output/", "được – luật Edit(<thư mục>/**) cho cả Write, không cần Write(...)"],
    ["Write / Edit trong input/, templates/, decisions/, thao-luan/", "bị chặn (permission_denials ghi Write / Edit)"],
    ["Write ở gốc workspace (không có allow)", "bị chặn – dontAsk từ chối mọi thứ ngoài allow; deny là lớp thứ hai"],
], [8.0, 9.0], size=9)
P("Đọc ngoài workspace bị --restricted chặn sẵn (spike 1). Bash/PowerShell không có trong --tools. Mẫu settings.json là hằng "
  "trong adapters/workspace; sửa mẫu thì phải chạy lại tests/security trước khi phát hành.")
H("6.3 Cấu hình công cụ lõi mcp.json", 2)
CODE("""
{"mcpServers": {"labour": {
   "command": "<python.exe của venv labour>",
   "args": ["-X", "utf8", "-m", "labour.tools.docx_mcp", "--root", "<workspace tuyệt đối>",
            "--audit", "data/audit/mcp-<group_id>.jsonl"]}}}
""")
H("6.4 Prompt hệ thống của lượt (system.md)", 2)
P("Dựng bởi core/turns.py, theo thứ tự sau; mỗi phần có tiêu đề cố định để test so được:")
T(["#", "Phần", "Nguồn"], [
    ["1", "Khung chung: bạn là bot [Vai] trong đội; không có shell; Word chỉ qua docx_read / docx_build; chỉ ghi output/, review/; trả tín hiệu theo schema", "hằng số trong mã"],
    ["2", "Vai của bạn: role_name + instructions nguyên văn", "role_assignments"],
    ["3", "Các bot khác trong nhóm: @username – [Vai] – có là reviewer", "role_assignments"],
    ["4", "Mức bảo mật và hệ quả (Nội bộ: reply chỉ lưu vào file, không lên chat)", "groups"],
    ["5", "Chỉ dẫn nhóm", "data/groups/<id>/chi-dan.md"],
    ["6", "Quyết định giải pháp: đường dẫn decisions/quyet-dinh-giai-phap.md (đọc bằng Read) + phiên bản", "decision_versions"],
    ["7", "Skill đã gắn: nội dung SKILL.md (bỏ frontmatter), mỗi skill một mục", "role_skills + kho skill"],
    ["8", "Thread: loại lượt, bộ đếm hiện tại và trần, file đang review (nếu có)", "threads, reviews"],
    ["9", "Nhật ký gần nhất của Thread: tối đa 30 tin trong group_log (đúng chữ đã hiện trên chat)", "group_log"],
], [0.8, 11.0, 5.2])
P("Prompt (stdin) = tin cần xử lý: với lượt thường là tin của chủ nhóm; với lượt ask là câu hỏi của bot hỏi; với lượt "
  "trả lời ask là câu trả lời (đọc từ thao-luan/); với lượt review là danh sách file cần review; với lượt sửa là đường dẫn file góp ý.")
H("6.5 Đọc kết quả", 2)
T(["Trường JSON của claude.exe", "Dùng làm"], [
    ["is_error, subtype", "phân loại lỗi (mục 13)"],
    ["structured_output", "tín hiệu; kiểm lại bằng jsonschema phía lõi trước khi dùng"],
    ["result", "văn bản tự do; chỉ dùng khi structured_output thiếu để ghi chẩn đoán, không đăng"],
    ["session_id", "lưu agent_sessions"],
    ["total_cost_usd, num_turns, duration_ms", "turns + audit"],
    ["permission_denials", "audit; có denial với Edit ngoài output/review → ghi cảnh báo"],
], [5.5, 11.5])
P("Nhận diện hết hạn mức [Kiểm chứng]: is_error = true và result chứa “usage limit” (không phân biệt hoa thường); "
  "nếu có mốc thời gian dạng “|<epoch>” thì đọc làm quota_reset_at. Mẫu chuỗi phải chụp lại khi gặp lần đầu và đưa vào test.")
H("6.6 Phiên CLI", 2)
B(["fingerprint = sha256(role_assignments.version, danh sách skill id, provider, decision version hiện hành).",
   "Trước lượt: fingerprint khác bản lưu → bỏ session_id (lượt chạy không --resume), sau lượt lưu session mới.",
   "--resume thất bại (session không tồn tại) → chạy lại một lần không --resume, cùng turn_id; vẫn chỉ tính 1 lượt CLI."])
H("6.7 Lượt diễn giải vai (F-06, R3)", 2)
P("Là một turn kind=dien_giai_vai (thread_id null) đi qua scheduler như mọi lượt – on_event không bao giờ await lượt AI. "
  "model_light, cwd = data/tmp/empty, --tools \"\", không --mcp-config, không --resume. Không giữ khoá nhóm (không chạm "
  "workspace) nhưng chiếm một suất đồng thời; mỗi nhóm tối đa một lượt dien_giai_vai chạy cùng lúc. Prompt gồm lời của chủ "
  "nhóm, chế độ (giao_vai | sua_vai), danh sách bot trong nhóm (username + vai và instructions hiện tại). Schema kết quả:")
CODE("""
{"type":"object","additionalProperties":false,"required":["assignments","unclear"],
 "properties":{
   "assignments":{"type":"array","maxItems":8,"items":{"type":"object","additionalProperties":false,
       "required":["bot","role_name","instructions","quote","is_reviewer"],
       "properties":{"bot":{"type":"string"},"role_name":{"type":"string","maxLength":40},
                     "instructions":{"type":"string","maxLength":4000},
                     "quote":{"type":"string","maxLength":300},      # chép nguyên văn từ lời chủ nhóm
                     "is_reviewer":{"type":"boolean"},
                     "provider":{"type":["string","null"],"enum":["claude","grok","gemini",null]}}}},
   "unclear":{"type":"array","items":{"type":"string"}}}}
""")
B(["Lõi bỏ mọi assignment có bot không thuộc nhóm hoặc provider ngoài danh sách cho phép / chưa hỗ trợ (T13); còn unclear thì bot hệ thống hỏi lại chủ nhóm.",
   "quote: lõi chuẩn hoá khoảng trắng rồi kiểm là chuỗi con của source_text; không phải → thay bằng 200 ký tự đầu của source_text. role_name: chuẩn hoá về chữ, số, khoảng trắng, ≤ 40 ký tự.",
   "assignments rỗng (luật 9–10 nhận nhầm) → lõi xử lý lại chính tin đó như giao_viec (gắn / mở Thread, 7.4–7.5)."])
H("6.8 Provider chưa có runtime (bản đầu)", 2)
P("Bản đầu chỉ có ClaudeCodeRuntime. grok và gemini đăng ký UnsupportedRuntime: run() trả ngay TurnResult(ok=False, "
  "error_code=UNSUPPORTED_PROVIDER), không gọi tiến trình nào. Lớp chặn chính ở trước: đổi provider, /gemini bat hoặc lượt "
  "diễn giải gán grok/gemini → T13 “provider chưa hỗ trợ ở bản này”, vai giữ provider cũ. Không ai phải tự nghĩ lệnh CLI cho "
  "grok/gemini. Chính sách đã thiết kế (Gemini thư mục trống, prompt chỉ là tin vừa gửi; Grok cấm ở nhóm Nội bộ – AD-21) giữ "
  "nguyên ở policy.py để khi có runtime thật thì cắm vào không phải thiết kế lại.")

# ================= 7 =================
H("7. Xử lý tin và lượt", 1)
H("7.1 Đường đi của một tin", 2)
CODE("""
on_event(e):                          # ingest.py – không await lượt AI nào
  if not processed_updates.insert_if_absent(e.chat_id, e.message_id):
      return                           # tin đến qua nhiều bot
  if e.sender_is_bot: return           # tin của chính các bot: lõi đã biết
  user = users.by_tg(e.sender_user_id)
  if e.chat_type == "private":         # chat riêng: chỉ /skill của quản trị viên
      if user and user.is_admin and e.command == "skill":
          return skills_admin.dispatch(user, e)          # 10, 11
      audit("update_rejected"); return
  if e.chat_type not in ("group", "supergroup"):
      audit("update_rejected"); return
  group = groups.by_chat(e.chat_id)
  if e.command == "start": return groups.register(e, user)    # 7.2
  if user is None or group is None:
      audit("update_rejected"); return                     # im lặng
  members.ensure(group, user)          # F-28: thành viên mới → thanh_vien
  if e.file:
      group_log.add(group, e, None); return policy.receive_file(group, user, e)   # 8.3
  if e.is_command:
      group_log.add(group, e, None); return commands.dispatch(group, user, e)    # 11
  if user.id != group.owner_user_id:   # thành viên: chỉ nhật ký (AD-23)
      group_log.add(group, e, threads.of_reply(group, e)); return
  intent = intents.classify(group, e)          # 7.3 – TRƯỚC khi gắn Thread
  thread = threads.attach(group, e, intent)    # 7.4 – dùng intent
  group_log.add(group, e, thread)
  handlers[intent.kind](group, thread, e, intent)   # chỉ ghi CSDL + xếp lượt
""")
P("Thứ tự là bắt buộc: classify → attach → log → handler. Handler không chạy tiến trình con; mọi việc cần AI thành turn trong "
  "hàng đợi (7.5). intents.classify tự tra Thread của tin được reply (group_log) khi luật cần trạng thái Thread.")
H("7.2 Đăng ký nhóm (F-01, F-02)", 2)
B(["/start chỉ được xét khi chat_type ∈ {group, supergroup}; người gửi phải có can_create_group; nhóm chưa đăng ký. Không thoả → bot im lặng, audit.",
   "Tạo groups (security_level = noi_bo), group_members (chu), workspace (mục 3.3), data/groups/<id>/ (settings.json, mcp.json, chi-dan.md mẫu).",
   "Bot nhận /start trở thành system_bot. Đăng tin: “[Hệ thống] Đã đăng ký nhóm – mức Nội bộ. Đổi: /baomat thoai_mai. Thư mục: <workspace>”.",
   "Kiểm quyền bot trong nhóm (getChatMember): mọi bot trong bể có mặt phải tắt privacy mode hoặc là admin; bot hệ thống phải là admin để ghim. Thiếu → báo cụ thể bot nào."])
H("7.3 Nhận diện ý của chủ nhóm (intents.py)", 2)
P("Luật tất định, xét theo thứ tự; không gọi AI. Khớp luật đầu tiên thì dừng.")
T(["#", "Điều kiện", "Ý (intent)", "Xử lý"], [
    ["1", "Reply vào tin trong pending_confirmations (cho) và chữ khớp ^(ok|đồng ý|đúng|xác nhận)\\b", "xac_nhan", "kind vai → 7.6; kind chot → 7.9"],
    ["2", "Reply vào tin ĐẠT (pins.dat) và chữ chứa “không đạt”", "mo_lai", "7.8"],
    ["3", "Reply vào tin thuộc Thread có status dang_lam hoặc cho_nguoi và chữ là “đạt” (cả từ, không có “không”)", "dat", "7.8"],
    ["4", "Reply vào tin lỗi lượt (T10) và chữ khớp “chạy lại”", "chay_lai", "tạo lượt mới cùng kind, cùng input"],
    ["5", "Reply trong Thread và chữ khớp ^(dừng|huỷ|hủy)\\b", "dung", "lượt cho → huy (hoàn suất), dang_chay → kill; Thread → huy (chu_dung)"],
    ["6", "Có nhắc bot và chữ khớp \\bdùng (thêm )?skill [a-z0-9-]+", "gan_skill", "10.3 – không cần lượt AI"],
    ["7", "Có nhắc bot và chữ khớp \\b(dùng|chuyển sang) (claude|grok|gemini)\\b", "doi_provider", "F-09 qua policy (6.8)"],
    ["8", "Có nhắc bot và chữ chứa “chốt”", "chot", "7.9"],
    ["9", "Có nhắc bot và (chữ bắt đầu bằng “giao vai”, hoặc chứa “vai” / “nhiệm vụ” mà bot được nhắc chưa có vai hieu_luc)", "giao_vai", "6.7 (giao_vai) → 7.6"],
    ["10", "Có nhắc bot đã có vai và chữ khớp \\b(thêm|bớt|bỏ|đổi|sửa)\\b.*\\b(việc|vai|nhiệm vụ)\\b – xét cả khi bot đang có Thread dang_lam", "sua_vai", "6.7 (sua_vai) → 7.6; không mở Thread, không chạy lượt soạn"],
    ["11", "Có nhắc bot hoặc reply tin của bot", "giao_viec", "7.5"],
    ["12", "Còn lại", "khong", "chỉ nhật ký"],
], [0.7, 8.3, 2.4, 5.6], size=8.5)
P("Luật 9–10 có thể nhầm (ví dụ “thêm việc kiểm tra vai trò module X” là giao việc). Lượt diễn giải trả assignments rỗng → "
  "lõi xử lý lại tin đó như giao_viec, nên nhầm chỉ tốn một lượt haiku. Bộ test intents có ít nhất 40 câu mẫu tiếng Việt, "
  "cả có dấu và không dấu, gồm các câu “Bot2 thêm việc phản biện” khi Bot2 đang có Thread dang_lam.")
H("7.4 Gắn Thread", 2)
CODE("""
attach(group, e, intent):            # chỉ cho tin của chủ nhóm, sau classify
  if e.reply_to_message_id:
     t = group_log.thread_of(group, e.reply_to_message_id)
     if t and t.status in ("dang_lam", "cho_nguoi"): return t
     if t and t.status == "dat" and intent.kind == "mo_lai": return t
  if intent.kind in ("giao_viec", "chot"):
     threads.close_open(group, reason="thay_the")   # xem dưới
     return threads.open(group, root=e.message_id)  # ba bộ đếm = 0
  return None                    # gan_skill, giao_vai, sua_vai, doi_provider, khong…
""")
B([("Một Thread mở mỗi nhóm: ", "close_open chuyển mọi Thread dang_lam / cho_nguoi của nhóm sang huy (closed_reason = thay_the); "
    "lượt cho của chúng → huy; lượt dang_chay (nếu có) chạy nốt nhưng kết quả chỉ ghi nhật ký, audit và T01 – không tạo lượt "
    "tiếp, không review. Bot hệ thống đăng T15. Muốn tiếp việc cũ thì reply vào tin của Thread đó trước khi giao việc mới."),
   ("Reply vào tin của Thread đã huy hoặc dat ", "(không phải “không đạt”) mà có ý giao_viec → mở Thread mới như trên.")])
H("7.5 Tạo lượt và lập lịch (F-10, F-20, AD-22)", 2)
CODE("""
handle_giao_viec(group, thread, e):
  if thread.status == "cho_nguoi":
      threads.owner_replies_in(thread)         # 7.7 – reset đúng bộ đếm, → dang_lam
  bots = unique(e.mentions) or [bot của tin được reply] or [thread.waiting_bot]
  bots = [b for b in bots if has_active_role(b)]   # thiếu vai → T13 bot_chua_co_vai
  with db_write:                                   # một transaction
      if thread.cli_turns + len(bots) > thread.cli_turn_cap:
          return escalate(thread, "cli_cap")       # không tạo lượt nào
      thread.cli_turns += len(bots)                # GIỮ CHỖ ngay lúc tạo
      for b in bots: insert turn(kind="thuong", bot=b, status="cho", input=e.text)
""")
B([("Giữ chỗ trần CLI: ", "mọi chỗ tạo lượt trong Thread (thuong, chot, review, sua, chay_lai, ask) kiểm trần và tăng cli_turns "
    "trong cùng transaction với INSERT turns, nên tin gửi sát nhau thấy số đã giữ chỗ của nhau; vượt → escalate(cli_cap); "
    "lượt cho bị huỷ (dừng, Thread thay_the) → cli_turns − 1; lượt đã chạy (xong / loi) không hoàn. Ask giữ 2 suất mỗi bot được "
    "hỏi (7.7); lượt tra_loi_ask dùng suất đã giữ, không tăng thêm. Chạy lại khi SESSION_LOST không tính thêm. Lượt dien_giai_vai "
    "không thuộc Thread nên không tính."),
   ("Scheduler (một coroutine): ", "lặp khi có sự kiện turn_queued hoặc turn_finished: chọn turn cho cũ nhất của các nhóm không có "
    "turn dang_chay (trừ dien_giai_vai: chỉ cần nhóm không có dien_giai_vai đang chạy), tới khi số dang_chay = max_concurrent_turns."),
   ("Lấy turn: ", "UPDATE turns SET status='dang_chay', started_at=… WHERE id=? AND status='cho' (chống chạy trùng); không đổi cli_turns."),
   ("Khởi động: ", "UPDATE turns SET status='loi', error_code='RESTART' WHERE status='dang_chay'; đăng T10 cho từng lượt; không tự chạy lại.")])
FIG("l4_turn_state", "Hình 4. Trạng thái của một lượt (Turn)", width=14)
H("7.6 Vai: đề xuất, xác nhận, ghim (F-06..F-08)", 2)
B(["giao_vai và sua_vai đều qua lượt dien_giai_vai (6.7), khác chế độ: giao_vai thay cả vai; sua_vai đưa instructions hiện tại vào prompt và nhận bản instructions đã gộp. Cả hai không mở Thread, không chạy lượt soạn; Thread đang làm của bot vẫn chạy với vai cũ tới khi xác nhận.",
   "Sau lượt diễn giải: tạo role_assignments status=cho_xac_nhan (version = cũ + 1, source_text = tin chủ nhóm, quote đã kiểm); mỗi bot đăng T14. T14 chỉ chứa tên vai, cờ reviewer và quote – chữ chủ nhóm tự gõ – không chứa instructions do model viết, nên dùng được ở nhóm Nội bộ.",
   "Bot hệ thống đăng tin tổng hợp “Reply ‘ok’ vào tin này để áp dụng các vai trên” → pending_confirmations(kind=vai).",
   "Reply ok: các vai cho_xac_nhan → hieu_luc, vai cũ của cùng bot → thay_the; chép role_skills sang bản mới; xoá agent_sessions của các bot đó.",
   "Tin ghim vai: nếu pins(vai) đã có → edit_text bằng đúng bot đã gửi; chưa có → bot hệ thống gửi rồi ghim.",
   "Trước khi xác nhận, lượt mới cho bot đó vẫn dùng vai hieu_luc cũ; bot chưa từng có vai thì từ chối việc mới (“chờ xác nhận vai”).",
   "Hết hạn 24 giờ → het_han; vai cho_xac_nhan bị bỏ."])
H("7.7 Hỏi nhau và leo thang (F-13, F-14)", 2)
CODE("""
on_signal_ask(turn, asks):                         # asks: [{bot, question}]
  targets = unique(a.bot for a in asks if a.bot != turn.bot and has_active_role(a.bot))
  with db_write:
    n = len(targets)
    if thread.ask_count + n > ask_cap or thread.cli_turns + 2*n > cli_turn_cap:
        # không tạo lượt nào
        return escalate(thread, "ask_cap" | "cli_cap", waiting_bot=turn.bot)
    thread.ask_count += n
    thread.cli_turns += 2*n                        # giữ chỗ: lượt ask + lượt tra_loi_ask
    for a in asks (theo thứ tự, bỏ trùng):
        path = ws.write_text("thao-luan/t<thread>/<turn>-ask-<bot>.md", a.question)
        post(T02 | full text theo mức bảo mật)
        enqueue(kind="ask", bot=a.bot, input=path, parent=turn)

on_ask_child_done(child):                        # mỗi lượt ask con kết thúc
  sib = các lượt ask cùng parent
  if child.status == "loi":
      cancel(sib còn cho); escalate(thread, "error", waiting_bot=parent.bot)
  elif child.signal.escalate:
      cancel(sib còn cho); escalate(thread, "escalate", waiting_bot=child.bot)
  elif all(s.status == "xong" for s in sib):
      # dùng suất đã giữ
      enqueue(kind="tra_loi_ask", bot=parent.bot, input=các file trả lời)
  # lỗi / leo thang: KHÔNG tạo tra_loi_ask; suất đã giữ không hoàn

escalate(thread, reason, waiting_bot):
  status = cho_nguoi; wait_reason = reason; waiting_bot_id = waiting_bot
  post T03 (tag chủ nhóm)

owner_replies_in(thread):          # gọi từ handle_giao_viec (7.5) khi cho_nguoi
  match wait_reason:
    ask_cap    → ask_count = 0
    review_cap → review_round = 0
    cli_cap    → cli_turns = 0
    escalate | no_reviewer | error → không đổi bộ đếm
  status = dang_lam; wait_reason = null
  # sau đó handle_giao_viec tạo lượt (mặc định cho waiting_bot)
""")
P("Một ask tốn 2 lượt CLI (lượt bot được hỏi + lượt bot hỏi chạy tiếp) nên giữ chỗ 2 suất mỗi bot được hỏi ngay lúc tạo.")
H("7.8 Review, đạt, mở lại (F-16, F-27)", 2)
B(["request_review {files, note}: files phải nằm trong output/ và có trong files_changed của chính lượt này (tác giả = bot của lượt). Sai → signal_rejected.",
   "Chọn reviewer: bot có vai hieu_luc, is_reviewer = true, khác tác giả; nhiều bot → bot đầu tiên theo thứ tự giao vai. Không có → Thread cho_nguoi (no_reviewer), tag chủ nhóm.",
   "review_round + 1; vượt review_cap → cho_nguoi (review_cap, waiting_bot = tác giả). Trần CLI kiểm và giữ chỗ như 7.5. Tạo reviews(round, files, author, reviewer); đăng T04; enqueue kind=review.",
   "Lượt review phải trả verdict ∈ {dat, chua_dat} và ghi góp ý vào review/t<thread>-v<round>.md (lõi kiểm file tồn tại khi chua_dat).",
   "chua_dat → đăng T05; enqueue kind=sua cho tác giả, input = đường dẫn góp ý. Lượt sửa ghi bản mới (v2…) rồi request_review lại → đăng T06.",
   "dat từ reviewer → Thread dat; approved_by = bot reviewer; đăng T07 bằng bot hệ thống, ghim (pins.dat: gỡ ghim tin ĐẠT cũ của nhóm trước nếu có, không đụng tin ghim vai).",
   "dat từ chủ nhóm (luật 3: Thread dang_lam hoặc cho_nguoi): lượt cho của Thread → huy (hoàn suất), dang_chay → kill; review vòng hiện tại (nếu có) verdict = dat, reviewer_bot_id = null; paths = files của review mới nhất, không có thì hợp files_changed trong output/ của các lượt trong Thread; Thread dat; T07; ghim như trên.",
   "mo_lai: Thread dat → dang_lam; review_round = 0; gỡ ghim tin ĐẠT; enqueue kind=sua cho tác giả lần cuối với input = lời chủ nhóm."])
H("7.9 Chốt quyết định giải pháp (F-15, HLD Hình 9)", 2)
B(["Ý chot: enqueue kind=chot cho bot được nhắc; system prompt thêm yêu cầu ghi bản quyết định vào output/de-xuat-quyet-dinh.md.",
   "Lượt xong và file tồn tại → đăng T08, tạo pending_confirmations(kind=chot, payload=turn_id). Không có file → lỗi NO_DECISION_FILE.",
   "Reply ok: version = max + 1; chép file sang data/groups/<id>/decisions/v<n>.md; sha256; decision_versions; chép bản sao sang decisions/quyet-dinh-giai-phap.md; đăng T09; xoá agent_sessions cả nhóm (fingerprint đổi).",
   "Trước mỗi lượt (scheduler): băm decisions/quyet-dinh-giai-phap.md ≠ sha256 của bản mới nhất → không chạy, chép lại bản gốc, audit decision_restored, đăng mẫu T12, lượt → loi (DECISION_TAMPERED)."])
H("7.10 Hợp đồng tín hiệu", 2)
CODE("""
{"type":"object","additionalProperties":false,"required":["reply"],
 "properties":{
   "reply":{"type":"string","maxLength":8000},
   "ask":{"type":"array","maxItems":3,"items":{"type":"object","additionalProperties":false,
          "required":["bot","question"],"properties":{"bot":{"type":"string","pattern":"^@?[A-Za-z0-9_]{3,32}$"},
          "question":{"type":"string","maxLength":4000}}}},
   "escalate":{"type":["object","null"],"additionalProperties":false,"required":["reason","question"],
          "properties":{"reason":{"type":"string","maxLength":2000},"question":{"type":"string","maxLength":2000}}},
   "request_review":{"type":["object","null"],"additionalProperties":false,"required":["files"],
          "properties":{"files":{"type":"array","minItems":1,"maxItems":10,"items":{"type":"string"}},
                        "note":{"type":"string","maxLength":2000}}},
   "verdict":{"type":["string","null"],"enum":["dat","chua_dat",null]},
   "files":{"type":"array","maxItems":20,"items":{"type":"string"}}}}
""")
T(["Kiểm tra phía lõi (sau schema)", "Vi phạm →"], [
    ["Chỉ một trong {ask, escalate, request_review, verdict} khác rỗng", "signal_rejected, lượt loi (BAD_SIGNAL)"],
    ["verdict chỉ ở lượt kind=review; request_review không ở lượt review", "như trên"],
    ["Mọi đường dẫn: chuẩn hoá, nằm trong output/ hoặc review/, tồn tại", "như trên"],
    ["bot trong ask: thuộc nhóm, có vai hieu_luc, khác chính nó", "bỏ phần tử đó, audit"],
], [11.0, 6.0])

# ================= 8 =================
H("8. Chính sách bảo mật và mẫu tin (policy.py)", 1)
H("8.1 Mẫu tin cố định", 2)
P("Ở nhóm Nội bộ chỉ được đăng các mẫu dưới đây. Biến chỉ nhận giá trị lõi tự có: tên vai (do chủ nhóm đặt), username, "
  "con số, đường dẫn đã chuẩn hoá. Không biến nào lấy từ reply, câu ask, góp ý hay escalate.reason.")
T(["Mã", "Khi nào", "Nội dung (Nội bộ)"], [
    ["T01", "lượt xong, chỉ có reply", "[{vai}] Đã trả lời – xem {path}"],
    ["T02", "ask", "[{vai}] Hỏi @{bot} ({n}/3) – câu hỏi: {path}"],
    ["T03", "leo thang / chạm trần", "[Hệ thống] @{owner} cần quyết định ({ly_do_ma}) – xem {path}"],
    ["T04", "gửi review", "[{vai}] Xong {k} file → nhờ @{reviewer} review (vòng {r}/3): {paths}"],
    ["T05", "chưa đạt", "[{vai}] Vòng {r}/3: CHƯA ĐẠT – {k} góp ý: {path}"],
    ["T06", "đã sửa", "[{vai}] Đã sửa theo góp ý vòng {r_cu} → review lại (vòng {r}/3): {paths}"],
    ["T07", "đạt", "ĐẠT – {paths} · duyệt: {who} · {r} vòng"],
    ["T08", "bản quyết định", "[{vai}] Đã soạn bản quyết định: {path} – reply “ok” để chốt"],
    ["T09", "đã chốt", "[Hệ thống] Đã chốt quyết định giải pháp – phiên bản {n}"],
    ["T10", "lượt lỗi", "[Hệ thống] Lượt của @{bot} lỗi ({error_code}) – reply “chạy lại” để thử lại"],
    ["T11", "hết hạn mức", "[Hệ thống] Claude hết hạn mức đến {gio}. Provider được phép: {ds}"],
    ["T12", "file quyết định bị đổi", "[Hệ thống] File quyết định bị sửa ngoài hệ thống – đã khôi phục phiên bản {n}"],
    ["T13", "từ chối", "[Hệ thống] {ma_tu_choi}"],
    ["T14", "nhận vai (chờ xác nhận)", "[{vai}] Tôi nhận vai {vai}{co_reviewer} – lời giao: “{trich}”"],
    ["T15", "đóng Thread cũ", "[Hệ thống] Đã đóng việc #{thread_id} vì có việc mới – huỷ {k} lượt chờ"],
], [1.2, 3.6, 12.2], size=8.5)
P("ly_do_ma ∈ {het_luot_hoi, het_vong_review, het_luot_cli, bot_can_nguoi, khong_co_reviewer, loi_luot_hoi}. Đường dẫn file do "
  "agent đặt tên: hiển thị basename đã chuẩn hoá về [A-Za-z0-9._-], tối đa 60 ký tự (tên file cũng có thể mang nội dung).")
P("ma_tu_choi là câu cố định theo mã: chi_chu_nhom (“Lệnh này chỉ dành cho chủ nhóm”), provider_chua_ho_tro, "
  "provider_khong_duoc_phep, noi_bo_khong_nhan_file, bot_chua_co_vai (kèm @username), skill_khong_dung_duoc, "
  "dang_cho_xac_nhan_vai.")
P("T14: {co_reviewer} = “ (reviewer)” hoặc rỗng; {trich} = role_assignments.quote – đoạn lõi đã kiểm là chuỗi con của tin "
  "chủ nhóm (6.7). Đây là mẫu duy nhất mang chữ người dùng, và chỉ chữ của chủ nhóm; kiểm tra bảo mật số 5 miễn T14 nhưng "
  "có ca test riêng xác nhận {trich} ⊆ source_text.")
P("Nhóm Thoải mái: thay đường dẫn bằng nội dung (reply, câu ask, góp ý) và gửi file .docx kèm T04/T07; vẫn giữ tiền tố vai.")
H("8.2 Provider", 2)
B(["Danh sách hiệu lực = groups.allowed_providers ?? config.providers[security_level]; Gemini còn cần gemini_enabled.",
   "Đổi provider ngoài danh sách → T13 provider_khong_duoc_phep. Provider trong danh sách nhưng chưa có runtime (bản đầu: grok, gemini) → T13 provider_chua_ho_tro (6.8).",
   "Lượt Gemini (khi có runtime): cwd = data/tmp/empty, --tools \"\", prompt chỉ gồm tin vừa gửi (không nhật ký, không quyết định, không skill). Grok: không bao giờ ở nhóm Nội bộ (AD-21).",
   "Hết hạn mức (QUOTA): Thread giữ nguyên, lượt loi; T11 chỉ liệt kê provider trong danh sách hiệu lực ngoài Claude (Nội bộ mặc định: không có)."])
H("8.3 File vào / ra", 2)
B(["Nội bộ: mọi file thả vào → không tải, T13 “nhóm Nội bộ không nhận file qua Telegram”, audit file_rejected.",
   "Thoải mái: chủ nhóm hoặc thành viên; ≤ file_in_max_mb; tên chuẩn hoá; lưu input/<tên>, trùng tên thêm -2, -3.",
   "File ra: chỉ nhóm Thoải mái, chỉ file trong output/ có trong files_changed của lượt, ≤ 50 MB."])

# ================= 9 =================
H("9. Công cụ Word của lõi (labour.tools.docx_mcp)", 1)
P("Phát triển tiếp từ spike/2026-11-19-docx-mcp. MCP stdio, JSON-RPC 2.0 từng dòng; chỉ phụ thuộc python-docx.")
H("9.1 Ràng buộc đường dẫn", 2)
B(["Gốc = --root; mọi path tương đối, resolve() rồi bắt buộc relative_to(root); không theo symlink/junction ra ngoài (kiểm cả từng thành phần).",
   "Đọc: input/, templates/, output/. Ghi: chỉ output/. Chỉ đuôi .docx; ≤ 20 MB; không ghi đè file đã có (trả lỗi EXISTS).",
   "Không có thao tác nào chạm decisions/, review/, thao-luan/, data/."])
H("9.2 docx_read", 2)
P("Vào: {path}. Ra: danh sách khối [{i, type: paragraph, style, text, numbered} | {i, type: table, rows}]; header/footer "
  "trong trường riêng `sections`. Văn bản > 200 000 ký tự → cắt và báo truncated.")
H("9.3 docx_build", 2)
P("Vào: {template, output, operations[]} với `op` là enum bắt buộc (spike: bot gọi nhầm “type” khi schema lỏng). Mỗi op có schema riêng (oneOf):")
T(["op", "Tham số", "Ghi chú"], [
    ["replace_text", "find, replace", "trong đoạn văn, ô bảng, header/footer; giữ định dạng run đầu"],
    ["set_paragraph", "index, text", "index theo docx_read của template"],
    ["insert_paragraphs_after", "index, paragraphs[{text, style?}]", "style phải có trong template"],
    ["table_fill_rows", "table, rows[[…]], template_row?, remove_template_row?", "nhân bản dòng mẫu"],
    ["table_set_cell", "table, row, col, text", "mới so với spike"],
    ["delete_block", "index", "làm sau cùng"],
], [3.6, 6.0, 7.4], size=8.5)
P("Xử lý theo thứ tự; các op dùng index đều tham chiếu bản template ban đầu. Sửa bản cũ = docx_build(template=output/v1.docx, "
  "output=output/v2.docx, …). Lỗi trả isError=true kèm mã: OUTSIDE_ROOT, DIR_NOT_ALLOWED, NOT_DOCX, EXISTS, BAD_INDEX, "
  "BAD_STYLE, BAD_OP, TOO_LARGE.")
H("9.4 Ngoài phạm vi bản đầu", 2)
P("Ảnh, mục lục, đánh số tự động mới, tracked changes. Gặp mẫu thật cần các thao tác này thì thêm op mới (sửa lõi, AD-18).")

# ================= 10 =================
H("10. Skill", 1)
H("10.1 Định dạng", 2)
CODE("""
skills/bao-cao-doi-tac/1.0.0/
  SKILL.md
  mau/vi-du-phan-hoi.docx        (tuỳ chọn: tài liệu tham khảo, không phải mã)
---
name: bao-cao-doi-tac            # [a-z0-9-]{3,40}
version: 1.0.0                   # semver
description: Soạn bảng phản hồi nhận xét đối tác theo mẫu công ty
levels: [noi_bo, thoai_mai]
tools: [docx_read, docx_build]   # ⊆ công cụ lõi đang có
---
(hướng dẫn cho bot, tiếng Việt)
""")
H("10.2 Kiểm tra khi /skill nap", 2)
B(["Frontmatter hợp lệ; name/version chưa có; tools ⊆ công cụ lõi.",
   "Chỉ cho phép đuôi .md .txt .docx .xlsx .pdf .png .jpg; có file .py .js .ps1 .bat .cmd .sh .exe .dll .vbs hoặc file không đuôi → từ chối với lý do “skill có mã: cần viết thành công cụ của lõi”.",
   "Tổng ≤ 5 MB; SKILL.md ≤ 50 000 ký tự.",
   "Lưu check_report; status = cho_duyet. /skill duyet chỉ chạy được khi check_report đạt; sha256 thư mục được chốt lúc duyệt và kiểm lại mỗi lần nạp vào lượt (lệch → không nạp, báo quản trị viên)."])
H("10.3 Gắn và nạp", 2)
B(["“@Bot3 dùng thêm skill X” (ý gan_skill – luật 6 mục 7.3, không cần lượt AI): kiểm X da_duyet và levels chứa mức nhóm → role_skills; cập nhật tin ghim vai; xoá agent_sessions của bot.",
   "Nạp: system.md phần 7 chứa SKILL.md của mọi skill gắn với vai; file tham khảo trong skill không được chép vào workspace ở bản đầu.",
   "/skill ngung X: status ngung; xoá role_skills; báo trong các nhóm đang dùng."])

# ================= 11 =================
H("11. Lệnh trên chat", 1)
T(["Lệnh", "Ai", "Kết quả"], [
    ["/start", "User can_create_group; chỉ trong group / supergroup", "đăng ký nhóm (7.2)"],
    ["/baomat noi_bo | thoai_mai", "chủ nhóm", "đổi mức; về noi_bo thì gỡ gemini_enabled"],
    ["/gemini bat | tat", "chủ nhóm (chỉ Thoải mái)", "bản đầu: T13 provider_chua_ho_tro (6.8)"],
    ["/vai [@bot] [tatca]", "mọi thành viên", "bảng vai (HLD 5.6); tatca lọc theo group_members"],
    ["/skills", "mọi thành viên", "skill dùng được + skill gắn từng vai"],
    ["/status", "mọi thành viên", "Thread mở, lượt cho/dang_chay, bộ đếm, chi phí ngày"],
    ["/skill nap | duyet <tên>@<bản> | ngung <tên>", "quản trị viên, chat riêng (private) với bất kỳ bot nào trong bể", "10.2–10.3; ở nhóm thì bỏ qua"],
    ["/thanhvien them | bot @user", "chủ nhóm", "group_members"],
], [5.2, 4.4, 7.4], size=9)
P("Lệnh trả lời bằng bot hệ thống, đọc CSDL, không tạo lượt. commands.dispatch tra cột “Ai” cho từng lệnh trước khi chạy; "
  "không đủ quyền → T13 chi_chu_nhom (lệnh của chủ nhóm) hoặc im lặng (lệnh quản trị). Ở mọi mức bảo mật, /vai hiển thị "
  "tên vai, cờ reviewer, provider, skill và quote (chữ chủ nhóm) – không hiển thị instructions do model viết.")

# ================= 12 =================
H("12. Telegram adapter", 1)
B(["aiogram 3: một Dispatcher, n đối tượng Bot; dp.start_polling(*bots). Mỗi Update mang bot nhận → MessageEvent.via_bot; message.chat.type → chat_type.",
   "Mọi bot trong bể tắt privacy mode qua BotFather (để thấy tin không nhắc tên) [Kiểm chứng trong nhóm thử].",
   "mentions: lấy từ entities type=mention khớp username trong bể, giữ thứ tự xuất hiện; reply vào tin của bot X tính như nhắc X nếu không có mention nào.",
   "Outbox: hàng theo chat; khoảng cách tối thiểu outbox_min_interval_s; gặp 429 thì chờ retry_after; tin > 4 096 ký tự (chỉ Thoải mái) chia theo đoạn.",
   "Mọi tin gửi đi ghi group_log (kind=template hoặc chat) kèm tg_msg_id trả về, để gắn Thread khi chủ nhóm reply.",
   "Tải file: getFile ≤ 20 MB (giới hạn Bot API); gửi file ≤ 50 MB."])

# ================= 13 =================
H("13. Mã lỗi và xử lý", 1)
T(["error_code", "Phát hiện", "Xử lý"], [
    ["TIMEOUT", "quá turn_timeout_s", "đóng Job; lượt loi; T10"],
    ["RESTART", "khởi động thấy dang_chay", "lượt loi; T10"],
    ["QUOTA", "is_error + “usage limit” [Kiểm chứng]", "lượt loi; T11; không lượt mới cho provider đó tới quota_reset_at"],
    ["CLI_ERROR", "mã thoát ≠ 0 / is_error khác", "lượt loi; T10; lưu result.json"],
    ["BAD_JSON", "stdout không phải JSON", "như trên"],
    ["BAD_SIGNAL", "thiếu structured_output / sai schema / sai luật 7.10", "lượt loi; T10; không tạo lượt tiếp"],
    ["NO_DECISION_FILE", "lượt chot không có file", "lượt loi; T10"],
    ["DECISION_TAMPERED", "băm decisions/ lệch", "khôi phục; T12; lượt loi"],
    ["VERSION_MISMATCH", "claude.exe --version ≠ pinned", "không chạy lượt nào; báo quản trị viên"],
    ["SESSION_LOST", "--resume báo không có phiên", "chạy lại 1 lần không --resume (6.6)"],
    ["UNSUPPORTED_PROVIDER", "UnsupportedRuntime (grok, gemini ở bản đầu)", "lượt loi; T13 provider_chua_ho_tro; chỉ là lớp chặn thứ hai (6.8)"],
], [3.6, 6.0, 7.4], size=8.5)

# ================= 14 =================
H("14. Kiểm thử", 1)
H("14.1 Đơn vị (FakeChannel, FakeRuntime, SQLite :memory:)", 2)
T(["Nhóm test", "Ca chính"], [
    ["ingest", "trùng (chat_id, message_id) qua 3 bot → xử lý 1 lần; người lạ / nhóm lạ → im lặng + audit; "
               "chat riêng: /skill của quản trị viên tới skills_admin, /start và tin khác bị từ chối, không tạo groups; "
               "thứ tự classify → attach: tin giao việc đầu tiên mở Thread"],
    ["intents", "≥ 40 câu mẫu; reply ok đúng / sai tin; “không đạt” vs “đạt”; “đạt” khi Thread dang_lam và cho_nguoi; "
                "“@Bot2 thêm việc phản biện” khi Bot2 đang có Thread dang_lam → sua_vai; “dùng skill x” → gan_skill"],
    ["threads", "3 ask rồi ask thứ 4 → cho_nguoi; chủ nhóm reply → ask_count = 0, dang_lam, lượt mới cho waiting_bot, ask kế tiếp được chạy; "
                "ask hỏi 2 bot khi còn 1 suất → không tạo lượt nào; review 3 vòng; hai đếm độc lập; "
                "ask con lỗi → không có tra_loi_ask, cho_nguoi(error); giao việc mới → Thread cũ huy, lượt cho huỷ, T15"],
    ["trần CLI", "cli_turns = 11, ba tin giao việc gửi sát nhau (FakeChannel đẩy liên tiếp) → đúng 1 lượt được tạo, tổng ≤ 12; "
                 "lượt cho bị huỷ hoàn suất"],
    ["review", "tác giả không review chính mình; không có reviewer → tag chủ; mở lại từ dat; chủ nhóm “đạt” giữa vòng → huỷ lượt cho, T07"],
    ["scheduler", "2 bot cùng nhóm không chạy song song; 3 nhóm chạy song song; nhóm thứ 4 chờ; khởi động lại → loi; "
                  "FakeRuntime dien_giai_vai chậm 60 s không chặn on_event của tin khác"],
    ["policy", "mọi mẫu Nội bộ không chứa chuỗi đánh dấu đặt trong reply/ask/góp ý/instructions giả; tên file bị chuẩn hoá; "
               "T14: quote không phải chuỗi con → thay bằng đầu source_text; grok/gemini → T13 provider_chua_ho_tro"],
    ["commands", "/baomat, /gemini, /thanhvien từ thành viên thường → T13 chi_chu_nhom, không đổi CSDL; /vai ở nhóm Nội bộ không có instructions"],
    ["decisions", "chốt → v1; sửa bản sao → khôi phục + loi; fingerprint đổi → bỏ session"],
    ["skills", "skill có .py bị từ chối; tools lạ bị từ chối; sha256 lệch không nạp"],
    ["members", "tin thành viên nhắc bot → không có turn"],
], [3.0, 14.0], size=9)
H("14.2 Tích hợp", 2)
B(["ClaudeCodeRuntime với claude.exe thật (model haiku), workspace tạm: một lượt thường, một lượt có ask, một lượt review, một lượt docx_build.",
   "TelegramAdapter với nhóm thử và 2 bot thật: nhận, gửi, sửa, ghim, gỡ ghim, file vào/ra."])
H("14.3 Bảo mật – 6 kiểm tra của HLD mục 10 (tự động, chạy trước mỗi bản phát hành)", 2)
T(["#", "Kiểm tra", "Cách làm"], [
    ["1", "Người lạ, nhóm chưa đăng ký bị từ chối", "unit ingest + tích hợp Telegram"],
    ["2", "Không đọc workspace nhóm khác", "spike 1 T1, T7 với settings sinh từ mã thật"],
    ["3", "Nội bộ không nhận / gửi file", "unit policy + tích hợp"],
    ["4", "Không push / make / ghi ngoài workspace", "spike 1 T4, T5, T5b, T6 (cấu hình C)"],
    ["5", "Nội bộ không có nguyên văn / diễn giải", "FakeRuntime trả reply chứa chuỗi đánh dấu → kiểm group_log không chứa; claude thật với prompt cố tình chép tài liệu. Miễn T14 (chữ chủ nhóm), có ca riêng ở policy"],
    ["6", "Agent chỉ ghi output/, review/", "spike 3 (spike/2026-11-19-lld-permissions) với settings.json sinh từ mã thật: ghi được review/, output/; không ghi được input/, templates/, decisions/, thao-luan/, gốc workspace; docx_build ghi ra ngoài output/ → lỗi"],
], [0.8, 6.0, 10.2], size=9)
P("Bộ spike chuyển vào tests/security và chạy lại mỗi lần đổi pinned_version (AD-20).")

# ================= 15 =================
H("15. Cài đặt bản đầu trên VM", 1)
B(["Tạo venv bằng uv; `uv sync` (gồm pywin32); `alembic upgrade head`.",
   "Ghim Claude Code: cài đúng pinned_version qua npm; đặt DISABLE_AUTOUPDATER=1 ở mức người dùng (tên biến có trong 2.1.328; quan sát một tuần xem có tự cập nhật không); đăng nhập subscription một lần bằng `claude` tương tác.",
   "Tạo 4 bot qua BotFather, tắt privacy mode, ghi token vào .env; điền config.yaml.",
   "Chạy: `python -X utf8 -m labour.app`. Tự khởi động lại (tuỳ chọn): Task Scheduler “At log on” + restart on failure.",
   "Kiểm sau cài: /start ở nhóm thử; chạy tests/security."])

# ================= 16 =================
H("16. Vấn đề mở", 1)
T(["#", "Vấn đề", "Đề xuất / cách đóng"], [
    ["1", "Chuỗi lỗi hết hạn mức chính xác của claude.exe", "chụp khi gặp lần đầu; đưa vào test"],
    ["2", "DISABLE_AUTOUPDATER có thật sự chặn cập nhật (tên đã thấy trong 2.1.328)", "quan sát sau cài; nếu vẫn cập nhật, chặn bằng quyền thư mục npm; kiểm phiên bản lúc khởi động vẫn là lớp chặn"],
    ["3", "Luật intents tất định có thể nhầm", "đo trên 2 tuần dùng thật; cân nhắc lượt phân loại bằng haiku"],
    ["4", "Trần lượt CLI 12, số bot trong bể 4", "đo trong luồng thật (HLD câu hỏi mở)"],
    ["5", "Mẫu Word thật phức tạp", "thử mẫu thật đã lọc; thêm op cho docx_build"],
    ["6", "Điều khoản dùng subscription cho dịch vụ riêng", "giữ nguyên rủi ro HLD; bản bán dùng tài khoản của khách"],
    ["7", "Runtime Grok, Gemini; bản Docker", "ngoài vòng này; cắm vào AgentRuntime, chính sách đã có (6.8, 8.2)"],
    ["8", "Một Thread mở mỗi nhóm có thể chật khi giao nhiều việc song song", "đo khi dùng thật; nếu cần, cho nhiều Thread nhưng vẫn một lượt mỗi nhóm"],
], [0.8, 7.2, 9.0], size=9)

doc.save(OUT)
print("saved", OUT)
