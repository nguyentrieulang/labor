import os, re, subprocess, sys
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)
D = {}

# ---------- H1 Context ----------
b = []
b.append(actor(75, 120, "Chủ nhóm", "(kỹ sư tạo nhóm)"))
b.append(actor(75, 290, "Kỹ sư thành viên"))
b.append(actor(75, 470, "Quản trị viên"))
b.append(box(190, 175, 170, 120, "Telegram", ["Nhóm chat", "+ bể bot", "Bot API"], "ext"))
b.append(box(450, 175, 230, 120, "Hệ thống Labour", ["Điều phối đội AI agent", "Một dịch vụ Python"], "core"))
b.append(box(760, 60, 260, 60, "AI cloud của nhà cung cấp", ["Anthropic · xAI · Google"], "ext"))
b.append(box(760, 150, 260, 80, "Claude Code CLI", ["claude -p, gói subscription", "mặc định cho mọi vai"]))
b.append(box(760, 255, 260, 66, "Cursor CLI (Grok)", ["cursor-agent – tuỳ chọn"]))
b.append(box(760, 345, 260, 66, "Gemini CLI", ["chỉ nhóm Thoải mái, tắt mặc định"]))
b.append(box(450, 450, 230, 90, "Workspace nhóm", ["input/ · output/ · decisions/", "chủ nhóm mở bằng Word"], "ext"))
b.append(box(190, 450, 170, 80, "Cấu hình + skills/", ["User, bể bot, giới hạn", "thư viện skill"], "ext"))
b.append(line([(118, 160), (190, 205)], "giao vai, giao việc,\nduyệt, nói “đạt”", 118, 132, lanchor="start"))
b.append(line([(118, 325), (190, 268)], "trao đổi, góp ý", 120, 345, lanchor="start"))
b.append(line([(118, 505), (190, 490)], "khai báo,\nthêm skill", 150, 530))
b.append(line([(360, 235), (450, 235)], "tin nhắn", 405, 228, both=True))
b.append(line([(360, 475), (415, 475), (415, 275), (450, 275)], "nạp cấu hình", 388, 380, lanchor="end"))
b.append(line([(680, 235), (720, 235), (720, 190), (760, 190)]))
b.append(line([(720, 235), (720, 288), (760, 288)]))
b.append(line([(720, 288), (720, 378), (760, 378)], "gọi 1 lượt\nagent", 712, 330, lanchor="end"))
b.append(line([(890, 150), (890, 120)], "HTTPS", 900, 140, lanchor="start"))
b.append(line([(890, 411), (890, 495), (680, 495)], "đọc / ghi file", 790, 488))
b.append(line([(565, 295), (565, 450)], "tạo thư mục,\nkhoá quyết định", 575, 360, lanchor="start"))
D["h1_context"] = svg(1040, 580, "\n".join(b), "Hình 1. Ngữ cảnh hệ thống",
                      "Hệ thống đứng giữa nhóm Telegram và các agent CLI; tài liệu chỉ nằm trong workspace trên đĩa")

# ---------- H2 Logical components ----------
b = []
W4 = 224
xs4 = [46 + i * (W4 + 24) for i in range(4)]
b.append(container(30, 64, 1000, 100, "Bộ nối kênh  «ChannelAdapter»"))
b.append(box(xs4[0], 96, W4, 56, "TelegramAdapter", ["aiogram 3, nhiều bot, long polling"]))
b.append(box(xs4[1], 96, W4, 56, "Khử trùng lặp tin", ["theo (chat_id, message_id)"]))
b.append(box(xs4[2], 96, W4 * 2 + 24, 56, "TeamsAdapter / SlackAdapter / Web (sau)", [], "fut"))
b.append(container(30, 196, 1000, 318, "Lõi điều phối (không phụ thuộc kênh hay nhà cung cấp AI)"))
core1 = [("Kiểm soát truy cập", ["allowlist người + nhóm", "quyền chủ nhóm"]),
         ("Nhóm & vai", ["đăng ký nhóm, mức bảo mật", "diễn giải lời giao vai"]),
         ("Định tuyến lượt", ["mention / reply → bot", "dựng ngữ cảnh cho lượt"]),
         ("Điều phối Thread", ["hỏi nhau ≤ 3, leo thang", "review → đạt"])]
core2 = [("Chính sách bảo mật", ["Nội bộ / Thoải mái", "lọc tin ra, chặn file"]),
         ("Quyết định giải pháp", ["ghi, khoá, phát hiện", "agent tự sửa"]),
         ("Hàng đợi & lập lịch", ["một lượt / nhóm tại một lúc", "tối đa 3 lượt đồng thời"]),
         ("Theo dõi hạn mức", ["báo hết hạn mức", "hỏi đổi provider"])]
for i, (n, l) in enumerate(core1):
    b.append(box(xs4[i], 228, W4, 80, n, l, "core"))
for i, (n, l) in enumerate(core2):
    b.append(box(xs4[i], 324, W4, 80, n, l, "core"))
core3 = [("Thư viện skill", ["danh mục, kiểm tra, duyệt", "gắn skill cho vai"]),
         ("Tra cứu vai & trạng thái", ["/vai, /skills, /status", "đọc CSDL, không chạy AI"]),
         ("Bộ gửi tin", ["đăng đúng bot, tiền tố [Vai]", "hiện từng bước review"]),
         ("Công cụ của lõi (MCP)", ["docx_read, docx_build", "agent không có shell"])]
for i, (n, l) in enumerate(core3):
    b.append(box(xs4[i], 420, W4, 80, n, l, "core"))
b.append(container(30, 546, 1000, 100, "Bộ nối AI  «AgentRuntime»"))
rt = [("ClaudeCodeRuntime", ["claude -p --resume"], "n"), ("CursorRuntime (Grok)", ["cursor-agent"], "n"),
      ("GeminiRuntime", ["Gemini CLI"], "n"), ("AgentSdkRuntime (sau)", ["API key của khách"], "fut")]
for i, (n, l, k) in enumerate(rt):
    b.append(box(xs4[i], 578, W4, 56, n, l, k))
b.append(container(30, 678, 1000, 100, "Hạ tầng"))
inf = [("Repository", ["SQLite → Postgres"]), ("AuditLog", ["audit.jsonl"]),
       ("WorkspaceManager", ["thư mục, CLAUDE.md,", "deny-list, cài skill"]), ("Kho skill", ["skills/<tên>/<phiên bản>"]),
       ("Cấu hình & bí mật", ["config.yaml, .env"])]
W5 = 180
for i, (n, l) in enumerate(inf):
    b.append(box(46 + i * (W5 + 15), 708, W5, 60, n, l))
b.append(line([(530, 164), (530, 196)], both=True))
b.append(line([(530, 514), (530, 546)]))
b.append(line([(1030, 420), (1060, 420), (1060, 728), (1030, 728)], "đọc/ghi", 1066, 580, lanchor="start"))
D["h2_logical"] = svg(1120, 800, "\n".join(b), "Hình 2. Logical view – các khối chức năng",
                      "Khối xanh = lõi (giá trị riêng của sản phẩm); viền đứt = làm sau")

# ---------- H3 Domain model ----------
b = []
def ent(x, y, w, name, attrs, kind="n"):
    h = 34 + 16 * len(attrs) + 8
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#ffffff" stroke="{ACC if kind=="core" else EDGE}" stroke-width="{2 if kind=="core" else 1.2}"/>',
         f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="6" fill="{ACC_FILL if kind=="core" else EXT_FILL}"/>',
         t(x + w / 2, y + 19, name, 13, 700)]
    for i, a in enumerate(attrs):
        s.append(t(x + 10, y + 46 + 16 * i, a, 11.5, 400, "start", QUIET))
    return "\n".join(s), h
e = {}
for key, x, y, w, name, attrs, k in [
    ("user", 40, 70, 210, "User", ["telegram_user_id", "là_quản_trị, được_tạo_nhóm"], "n"),
    ("group", 420, 70, 230, "Group (nhóm)", ["chat_id", "owner_user_id (chủ)", "security_level: noi_bo|thoai_mai", "workspace_path"], "core"),
    ("bot", 820, 70, 210, "BotIdentity (bể bot)", ["username", "token (bí mật)", "không mang vai"], "n"),
    ("thread", 300, 320, 220, "Thread", ["trạng thái: dang_lam|cho_nguoi|dat|huy", "số_ask (≤ 3), số_vòng_review (≤ 3)", "số_lượt_CLI (≤ trần)"], "core"),
    ("role", 600, 320, 220, "RoleAssignment (vai)", ["tên_vai (tiền tố tin)", "chỉ_dẫn (nguyên văn)", "provider, là_reviewer", "trạng thái"], "core"),
    ("sess", 860, 320, 170, "AgentSession", ["khoá (nhóm, bot)", "provider, session_id", "dấu vai+skill+provider"], "n"),
    ("turn", 300, 520, 220, "Turn (lượt)", ["bot_id, loại: thuong|ask|review|sua", "trạng thái: cho|dang_chay|xong|loi", "tín hiệu, file đổi, mức dùng"], "n"),
    ("team", 40, 520, 210, "SavedTeam (sau)", ["danh sách (vai, chỉ_dẫn,", "provider)"], "n"),
    ("member", 40, 320, 210, "GroupMember", ["(nhóm, user)", "vai_trò: chu|thanh_vien"], "core"),
    ("skill", 640, 500, 240, "Skill", ["tên, phiên bản, mô tả", "trạng thái: cho_duyet|da_duyet|ngung", "mức cho phép: noi_bo / thoai_mai", "người duyệt, ngày duyệt"], "n")]:
    s, h = ent(x, y, w, name, attrs, k)
    e[key] = (x, y, w, h)
    b.append(s)
b.append(line([(250, 100), (420, 100)], "là chủ   1 ── *", 335, 92, head=False))
b.append(line([(535, 176), (410, 320)], "1 ── *", 455, 250, head=False, lanchor="end"))
b.append(line([(600, 176), (690, 320)], "1 ── *", 668, 248, head=False))
b.append(line([(870, 160), (770, 320)], "1 ── *", 846, 240, head=False))
b.append(line([(945, 160), (945, 320)], "bot", 955, 240, head=False, lanchor="start"))
b.append(line([(650, 168), (800, 168), (800, 295), (900, 295), (900, 320)], "nhóm", 908, 290, head=False, lanchor="start"))
b.append(line([(410, 410), (410, 520)], "1 ── *", 420, 470, head=False, lanchor="start"))
b.append(line([(145, 144), (145, 320)], "1 ── *", 155, 230, head=False, lanchor="start"))
b.append(line([(200, 320), (200, 290), (470, 290), (470, 176)], "* ── 1", 300, 284, head=False))
b.append(line([(145, 402), (145, 520)], "sở hữu (từ User)", 155, 470, head=False, lanchor="start"))
b.append(line([(730, 426), (730, 500)], "* ── *  vai dùng skill", 740, 466, head=False, lanchor="start"))
D["h3_domain"] = svg(1060, 660, "\n".join(b), "Hình 3. Logical view – mô hình dữ liệu",
                     "Vai gắn với cặp (nhóm, bot), không gắn vào bot → một bot dùng lại cho nhiều nhóm với vai khác nhau")

# ---------- H4 Process / runtime ----------
b = []
b.append(box(20, 190, 140, 200, "Telegram", ["Bot API"], "ext"))
b.append(container(190, 64, 890, 456, "Tiến trình labour – asyncio, một event loop"))
for i, n in enumerate(["Poller Bot1", "Poller Bot2", "Poller BotN"]):
    b.append(box(210, 104 + 60 * i, 150, 44, n))
    b.append(line([(160, 220 + 0 * i), (210, 126 + 60 * i)]))
b.append(box(395, 140, 165, 80, "Khử trùng lặp", ["+ kiểm soát truy cập"]))
for i in range(3):
    b.append(line([(360, 126 + 60 * i), (395, 180)]))
b.append(box(590, 140, 160, 80, "Định tuyến", ["+ điều phối Thread"], "core"))
b.append(line([(560, 180), (590, 180)]))
for i, n in enumerate(["Hàng đợi nhóm A", "Hàng đợi nhóm B", "Hàng đợi nhóm C"]):
    b.append(box(780, 104 + 60 * i, 140, 44, n))
    b.append(line([(750, 180), (780, 126 + 60 * i)]))
    b.append(line([(920, 126 + 60 * i), (945, 180)]))
b.append(box(945, 140, 120, 80, "Worker pool", ["semaphore = 3"], "core"))
b.append(box(865, 560, 215, 64, "Tiến trình con", ["claude -p --restricted, không shell", "+ MCP docx của lõi"], "ext"))
b.append(line([(1005, 220), (1005, 560)], "chạy, chờ,\ntimeout", 1015, 470, both=True, lanchor="start"))
b.append(box(780, 320, 140, 70, "Bộ lọc chính sách", ["theo mức nhóm"], "core"))
b.append(line([(1005, 355), (920, 355)], "kết quả +\ntín hiệu", 962, 330))
b.append(box(590, 320, 160, 70, "Bộ gửi tin", ["đăng bằng đúng bot"]))
b.append(line([(780, 355), (750, 355)]))
b.append(line([(590, 355), (160, 355)], "tin ra (HTTPS)", 300, 348))
b.append(box(395, 430, 525, 56, "Repository (SQLite) + audit.jsonl", ["nhật ký nhóm, Thread, lượt, phiên"]))
b.append(line([(478, 220), (478, 430)], dashed=True))
b.append(line([(850, 390), (850, 430)], dashed=True))
b.append(line([(850, 320), (850, 268)], dashed=True, label="ask / review →\nlượt mới vào hàng đợi", lx=840, ly=290, lanchor="end"))
D["h4_process"] = svg(1100, 640, "\n".join(b), "Hình 4. Process view – luồng chạy trong tiến trình",
                      "Mỗi nhóm chạy một lượt tại một lúc (các bot dùng chung workspace); giữa các nhóm tối đa 3 lượt đồng thời")

# ---------- H5 Sequence: assign roles ----------
D["h5_seq_roles"] = sequence(
    [("u", "Chủ nhóm", None), ("tg", "Telegram", "bot trong bể"), ("core", "Lõi điều phối", None),
     ("ai", "Diễn giải vai", "lượt AI nhỏ, không file"), ("db", "Lưu trữ", None)],
    [("m", "u", "tg", "“@Bot1 lo giải pháp… @Bot2 phản biện + review…”", False),
     ("m", "tg", "core", "MessageEvent (poller, khử trùng lặp)", False),
     ("self", "core", "nhóm đã đăng ký? người gửi là chủ?"),
     ("m", "core", "ai", "chỉ câu nói + danh sách bot (không đọc workspace)", False),
     ("m", "ai", "core", "[Bot1: Giải pháp], [Bot2: Phản biện, reviewer]", True),
     ("m", "core", "db", "lưu RoleAssignment (chờ xác nhận)", False),
     ("m", "core", "tg", "mỗi bot nhắc lại vai, có tiền tố [Vai]", False),
     ("m", "u", "tg", "“ok” – reply đúng tin xác nhận", False),
     ("m", "tg", "core", "xác nhận của chủ nhóm", False),
     ("m", "core", "db", "vai → hiệu lực; huỷ phiên CLI cũ (nhóm, bot)", False),
     ("m", "core", "tg", "sửa nội dung tin ghim vai (một tin, không ghim thêm)", False),
     ("note", "u", "db", "Trước “ok”: bot giữ vai cũ, từ chối việc mới. Người không phải chủ giao vai → từ chối, ghi audit")],
    1060, "Hình 5. Process view – giao vai bằng lời (R3, R4)")

# ---------- H6 Sequence: ask & escalate ----------
D["h6_seq_ask"] = sequence(
    [("u", "Chủ nhóm", None), ("tg", "Telegram", None), ("core", "Lõi điều phối", None),
     ("b3", "Bot3 – Soạn Word", "agent CLI"), ("b1", "Bot1 – Giải pháp", "agent CLI")],
    [("m", "u", "tg", "“@Bot3 soạn phản hồi theo mẫu”", False),
     ("m", "tg", "core", "mở Thread T: số_ask = 0, số_vòng_review = 0", False),
     ("m", "core", "b3", "chạy lượt: vai + ngữ cảnh + file quyết định", False),
     ("m", "b3", "core", "tín hiệu ask → Bot1 (structured output, tách khỏi bài)", True),
     ("self", "core", "số_ask + số bot được hỏi ≤ 3? → số_ask = 1"),
     ("m", "core", "tg", "Bot3 đăng câu hỏi (Nội bộ: theo mẫu cố định)", False),
     ("m", "core", "b1", "chạy lượt với câu hỏi", False),
     ("m", "b1", "core", "trả lời theo file quyết định", True),
     ("m", "core", "b3", "chạy tiếp với câu trả lời", False),
     ("note", "u", "b1", "Đã đủ 3 ask → ask kế tiếp KHÔNG chạy; hoặc escalate; hoặc hết trần lượt CLI của Thread"),
     ("m", "core", "tg", "tag @chủ nhóm: “các bot chưa thống nhất…”; T → chờ người", False),
     ("m", "u", "tg", "trả lời trong Thread", False),
     ("m", "tg", "core", "số_ask về 0, chạy tiếp", False)],
    1060, "Hình 6. Process view – bot hỏi bot và leo thang (R8)")

# ---------- H7 Sequence: review ----------
D["h7_seq_review"] = sequence(
    [("u", "Chủ nhóm", None), ("tg", "Nhóm Telegram", "mọi người thấy"), ("core", "Lõi điều phối", None),
     ("b3", "Bot3 – Soạn Word", None), ("b2", "Bot2 – Reviewer", None), ("ws", "Workspace", "output/, review/")],
    [("m", "b3", "ws", "ghi phan_hoi_v1.docx", False),
     ("m", "b3", "core", "tín hiệu request_review", True),
     ("self", "core", "reviewer do chủ nhóm giao, khác bot tác giả? vòng 1 ≤ 3?"),
     ("m", "core", "tg", "[Soạn Word] Xong v1 → nhờ @Bot2 review (vòng 1/3)", False),
     ("m", "core", "b2", "lượt review (v1)", False),
     ("m", "b2", "ws", "đọc v1, ghi review/v1.md", False),
     ("m", "b2", "core", "verdict: chưa đạt + 3 góp ý", True),
     ("m", "core", "tg", "[Phản biện] Vòng 1/3: CHƯA ĐẠT – tóm tắt 3 góp ý", False),
     ("m", "core", "b3", "lượt sửa theo góp ý", False),
     ("m", "b3", "ws", "ghi v2", False),
     ("m", "core", "tg", "[Soạn Word] Đã sửa v2 → review lại (vòng 2/3)", False),
     ("m", "core", "b2", "lượt review (v2)", False),
     ("m", "b2", "core", "verdict: đạt", True),
     ("self", "core", "Thread → đạt, ghi audit"),
     ("m", "core", "tg", "ĐẠT – output/phan_hoi_v2.docx · duyệt: Bot2 · 2 vòng (tin mới, ghim)", False),
     ("m", "u", "tg", "“không đạt: …” (reply tin ĐẠT)", False),
     ("m", "tg", "core", "Thread Đạt → Đang làm; số_vòng_review = 0; gỡ ghim", False),
     ("note", "u", "ws", "Không có reviewer hợp lệ, hoặc đủ 3 vòng → tag chủ nhóm duyệt. Nội bộ: mọi tin theo mẫu cố định")],
    1160, "Hình 7. Process view – review và kết thúc “đạt”, hiển thị trên nhóm (R15)")

# ---------- H7b Sequence: skill ----------
D["h8_seq_skill"] = sequence(
    [("qtv", "Quản trị viên", None), ("u", "Chủ nhóm", None), ("tg", "Telegram", None),
     ("core", "Lõi – Thư viện skill", None), ("store", "Kho skill", "skills/"), ("ws", "Lượt của bot", "ngữ cảnh + công cụ")],
    [("m", "qtv", "store", "chép thư mục skill mới (SKILL.md + script, mẫu)", False),
     ("m", "qtv", "tg", "/skill nap", False),
     ("m", "tg", "core", "lệnh của quản trị viên", False),
     ("m", "core", "store", "kiểm tra: cấu trúc, mức cho phép, lệnh cấm", False),
     ("self", "core", "skill → chờ duyệt; báo kết quả kiểm tra"),
     ("m", "qtv", "tg", "/skill duyet bao-cao-doi-tac", False),
     ("m", "core", "store", "trạng thái → đã duyệt (ghi audit)", False),
     ("m", "u", "tg", "“có những skill nào?”", False),
     ("m", "core", "tg", "danh sách skill đã duyệt, hợp mức bảo mật nhóm", False),
     ("m", "u", "tg", "“@Bot3 dùng thêm skill bao-cao-doi-tac”", False),
     ("m", "core", "ws", "nạp SKILL.md vào ngữ cảnh lượt; script → công cụ của lõi", False),
     ("m", "core", "tg", "[Soạn Word] Đã nhận skill bao-cao-doi-tac; cập nhật tin ghim", False),
     ("note", "qtv", "ws", "Skill chưa duyệt không chạy ở nhóm nào; nhóm Nội bộ chỉ dùng skill cho phép Nội bộ")],
    1160, "Hình 8. Process view – thêm, duyệt và gắn skill (R13)")

# ---------- H9 Sequence: decision ----------
D["h9_seq_decide"] = sequence(
    [("u", "Chủ nhóm", None), ("tg", "Telegram", None), ("core", "Lõi – Quyết định", None),
     ("b1", "Bot1 – Giải pháp", "agent CLI"), ("data", "data/<nhóm>/", "bản gốc + băm"), ("ws", "Workspace", "decisions/ (bản sao)")],
    [("m", "u", "tg", "“@Bot1 chốt phương án như đã bàn”", False),
     ("m", "tg", "core", "người gửi là chủ nhóm? (thành viên → chỉ ghi nhật ký)", False),
     ("m", "core", "b1", "lượt: soạn bản quyết định → output/de-xuat-quyet-dinh.md", False),
     ("m", "b1", "core", "tín hiệu files", True),
     ("m", "core", "tg", "[Giải pháp] Đã soạn bản quyết định: output/de-xuat-quyet-dinh.md – reply “ok” để chốt", False),
     ("m", "u", "tg", "“ok” – reply đúng tin trên", False),
     ("m", "core", "data", "lưu bản gốc (phiên bản n) + băm vào data/ và CSDL", False),
     ("m", "core", "ws", "chép sang decisions/quyet-dinh-giai-phap.md (agent chỉ đọc)", False),
     ("m", "core", "tg", "[Hệ thống] Đã chốt quyết định giải pháp – phiên bản n", False),
     ("note", "u", "ws", "Trước mỗi lượt: băm decisions/ ≠ bản gốc → không chạy, khôi phục từ data/, tag chủ nhóm")],
    1160, "Hình 9. Process view – chốt quyết định giải pháp (R7)")

# ---------- H8 Thread state machine ----------
b = []
b.append('<circle cx="50" cy="210" r="9" fill="#1f2937"/>')
b.append(box(150, 180, 190, 60, "Đang làm", ["dang_lam"], "core"))
b.append(box(560, 70, 190, 60, "Chờ người", ["cho_nguoi"]))
b.append(box(560, 300, 190, 60, "Đạt", ["dat – kết thúc"]))
b.append(box(860, 180, 150, 60, "Huỷ", ["huy – kết thúc"]))
b.append(line([(59, 210), (150, 210)], "chủ nhóm\ngiao việc", 104, 188))
b.append(line([(170, 240), (170, 278), (230, 278), (230, 240)], "ask: số_ask + 1\nreview: số_vòng + 1\n(hai đếm riêng)", 160, 300, lanchor="end"))
b.append(line([(340, 192), (560, 92)], "ask thứ 4 / review vòng 4 /\nescalate / hết trần lượt CLI /\nkhông có reviewer", 300, 80, lanchor="start"))
b.append(line([(560, 116), (340, 214)], "chủ nhóm trả lời → đếm của loại\nđã chạm trần về 0", 400, 226, lanchor="start"))
b.append(line([(340, 230), (560, 322)], "reviewer: đạt\nhoặc chủ nhóm: đạt", 420, 300))
b.append(line([(560, 345), (290, 345), (290, 240)], "chủ nhóm: không đạt / mở lại", 430, 372))
b.append(line([(655, 130), (655, 300)], "chủ nhóm: đạt", 665, 220, lanchor="start"))
b.append(line([(750, 100), (935, 100), (935, 180)], "chủ nhóm: dừng / huỷ", 840, 92))
b.append(line([(325, 240), (325, 420), (935, 420), (935, 240)], "chủ nhóm: dừng / huỷ", 600, 412))
D["h8_state"] = svg(1040, 450, "\n".join(b), "Hình 10. Process view – vòng đời của một Thread",
                    "Hai đếm độc lập, mỗi đếm tối đa 3; thêm trần tổng lượt CLI của Thread. “Chờ người”: không lượt bot nào chạy")

# ---------- H9 Development view ----------
b = []
b.append(box(360, 70, 300, 64, "labour.app", ["khởi động, ghép nối, đọc cấu hình"]))
b.append(box(110, 200, 330, 96, "labour.core", ["nghiệp vụ: nhóm, vai, Thread, chính sách,", "quyết định, lập lịch, skill", "không import thư viện ngoài"], "core"))
b.append(box(590, 200, 330, 96, "labour.ports", ["interface: ChannelAdapter, AgentRuntime,", "Repository, AuditSink,", "WorkspaceStore, SkillStore"], "core"))
ad = [("labour.channels.telegram", ["aiogram 3"]), ("labour.runtimes", ["claude_code, cursor, gemini"]),
      ("labour.storage", ["SQLAlchemy + Alembic, jsonl"]), ("labour.workspace, .tools", ["thư mục, luật quyền, MCP docx"])]
for i, (n, l) in enumerate(ad):
    b.append(box(30 + i * 250, 380, 230, 64, n, l))
    b.append(line([(145 + i * 250, 380), (145 + i * 250, 350), (755, 350), (755, 296)], dashed=True, head=False))
b.append(line([(755, 330), (755, 297)], head=False))
b.append('<path d="M755 297 L748 310 L762 310 Z" fill="#ffffff" stroke="#6b7280"/>')
b.append(t(770, 340, "triển khai interface", 11.5, 400, "start", QUIET))
b.append(line([(440, 248), (590, 248)], "dùng", 515, 240))
b.append(line([(450, 134), (275, 200)]))
b.append(line([(570, 134), (755, 200)]))
b.append(line([(660, 102), (1010, 102), (1010, 380)], "tạo & tiêm adapter", 1000, 160, lanchor="end"))
b.append(box(30, 490, 480, 56, "tests/unit", ["lõi chạy với FakeChannel + FakeRuntime, không gọi mạng"], "ext"))
b.append(box(530, 490, 480, 56, "tests/integration", ["Claude Code thật trong workspace tạm; Telegram nhóm thử"], "ext"))
D["h9_dev"] = svg(1040, 570, "\n".join(b), "Hình 11. Development view – gói mã nguồn và chiều phụ thuộc",
                  "Quy tắc: core chỉ phụ thuộc ports; thêm kênh / nhà cung cấp AI = thêm một gói adapter")

# ---------- H10 Physical MVP ----------
b = []
b.append(box(20, 150, 170, 90, "Điện thoại / laptop", ["ứng dụng Telegram"], "ext"))
b.append(container(220, 64, 540, 400, "VM công ty – Windows 10 (16 core, 14,6 GB)", dashed=False))
b.append(box(250, 110, 220, 70, "Tiến trình labour", ["Python 3.12 + uv"], "core"))
b.append(box(510, 110, 220, 70, "data\\", ["labour.db, audit.jsonl, skills\\", "luật quyền, chỉ dẫn nhóm, QĐ gốc"]))
b.append(box(250, 230, 220, 70, "Claude Code CLI", ["ghim 2.1.328, tắt tự cập nhật"]))
b.append(box(510, 230, 220, 70, "workspaces\\<nhóm>\\", ["C:\\Works\\Labour\\workspaces"]))
b.append(box(250, 370, 220, 64, "Task Scheduler", ["tuỳ chọn: tự khởi động lại"], "fut"))
b.append(box(510, 370, 220, 64, "Word / Explorer", ["người dùng mở file kết quả"]))
b.append(box(800, 100, 190, 70, "Máy chủ Telegram", ["Bot API"], "ext"))
b.append(box(800, 250, 190, 70, "Anthropic", ["Claude subscription"], "ext"))
b.append(box(800, 380, 190, 64, "Cursor / Google", ["tuỳ chọn"], "fut"))
b.append(line([(470, 145), (510, 145)]))
b.append(line([(360, 180), (360, 230)], "gọi lượt", 370, 210, lanchor="start"))
b.append(line([(470, 265), (510, 265)]))
b.append(line([(620, 370), (620, 300)]))
b.append(line([(360, 110), (360, 97), (780, 97), (780, 135), (800, 135)], "long polling – HTTPS đi ra", 650, 91))
b.append(line([(360, 300), (360, 330), (780, 330), (780, 285), (800, 285)], "HTTPS đi ra", 570, 324))
b.append(line([(105, 150), (105, 40), (895, 40), (895, 100)], "Telegram app", 500, 34))
D["h10_phys_mvp"] = svg(1010, 510, "\n".join(b), None)
D["h10_phys_mvp"] = D["h10_phys_mvp"].replace("</svg>", t(20, 498, "Hình 12. Physical view – bản cá nhân (MVP): chạy thẳng trên Windows, không mở cổng vào", 13, 700, "start") + "</svg>")

# ---------- H11 Physical commercial ----------
b = []
b.append(container(200, 64, 580, 420, "Máy chủ của công ty khách (Linux)", dashed=False))
b.append(container(220, 100, 540, 260, "Docker Compose"))
b.append(box(240, 140, 200, 70, "labour", ["container dịch vụ"], "core"))
b.append(box(480, 140, 260, 70, "Volume data/", ["SQLite → Postgres khi lớn", "skills/ (kho skill)"]))
b.append(box(240, 260, 200, 70, "Volume workspaces/", ["mỗi nhóm một thư mục"]))
b.append(box(480, 260, 260, 70, "Syncthing / SMB", ["tuỳ khách bật; ngoài", "phạm vi mức Nội bộ"], "fut"))
b.append(box(220, 390, 260, 70, ".env + config.yaml", ["token bot, API key, danh sách User"], "ext"))
b.append(box(500, 390, 260, 70, "Quản trị viên", ["chỉnh cấu hình, bể bot, giới hạn"], "ext"))
b.append(box(810, 90, 190, 70, "Telegram / Teams / Slack", ["kênh chat"], "ext"))
b.append(box(810, 200, 190, 90, "AI provider API", ["Anthropic API / Agent SDK", "tài khoản của khách"], "ext"))
b.append(box(810, 350, 190, 90, "Máy kỹ sư", ["ứng dụng chat", "thư mục đồng bộ, Word"], "ext"))
b.append(box(20, 140, 160, 90, "Kỹ sư, chủ nhóm", ["dùng qua kênh chat"], "ext"))
b.append(line([(440, 175), (480, 175)]))
b.append(line([(340, 210), (340, 260)]))
b.append(line([(440, 295), (480, 295)]))
b.append(line([(340, 140), (340, 130), (790, 130), (790, 125), (810, 125)], "HTTPS đi ra", 640, 124))
b.append(line([(440, 200), (460, 200), (460, 234), (795, 234), (795, 245), (810, 245)], "HTTPS đi ra", 620, 228))
b.append(line([(740, 295), (790, 295), (790, 395), (810, 395)], both=True))
b.append(line([(100, 140), (100, 44), (905, 44), (905, 90)], "chat", 500, 38))
D["h11_phys_prod"] = svg(1020, 530, "\n".join(b), None)
D["h11_phys_prod"] = D["h11_phys_prod"].replace("</svg>", t(20, 518, "Hình 13. Physical view – bản sản phẩm: công ty tự cài trên máy chủ của mình", 13, 700, "start") + "</svg>")

# ---------- H12 Use cases ----------
b = []
b.append(container(230, 60, 540, 700, "Hệ thống Labour", dashed=False))
ucs = ["UC-01 Đăng ký nhóm, chọn mức bảo mật", "UC-02 Giao / sửa vai bằng lời", "UC-03 Thảo luận giải pháp với bot",
       "UC-04 Chốt quyết định giải pháp", "UC-05 Giao việc soạn tài liệu theo mẫu", "UC-06 Bot hỏi bot, leo thang",
       "UC-07 Review, “đạt” – hiện trên nhóm", "UC-08 Đổi provider AI bằng lời", "UC-09 Đưa file vào, nhận kết quả",
       "UC-10 Quản lý User, bể bot, giới hạn", "UC-11 Lưu đội để dùng lại (sau)",
       "UC-12 Xem, thêm, gắn skill", "UC-13 Xem vai của một bot"]
ys = [110 + 49 * i for i in range(len(ucs))]
for u, y in zip(ucs, ys):
    b.append(ellipse(500, y, 220, 20, u))
b.append(actor(90, 190, "Chủ nhóm"))
b.append(actor(90, 470, "Kỹ sư thành viên"))
b.append(actor(905, 520, "Quản trị viên"))
b.append(actor(905, 250, "Bot (agent)"))
for i in [0, 1, 2, 3, 4, 6, 7, 8, 10, 11, 12]:
    b.append(line([(108, 230), (280, ys[i])], head=False))
for i in [2, 8, 12]:
    b.append(line([(108, 510), (280, ys[i])], head=False))
for i in [5, 6]:
    b.append(line([(887, 290), (720, ys[i])], head=False))
b.append(line([(887, 560), (720, ys[9])], head=False))
b.append(line([(887, 560), (720, ys[11])], head=False))
D["h12_usecase"] = svg(1000, 780, "\n".join(b), "Hình 14. Scenarios (+1) – các ca sử dụng")

# ---------- render ----------
chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
for name, s in D.items():
    p = os.path.join(OUT, name + ".svg")
    open(p, "w", encoding="utf-8").write(s)
    w = int(re.search(r'width="(\d+)"', s).group(1)); h = int(re.search(r'height="(\d+)"', s).group(1))
    html = os.path.join(OUT, name + ".html")
    open(html, "w", encoding="utf-8").write(
        f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;padding:0;overflow:hidden}}</style>{s}')
    png = os.path.join(OUT, name + ".png")
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--screenshot={png}", f"--window-size={w},{h}", "--force-device-scale-factor=2",
                    "file:///" + html.replace("\\", "/")], capture_output=True, timeout=60)
    print(name, w, h, os.path.exists(png))
