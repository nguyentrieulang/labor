import os, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
OUT = sys.argv[1]

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for m in ("left_margin", "right_margin"):
    setattr(sec, m, Cm(2))
sec.top_margin = sec.bottom_margin = Cm(2)

st = doc.styles["Normal"]
st.font.name = "Calibri"; st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.paragraph_format.space_after = Pt(6)
for lvl, size, color in [(1, 16, "1F3864"), (2, 13, "2E5597"), (3, 11.5, "2E5597")]:
    h = doc.styles[f"Heading {lvl}"]
    h.font.name = "Calibri"; h.font.size = Pt(size); h.font.bold = True
    h.font.color.rgb = RGBColor.from_string(color)
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    h.paragraph_format.space_before = Pt(14 if lvl == 1 else 10)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True


def H(text, lvl=1):
    doc.add_heading(text, lvl)


def P(text, bold_prefix=None, italic=False, size=None, align=None):
    p = doc.add_paragraph()
    if bold_prefix:
        r = p.add_run(bold_prefix); r.bold = True
    r = p.add_run(text); r.italic = italic
    if size: r.font.size = Pt(size)
    if align: p.alignment = align
    return p


def B(items, style="List Bullet"):
    for it in items:
        p = doc.add_paragraph(style=style)
        if isinstance(it, tuple):
            r = p.add_run(it[0]); r.bold = True
            p.add_run(it[1])
        else:
            p.add_run(it)
        p.paragraph_format.space_after = Pt(2)


def shade(cell, hex_):
    tcPr = cell._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd"); s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), hex_)
    tcPr.append(s)


def T(header, rows, widths, size=9.5):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(size)
        shade(c, "D9E2F3")
    # repeat header row
    trPr = t.rows[0]._tr.get_or_add_trPr(); th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            par = cells[i].paragraphs[0]
            bold = False
            if isinstance(v, tuple):
                v, bold = v
            r = par.add_run(str(v)); r.font.size = Pt(size); r.bold = bold
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
            for par in row.cells[i].paragraphs:
                par.paragraph_format.space_after = Pt(1)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def FIG(name, caption, width=17):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(os.path.join(IMG, name + ".png"), width=Cm(width))
    p.paragraph_format.keep_with_next = True
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(caption); r.italic = True; r.font.size = Pt(9.5)


def page_break():
    doc.add_page_break()


def toc():
    p = doc.add_paragraph()
    r = p.add_run()
    for tag, txt in [("begin", None), (None, 'TOC \\o "1-2" \\h \\z \\u'), ("separate", None), (None, None), ("end", None)]:
        if tag:
            f = OxmlElement("w:fldChar"); f.set(qn("w:fldCharType"), tag); r._r.append(f)
        elif txt:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = txt; r._r.append(it)
        else:
            tt = OxmlElement("w:t"); tt.text = "Mở file trong Word, bấm chuột phải vào đây → Update Field để hiện mục lục."; r._r.append(tt)


# ================= COVER =================
for _ in range(5):
    doc.add_paragraph()
P("TÀI LIỆU THIẾT KẾ KIẾN TRÚC MỨC CAO (HLD)", size=22, align=WD_ALIGN_PARAGRAPH.CENTER).runs[0].bold = True
P("Hệ thống Labour – Đội AI Agent trên Telegram", size=16, align=WD_ALIGN_PARAGRAPH.CENTER)
P("Yêu cầu v2.2 · Phương án kiến trúc A · Trình bày theo mô hình 4+1 views", size=12,
  align=WD_ALIGN_PARAGRAPH.CENTER, italic=True)
doc.add_paragraph()
T(["Thuộc tính", "Giá trị"], [
    ["Phiên bản", "0.6 – bản đề nghị khoá"],
    ["Ngày", "19/11/2026"],
    ["Trạng thái", "Chờ review"],
    ["Tài liệu đầu vào", "Requirement_v2.1.docx; notes/2026-11-18-yeu-cau-v2.2.md (yêu cầu v2.2, R1–R15); góp ý review HLD v0.2; nhận xét chuyên gia về HLD v0.3 và v0.5; spike/2026-11-19-windows-denylist và spike/2026-11-19-docx-mcp (kết quả thử); "
                         "docs/2026-11-18-agent-team-v2.2-design.md (thiết kế sơ bộ)"],
    ["Đối tượng đọc", "Người đánh giá kiến trúc, bảo mật, quản lý dự án; người viết LLD và người triển khai"],
    ["Tài liệu tiếp theo", "LLD (chi tiết interface, schema, prompt hệ thống) – viết sau khi HLD được duyệt"],
], [4.5, 12.5], size=10)
P("Lịch sử thay đổi", bold_prefix="")
T(["Phiên bản", "Ngày", "Nội dung"], [
    ["0.1", "18/11/2026", "Bản mô tả kiến trúc sơ bộ (chưa có danh sách chức năng, truy vết, hình vẽ)."],
    ["0.2", "18/11/2026", "Viết lại theo 4+1 views; thêm ngữ cảnh hệ thống, danh sách chức năng F-01..F-22, "
                          "ma trận truy vết sang R1–R12 và FR/NFR/SEC của v2.1, 12 hình, quyết định kiến trúc."],
    ["0.3", "18/11/2026", "Theo góp ý review: thêm quản lý skill (R13, F-23..F-25, Hình 8), xem vai của một bot "
                          "(R14, F-26), hiển thị luồng review và “đạt” trên nhóm (R15, F-27, Hình 7 vẽ lại); "
                          "cập nhật Hình 1, 2, 3, 10–13, bảo mật, AD-10..AD-12, rủi ro, nghiệm thu."],
    ["0.4", "19/11/2026", "Theo nhận xét chuyên gia: tách hai bộ đếm + trần lượt CLI (mục 6.6); nhóm Nội bộ chỉ đăng mẫu cố định; "
                          "chỉ lõi ghi decisions/, “chốt” có xác nhận, R7 vào MVP; quy tắc reviewer và mở lại Thread đạt; "
                          "phiên CLI theo (nhóm, bot); GroupMember; tín hiệu qua structured output; lượt dở → lỗi; Gemini chạy trong thư mục trống; "
                          "F-28; AD-13..AD-17; 6 kiểm tra bảo mật; sửa các điểm nhỏ."],
    ["0.5", "19/11/2026", "Theo kết quả hai lần thử trên VM: agent chạy không có shell; luật quyền do lõi giữ, truyền qua "
                          "--settings --restricted (không đặt trong workspace); thêm công cụ Word của lõi (MCP, F-29); skill nạp qua "
                          "ngữ cảnh lượt, script của skill chạy qua công cụ lõi; ghim phiên bản Claude Code; mục 7.4 kết quả thử; AD-18..AD-20."],
    ["0.6", "19/11/2026", "Theo nhận xét chuyên gia về v0.5: tin Nội bộ chỉ ghép từ trường có kiểu (bỏ câu tóm tắt cắt từ lời agent); "
                          "agent chỉ ghi output/ và review/, chỉ dẫn nhóm + luật quyền + bản gốc quyết định ở data/; một lượt mỗi nhóm "
                          "tại một lúc; chỉ chủ nhóm tạo lượt agent; Grok/Gemini với nhóm Nội bộ; Hình 9 mới (chốt quyết định); "
                          "sửa chữ lệch (chạy mã, skill, AD-05, quá giờ, tác giả review, claude.exe); AD-21..AD-23."],
], [2.2, 2.6, 12.2], size=10)
page_break()
H("Mục lục", 1)
toc()
page_break()

# ================= 1 =================
H("1. Giới thiệu", 1)
H("1.1 Mục đích tài liệu", 2)
P("Tài liệu mô tả kiến trúc mức cao của hệ thống Labour theo phương án A: một dịch vụ Python duy nhất, chia khối rõ "
  "ràng bên trong (modular monolith). Mục tiêu là để các bên đánh giá được ba điều: hệ thống làm những chức năng gì, "
  "mỗi chức năng đáp ứng yêu cầu nào, và kiến trúc tổ chức các chức năng đó ra sao ở năm góc nhìn của mô hình 4+1.")
H("1.2 Phạm vi hệ thống", 2)
P("Hệ thống cho một kỹ sư làm trưởng nhóm của một đội AI agent trong nhóm chat Telegram. Kỹ sư giao vai bằng lời, "
  "cùng các bot nghĩ giải pháp, rồi giao việc soạn tài liệu và chỉ review kết quả.")
T(["", "Bản đầu (MVP)", "Sau"], [
    ["Luồng nghiệp vụ", "Nhận xét đối tác → file Word theo mẫu", "Slide, code, thuyết minh đề tài (không cần code mới)"],
    ["Người dùng", "1 người (chủ dự án), mã kiểm quyền đầy đủ", "Nhiều kỹ sư trong một công ty"],
    ["Kênh", "Telegram", "Teams, Slack, web"],
    ["AI", "Claude Code CLI (subscription); Grok, Gemini nếu chạy headless được", "Claude Agent SDK / API key của khách; model local"],
    ["Nơi chạy", "VM công ty, Windows 10, chạy thẳng", "Máy chủ của công ty khách, Docker Compose"],
    ["Lưu trữ", "SQLite + audit.jsonl", "Postgres"],
], [3.2, 6.9, 6.9])
H("1.3 Thuật ngữ", 2)
T(["Thuật ngữ", "Nghĩa"], [
    ["Nhóm", "Một nhóm chat Telegram đã đăng ký với hệ thống; gắn với một workspace và một mức bảo mật."],
    ["Chủ nhóm", "Người tạo nhóm (phải là User được phép tạo nhóm). Chỉ chủ nhóm tạo lượt agent (giao việc, sửa, hỏi), giao/sửa vai, chốt quyết định giải pháp, nói “đạt” / “không đạt”, giao quyền review, đổi mức bảo mật."],
    ["Bể bot", "Tập bot Telegram tạo sẵn qua BotFather, tên trung tính, dùng lại cho nhiều nhóm."],
    ["Vai", "Nhiệm vụ của một bot trong một nhóm (ví dụ Giải pháp, Phản biện, Soạn Word), giao bằng lời tự nhiên."],
    ["Thread", "Một chuỗi việc bắt đầu từ lời giao của chủ nhóm. Có hai bộ đếm độc lập (số ask, số vòng review, mỗi loại tối đa 3) và một trần tổng số lượt CLI."],
    ["Lượt (Turn)", "Một lần chạy agent CLI cho một bot, trong workspace của nhóm."],
    ["Tín hiệu", "Khối dữ liệu có cấu trúc agent trả về cuối mỗi lượt: reply, ask, escalate, request_review, verdict, files."],
    ["Leo thang", "Dừng chuỗi bot và tag chủ nhóm để người quyết định."],
    ["Công cụ của lõi", "Công cụ do lõi cung cấp cho agent qua MCP (ví dụ docx_read, docx_build). Agent không có shell; mọi việc cần chạy mã đi qua các công cụ này, mỗi công cụ tự kiểm đường dẫn."],
    ["Mẫu tin Nội bộ", "Dạng tin duy nhất lõi được đăng ở nhóm Nội bộ, ghép chỉ từ trường có kiểu: [Vai], loại việc vừa làm (từ danh mục cố định, ví dụ “đã soạn”, “review: chưa đạt”), con số (vòng, số góp ý), đường dẫn file. Không chữ nào lấy từ văn bản của agent; reply, câu ask, góp ý ghi nguyên văn vào file trên đĩa."],
    ["Workspace", "Thư mục của nhóm trên đĩa. Agent chỉ ghi output/ và review/; input/, templates/, decisions/ (bản sao) chỉ đọc; lõi ghi thao-luan/. Chỉ dẫn nhóm (CLAUDE.md), luật quyền và bản gốc quyết định nằm ở data/<nhóm>/, ngoài workspace."],
    ["Nội bộ / Thoải mái", "Hai mức bảo mật của nhóm. Nội bộ: Telegram chỉ thấy mẫu tin cố định (vai, việc, con số, đường dẫn). Thoải mái: nội dung và file đi qua Telegram."],
    ["Provider", "Nhà cung cấp AI chạy cho một vai: claude (mặc định), grok, gemini; sau này claude_api."],
    ["Skill", "Gói năng lực dùng lại cho agent: một thư mục có SKILL.md (mô tả, hướng dẫn), có thể kèm script và mẫu. Ví dụ: soạn/sửa Word theo mẫu, review tài liệu."],
    ["Thư viện skill", "Danh mục skill của một bản cài. Skill phải được quản trị viên duyệt mới dùng được; chủ nhóm chọn skill cho từng vai."],
], [3.5, 13.5])
H("1.4 Cách đọc tài liệu – mô hình 4+1", 2)
P("Mỗi view trả lời một câu hỏi cho một nhóm người đọc. View thứ năm (Scenarios) dùng các ca sử dụng để kiểm chứng rằng "
  "bốn view kia khớp nhau. Ngoài 4+1, tài liệu thêm hai phần mà 4+1 không có sẵn: sơ đồ ngữ cảnh (mục 2) và ma trận "
  "chức năng ↔ yêu cầu (mục 4).")
T(["View", "Câu hỏi trả lời", "Người đọc chính", "Mục, hình"], [
    ["Logical", "Hệ thống gồm những khối chức năng nào, dữ liệu gì?", "Kiến trúc sư, người viết LLD", "Mục 5 · Hình 2, 3"],
    ["Process", "Lúc chạy: tiến trình, đồng thời, luồng tin giữa các khối?", "Kiến trúc sư, người triển khai", "Mục 6 · Hình 4–10"],
    ["Development", "Mã nguồn chia gói thế nào, phụ thuộc theo chiều nào?", "Lập trình viên", "Mục 7 · Hình 11"],
    ["Physical", "Chạy trên máy nào, kết nối mạng ra sao?", "Vận hành, bảo mật", "Mục 8 · Hình 12, 13"],
    ["Scenarios (+1)", "Các ca sử dụng chạy qua bốn view thế nào?", "Tất cả", "Mục 9 · Hình 14"],
], [2.6, 6.6, 4.2, 3.6])

# ================= 2 =================
H("2. Ngữ cảnh hệ thống", 1)
P("Hệ thống đứng giữa nhóm Telegram và các agent CLI. Người dùng chỉ làm việc qua Telegram và mở file kết quả bằng "
  "Word. Tài liệu công việc chỉ nằm trong workspace trên đĩa; Telegram chỉ nhận đúng phần mà mức bảo mật của nhóm cho phép.")
FIG("h1_context", "Hình 1. Ngữ cảnh hệ thống")
T(["Bên ngoài", "Vai trò", "Giao tiếp với hệ thống", "Dữ liệu đi qua"], [
    ["Chủ nhóm", "Giao vai, giao việc, thảo luận, duyệt, nói “đạt”", "Telegram", "Lời giao việc, câu trả lời"],
    ["Kỹ sư thành viên", "Góp ý vào nhật ký Thread (bot đọc ở lượt sau), tra cứu /vai /skills /status; không tạo lượt agent", "Telegram", "Tin nhắn"],
    ["Quản trị viên", "Khai báo User, bể bot, giới hạn; thêm và duyệt skill", "File config.yaml, .env; thư mục skills/; lệnh /skill", "Cấu hình, bí mật, skill"],
    ["Telegram Bot API", "Kênh chat; một tài khoản bot cho mỗi bot trong bể", "Long polling, HTTPS đi ra", "Nhóm Nội bộ: mẫu tin cố định; Thoải mái: đầy đủ + file ≤ 20 MB"],
    ["Claude Code CLI", "Runtime agent mặc định, đọc/ghi file văn bản; Word qua công cụ của lõi", "Tiến trình con `claude -p --restricted`, không shell", "Prompt + nội dung workspace → Anthropic"],
    ["Cursor CLI (Grok)", "Runtime tuỳ chọn", "Tiến trình con `cursor-agent`", "Như trên → Cursor/xAI"],
    ["Gemini CLI", "Runtime tuỳ chọn, chỉ nhóm Thoải mái", "Tiến trình con", "Không bao giờ nhận tài liệu công ty"],
    ["Workspace (đĩa)", "Nơi chứa tài liệu vào/ra, quyết định giải pháp", "Hệ thống file", "Toàn bộ nội dung công việc"],
], [3.0, 4.6, 4.0, 5.4])

# ================= 3 =================
H("3. Yêu cầu định hướng kiến trúc", 1)
H("3.1 Yêu cầu nguồn", 2)
P("HLD đáp ứng 15 yêu cầu chức năng mới của v2.2 (R1–R15) và kế thừa các yêu cầu của v2.1 còn áp dụng. Mức "
  "“Chốt / Đề xuất” lấy từ bản tổng hợp yêu cầu v2.2.")
T(["Mã", "Yêu cầu v2.2", "Trạng thái"], [
    ["R1", "Giao diện chính là nhóm Telegram: người dùng + nhiều bot, mỗi bot là một agent.", "Chốt"],
    ["R2", "Bể bot dùng lại cho nhiều nhóm; vai gắn theo nhóm, không gắn vào bot.", "Chốt"],
    ["R3", "Giao vai/giao việc bằng lời tự nhiên trên chat; sửa vai giữa chừng cũng bằng lời.", "Chốt"],
    ["R4", "Bot nhắc lại vai để xác nhận; vai được ghim; tin của bot có tiền tố vai.", "Chốt (MVP, F-07)"],
    ["R5", "“Lưu đội này lại” để dùng lại tổ hợp vai.", "Đề xuất"],
    ["R6", "Hai chế độ: nghĩ giải pháp = tương tác; làm tài liệu = giao việc, chỉ review.", "Chốt"],
    ["R7", "File “quyết định giải pháp” là điểm bàn giao giữa hai chế độ; chỉ lõi ghi, “chốt” có xác nhận.", "Chốt (MVP, F-15)"],
    ["R8", "Bot vướng → hỏi bot khác trước, tối đa ~3 lượt; quá giới hạn hoặc chạm quyết định đã chốt → tag người dùng.", "Chốt"],
    ["R9", "Mỗi nhóm ↔ một thư mục dự án; thả file nhỏ vào nhóm Thoải mái thì tự lưu.", "Chốt"],
    ["R10", "Mẫu đầu ra không cố định; bot có năng lực như agent CLI (đọc mẫu, tạo/sửa .docx).", "Chốt"],
    ["R11", "Mức bảo mật theo từng nhóm: Nội bộ / Thoải mái.", "Chốt"],
    ["R12", "Gemini không bao giờ nhận tài liệu công ty.", "Đề xuất"],
    ["R13", "Quản lý skill: có thư viện skill sẵn có, xem được, thêm được skill mới, gắn skill cho vai.", "Chốt (review v0.2)"],
    ["R14", "Xem được các vai mà một bot đang đảm nhiệm.", "Chốt (review v0.2)"],
    ["R15", "Luồng review và kết thúc “đạt” hiển thị trên nhóm chat.", "Chốt (review v0.2)"],
    ["Đạt", "Việc “đạt” khi chủ nhóm review đạt, hoặc bot có vai reviewer báo đạt.", "Chốt"],
    ["1a", "Bán cho công ty tự cài; nhiều kỹ sư trong một bản cài; mỗi nhóm một chủ.", "Chốt"],
], [1.4, 13.2, 2.4])
P("Yêu cầu v2.1 kế thừa: FR-02, FR-03, FR-04, FR-05, FR-06, FR-09, FR-11, FR-12, FR-19, FR-22, FR-32, FR-33, FR-34, "
  "FR-35; NFR-03, NFR-04, NFR-06, NFR-07, NFR-13, NFR-21, NFR-22; SEC-01 đến SEC-07. Mẫu tác vụ (FR-23..29) của v2.1 "
  "được thay bằng thư viện skill (F-23..F-25), không bị bỏ. KnowledgeBase (FR-13..17) và module lịch (FR-30..31) "
  "không thuộc phạm vi v2.2 bản đầu.")
H("3.2 Thuộc tính chất lượng, xếp theo ưu tiên", 2)
T(["#", "Thuộc tính", "Ý nghĩa cụ thể", "Kiến trúc đáp ứng bằng"], [
    ["1", "Bảo mật dữ liệu", "Nội dung nhóm Nội bộ không lên Telegram; tài liệu công ty không sang Gemini; agent không ra khỏi workspace, không sửa file quyết định", "Nhóm Nội bộ chỉ đăng mẫu cố định do lõi dựng; agent không có shell, luật quyền do lõi cấp; chỉ lõi ghi decisions/; skill phải được duyệt"],
    ["2", "Kiểm soát hạn mức AI", "Bot không tự cãi nhau vô hạn, không đốt hết subscription", "Hai trần 3 (ask, review) + trần tổng lượt CLI mỗi Thread; 3 lượt đồng thời; tin không nhắc ai không chạy bot"],
    ["3", "Người kiểm soát", "Mọi quyết định quan trọng do chủ nhóm", "Leo thang bắt buộc; khoá file quyết định; chỉ chủ nhóm nói “đạt” (hoặc reviewer do chủ giao); mọi bước review hiện trên nhóm"],
    ["4", "Dễ cài cho khách", "Một bản cài cho một công ty", "Một dịch vụ, Docker Compose, cấu hình bằng file"],
    ["5", "Mở rộng", "Thêm kênh / nhà cung cấp AI không viết lại lõi; skill toàn chữ thêm không sửa lõi", "Lõi chỉ biết interface ChannelAdapter, AgentRuntime. Skill có mã = thêm công cụ của lõi (bản cài mới)"],
    ["6", "Hiệu năng", "Một lượt agent mất từ vài chục giây tới vài phút – chấp nhận được", "Hàng đợi bất đồng bộ; không chặn tin khác khi một lượt đang chạy"],
], [0.7, 3.0, 6.6, 6.7])
H("3.3 Ràng buộc", 2)
B([("AI bản cá nhân: ", "Claude Code gói subscription đăng nhập bằng code (không API key); Cursor trả phí; Google Pro (Gemini CLI)."),
   ("Hạ tầng: ", "VM công ty Windows 10, 16 core / 14,6 GB RAM (đo trên máy; v2.1 ghi 14 GB); Python 3.12; Claude Code cài qua npm trên Windows (2.1.327, tự cập nhật lên 2.1.328 trong lúc thử) (lõi gọi thẳng claude.exe trong %APPDATA%\\npm\\node_modules\\@anthropic-ai\\claude-code\\bin như spike, không qua claude.ps1 / claude.cmd); chưa có code v2.1."),
   ("Telegram: ", "bot tạo thủ công; tên bot chung toàn cục; file tải về ≤ 20 MB; không mã hoá đầu-cuối với bot."),
   ("Điều khoản: ", "dùng subscription cá nhân cho sản phẩm bán là rủi ro; bản thương mại dùng tài khoản AI của khách.")])

# ================= 4 =================
H("4. Chức năng hệ thống và truy vết yêu cầu", 1)
P("Bảng dưới là danh sách chức năng của hệ thống. Mỗi chức năng ghi yêu cầu nguồn và khối logical thực hiện "
  "(xem mục 5). Cột Phase: M = bản đầu, S = sau.")
F = [
    ["F-01", "Đăng ký nhóm", "Bot được thêm vào nhóm, User có quyền tạo nhóm gõ /start → tạo Group, người đó làm chủ, tạo workspace. User chỉ có trong allowlist thì không thành chủ.", "R1, R9, 1a", "Nhóm & vai; WorkspaceManager", "M"],
    ["F-02", "Chọn / đổi mức bảo mật", "Hỏi Nội bộ / Thoải mái khi đăng ký (mặc định Nội bộ); chỉ chủ nhóm đổi.", "R11", "Nhóm & vai; Chính sách", "M"],
    ["F-03", "Quản lý bể bot", "Khai báo token các bot; mọi bot chạy trong một tiến trình; bot không mang vai.", "R2", "TelegramAdapter; Cấu hình", "M"],
    ["F-04", "Kiểm soát truy cập", "Chỉ User trong danh sách và nhóm đã đăng ký được phục vụ; người lạ bị bỏ qua và ghi audit.", "FR-02, 1a", "Kiểm soát truy cập", "M"],
    ["F-05", "Quyền chủ nhóm", "Chỉ chủ nhóm tạo lượt agent, giao/sửa vai, giao quyền review, chốt quyết định, nói “đạt” / “không đạt”, đổi bảo mật, bật Gemini/Grok.", "1a, Đạt", "Kiểm soát truy cập", "M"],
    ["F-06", "Giao vai bằng lời", "Diễn giải lời giao tự nhiên thành vai của từng bot bằng một lượt AI nhỏ chỉ nhận câu nói + danh sách bot (không đọc workspace); lưu chỉ dẫn nguyên văn.", "R3", "Nhóm & vai", "M"],
    ["F-07", "Xác nhận, ghim vai, tiền tố", "Bot nhắc lại vai; “ok” chỉ có hiệu lực khi chủ nhóm reply đúng tin xác nhận; trước đó bot giữ vai cũ và từ chối việc mới. Một tin ghim vai, cập nhật bằng sửa nội dung; tin bot có [Vai].", "R4", "Nhóm & vai; Bộ gửi tin", "M"],
    ["F-08", "Sửa vai giữa chừng", "Lời bổ sung được nối vào chỉ dẫn; cập nhật tin ghim.", "R3", "Nhóm & vai", "M"],
    ["F-09", "Đổi provider bằng lời", "“@Bot3 dùng Grok”; lõi từ chối nếu provider không có trong danh sách cho phép của mức bảo mật (Nội bộ mặc định chỉ Claude).", "NFR-21, R12", "Nhóm & vai; Chính sách", "M"],
    ["F-10", "Định tuyến lượt", "Chỉ tin của chủ nhóm nhắc @bot / reply tin bot mới tạo lượt. Tin nhắc nhiều bot → một lượt cho từng bot theo thứ tự được nhắc, chạy lần lượt. Tin của thành viên và tin không nhắc ai chỉ ghi nhật ký Thread; lệnh tra cứu vẫn trả lời.", "R1, R6", "Định tuyến lượt", "M"],
    ["F-11", "Chạy lượt agent", "Dựng ngữ cảnh (vai, vai các bot khác, mức bảo mật, nhật ký, file quyết định, SKILL.md đã gắn); chạy CLI trong workspace ở chế độ hạn chế: không shell, luật quyền do lõi cấp, công cụ của lõi qua MCP; đọc tín hiệu.", "R10, FR-06, FR-11, FR-12", "Định tuyến; AgentRuntime", "M"],
    ["F-12", "Phiên agent theo (nhóm, bot)", "Khoá phiên là (nhóm, bot): cùng bot ở hai nhóm không chung transcript. Đổi vai, skill hoặc provider → tạo phiên mới.", "FR-33", "AgentRuntime; Repository", "M"],
    ["F-13", "Bot hỏi bot", "Tín hiệu ask → đăng câu hỏi ra nhóm, tạo lượt cho bot được hỏi. Bộ đếm ask riêng, tối đa 3/Thread; ask hỏi nhiều bot thì cộng đủ số bot trước khi tạo lượt; vượt trần thì không tạo lượt nào.", "R8", "Điều phối Thread", "M"],
    ["F-14", "Leo thang", "Ask thứ 4, review vòng 4, hết trần lượt CLI, không có reviewer hợp lệ, hoặc tín hiệu escalate → tag chủ nhóm, Thread chờ người.", "R8", "Điều phối Thread", "M"],
    ["F-15", "Quyết định giải pháp", "“Chốt” → bot soạn bản quyết định vào output/ → lõi báo đường dẫn, chủ nhóm reply “ok” → lõi lưu bản gốc + băm ở data/ và CSDL, chép sang decisions/ (bản sao, agent chỉ đọc); nạp vào mọi lượt sau; băm lệch → khôi phục từ bản gốc. Hình 9.", "R6, R7", "Quyết định giải pháp", "M"],
    ["F-16", "Review và “đạt”", "request_review → reviewer do chủ nhóm giao, khác bot tác giả (bot đã ghi các file nằm trong request_review); chưa đạt → lượt sửa (bộ đếm review riêng, tối đa 3 vòng); đạt → Thread Đạt. Chủ nhóm reply “không đạt” → Thread về Đang làm. Mỗi bước hiện trên nhóm (F-27).", "Đạt, R15", "Điều phối Thread", "M"],
    ["F-17", "Nhận file vào", "Nhóm Thoải mái: file ≤ 20 MB thả vào chat được lưu vào input/. Nhóm Nội bộ: từ chối.", "R9, R11", "TelegramAdapter; Chính sách", "M"],
    ["F-18", "Giao kết quả theo mức bảo mật", "Nội bộ: mọi tin (reply, ask, góp ý review, ĐẠT) chỉ theo mẫu cố định do lõi dựng; văn bản tự do của agent ghi vào file trong workspace. Thoải mái: nội dung đầy đủ + gửi file.", "R11, FR-04, FR-32, NFR-04", "Chính sách; Bộ gửi tin", "M"],
    ["F-19", "Chặn Gemini với tài liệu công ty", "Gemini cấm ở nhóm Nội bộ. Ở nhóm Thoải mái chỉ khi chủ nhóm bật, và lượt Gemini chạy trong một thư mục trống riêng, không thấy workspace; prompt chỉ gồm câu vừa gửi, không kèm nhật ký nhóm.", "R12, NFR-03", "Chính sách", "M"],
    ["F-20", "Giới hạn chạy và hạn mức", "Mỗi nhóm một lượt CLI tại một lúc (các bot dùng chung workspace); tối đa 3 lượt đồng thời giữa các nhóm; trần tổng lượt CLI mỗi Thread; báo hết hạn mức, chỉ gợi ý provider mà chính sách nhóm cho phép (Nội bộ mặc định chỉ Claude, không bao giờ Gemini).", "NFR-13, ràng buộc", "Hàng đợi; Theo dõi hạn mức", "M"],
    ["F-21", "Audit và trạng thái", "Ghi mọi lượt (ai, nhóm, bot, provider, file, tín hiệu, thời gian, mức dùng); /status.", "FR-34, FR-35, SEC-06, NFR-07", "AuditLog", "M"],
    ["F-22", "Lưu đội để dùng lại", "“Lưu đội này lại” → SavedTeam; áp vào nhóm mới.", "R5", "Nhóm & vai", "S"],
    ["F-23", "Xem thư viện skill", "/skills hoặc “có những skill nào?” → tên, mô tả, phiên bản, trạng thái, mức bảo mật cho phép; chỉ hiện skill dùng được ở nhóm đang hỏi. Có sẵn skill docx.", "R13", "Thư viện skill; Tra cứu", "M"],
    ["F-24", "Thêm / cập nhật / ngừng skill", "Quản trị viên chép thư mục skill vào kho, gõ /skill nap → kiểm tra tự động (cấu trúc, mức cho phép, lệnh cấm) → chờ duyệt → /skill duyet. Giữ phiên bản, ngừng dùng được. Thả file zip vào chat để thêm: làm sau.", "R13, SEC-02, thay FR-23..29", "Thư viện skill; Kho skill", "M"],
    ["F-25", "Gắn skill cho vai", "“@Bot3 dùng thêm skill X” (hoặc ghi trong lời giao vai) → kiểm tra đã duyệt và hợp mức bảo mật → lõi nạp SKILL.md vào ngữ cảnh mỗi lượt của vai đó; script của skill chỉ chạy qua công cụ của lõi; ghi vào tin ghim.", "R13, R3", "Thư viện skill; WorkspaceManager", "M"],
    ["F-26", "Xem vai của một bot", "“@Bot1 đang làm vai gì?” hoặc /vai @Bot1 → vai, chỉ dẫn, provider, skill, có là reviewer trong nhóm này. /vai @Bot1 tatca → mọi nhóm bot có vai mà người hỏi là thành viên (theo GroupMember). /vai → bảng vai cả nhóm. Đọc CSDL, không tốn lượt AI.", "R14, R4", "Tra cứu vai & trạng thái", "M"],
    ["F-27", "Hiện luồng review trên nhóm", "Đăng lên nhóm mỗi bước: gửi review (vòng n/3), kết luận chưa đạt + góp ý (Thoải mái) hoặc số góp ý + đường dẫn (Nội bộ), đã sửa, ĐẠT (file, người duyệt, số vòng) là tin mới được ghim, tách khỏi tin ghim vai. Góp ý chi tiết lưu review/ trong workspace; nhóm Nội bộ theo mẫu cố định.", "R15, R11", "Điều phối Thread; Bộ gửi tin; Chính sách", "M"],
    ["F-28", "Thành viên nhóm", "Ghi GroupMember khi User trong allowlist viết lần đầu trong nhóm; chủ nhóm có thể thêm/bớt. Dùng để lọc /vai tatca và quyền góp ý.", "1a, R14", "Nhóm & vai", "M"],
    ["F-29", "Công cụ Word của lõi", "docx_read (đọc mẫu, nhận xét: đoạn văn + style, bảng) và docx_build (sao mẫu, thay chữ, điền bảng, chèn/xoá đoạn). Chỉ đọc input/, templates/, output/; chỉ ghi output/; không chạm decisions/. Đã thử đạt (mục 7.4).", "R10, SEC-01, SEC-03", "Công cụ của lõi", "M"],
]
T(["Mã", "Chức năng", "Mô tả", "Yêu cầu nguồn", "Khối thực hiện", "Ph."], F, [1.1, 2.9, 6.6, 2.4, 3.1, 0.9], size=9)
H("4.1 Kiểm tra độ phủ: yêu cầu → chức năng", 2)
P("Mọi yêu cầu v2.2 đều có ít nhất một chức năng đáp ứng.")
T(["Yêu cầu", "Chức năng", "Hình minh hoạ"], [
    ["R1 Nhóm Telegram nhiều bot", "F-01, F-10", "Hình 1, 4"],
    ["R2 Bể bot", "F-03", "Hình 3"],
    ["R3 Giao vai bằng lời", "F-06, F-08", "Hình 5"],
    ["R4 Nhắc lại, ghim, tiền tố", "F-07", "Hình 5"],
    ["R5 Lưu đội", "F-22 (sau)", "Hình 3"],
    ["R6 Hai chế độ", "F-10, F-15", "Mục 9.2"],
    ["R7 File quyết định giải pháp", "F-15", "Hình 9"],
    ["R8 Hỏi nhau ≤ 3, leo thang", "F-13, F-14, F-20", "Hình 6, 10; mục 6.7"],
    ["R9 Thư mục dự án, thả file", "F-01, F-17", "Hình 12"],
    ["R10 Mẫu không cố định, agent như CLI", "F-11, F-29", "Hình 4, 7; mục 7.4"],
    ["R11 Mức bảo mật theo nhóm", "F-02, F-17, F-18", "Mục 10"],
    ["R12 Gemini không nhận tài liệu công ty", "F-09, F-19", "Mục 10"],
    ["R13 Quản lý skill", "F-23, F-24, F-25", "Hình 8; mục 5.5"],
    ["R14 Xem vai của bot", "F-26, F-28", "Mục 5.6; Hình 3"],
    ["R15 Review, “đạt” hiện trên nhóm", "F-16, F-27", "Hình 7; mục 6.4"],
    ["Đạt = chủ nhóm hoặc reviewer", "F-05, F-16, F-27", "Hình 7, 10"],
    ["1a Nhiều kỹ sư, một chủ/nhóm, tự cài", "F-01, F-04, F-05, F-28", "Hình 3, 13"],
], [6.5, 5.0, 5.5])
page_break()

# ================= 5 LOGICAL =================
H("5. Logical view", 1)
H("5.1 Các khối chức năng", 2)
P("Hệ thống chia bốn tầng. Chỉ hai tầng bộ nối chạm vào thế giới bên ngoài; lõi điều phối không import Telegram hay "
  "tên CLI cụ thể. Đây là điều kiện để thêm Teams/Slack hoặc chuyển sang API key mà không viết lại lõi.")
FIG("h2_logical", "Hình 2. Logical view – các khối chức năng")
T(["Khối", "Trách nhiệm", "Chức năng"], [
    ["TelegramAdapter", "Nhận tin/file từ mọi bot trong bể; đăng tin, gửi file, ghim tin bằng đúng bot; khử trùng lặp", "F-03, F-17, F-18"],
    ["Kiểm soát truy cập", "Allowlist người + nhóm; kiểm tra quyền chủ nhóm cho từng hành động", "F-04, F-05"],
    ["Nhóm & vai", "Đăng ký nhóm, thành viên, mức bảo mật; diễn giải lời giao vai; xác nhận, ghim; đổi provider; lưu đội", "F-01, F-02, F-06..F-09, F-22, F-28"],
    ["Định tuyến lượt", "Chọn bot cho mỗi tin; dựng ngữ cảnh cho lượt; ghi nhật ký nhóm", "F-10, F-11"],
    ["Điều phối Thread", "Mở/gắn/đóng Thread; đếm lượt hỏi nhau và vòng review; leo thang; kết thúc “đạt”; phát sự kiện review ra nhóm", "F-13, F-14, F-16, F-27"],
    ["Chính sách bảo mật", "Dựng mẫu tin Nội bộ cho mọi tin ra; chặn file vào/ra theo mức; chặn Gemini", "F-17, F-18, F-19"],
    ["Quyết định giải pháp", "Xác nhận “chốt”; là thành phần duy nhất ghi decisions/; nạp vào lượt; kiểm tra băm", "F-15"],
    ["Hàng đợi & lập lịch", "Hàng đợi theo nhóm, một lượt CLI mỗi nhóm tại một lúc; tối đa 3 lượt đồng thời toàn hệ thống", "F-20"],
    ["Theo dõi hạn mức", "Nhận lỗi hết hạn mức từ runtime, báo trong nhóm, hỏi đổi provider", "F-20"],
    ["Thư viện skill", "Danh mục skill; kiểm tra, duyệt, phiên bản, ngừng dùng; gắn skill cho vai; cấp SKILL.md cho lượt", "F-23, F-24, F-25"],
    ["Tra cứu vai & trạng thái", "Trả lời /vai, /skills, /status từ CSDL; lọc theo quyền người hỏi; không chạy agent", "F-21, F-23, F-26"],
    ["Bộ gửi tin", "Đăng bằng đúng bot, tiền tố [Vai], ghim tin; định dạng các tin review / ĐẠT", "F-07, F-18, F-27"],
    ["AgentRuntime (Claude/Cursor/Gemini)", "Chạy một lượt trong workspace, giữ phiên, trả văn bản + tín hiệu + file đổi + lỗi", "F-11, F-12"],
    ["Repository, AuditLog", "Lưu trạng thái nhóm, vai, Thread, lượt, phiên; audit mỗi lượt", "F-12, F-21"],
    ["WorkspaceManager", "Tạo thư mục nhóm; sinh chỉ dẫn nhóm (nạp vào lượt qua --append-system-prompt) và luật quyền ở data/<nhóm>/, ngoài workspace; luật chỉ cho ghi output/, review/", "F-01, F-11"],
    ["Công cụ của lõi (MCP)", "Tiến trình MCP stdio đi kèm mỗi lượt, gắn với gốc workspace của nhóm; docx_read, docx_build; tự kiểm đường dẫn", "F-29, F-25"],
    ["Kho skill", "Thư mục skills/<tên>/<phiên bản>/ trên đĩa; chỉ quản trị viên ghi", "F-24"],
], [4.0, 9.4, 3.6])
H("5.2 Interface giữa lõi và bên ngoài", 2)
T(["Interface", "Thao tác chính", "Ghi chú"], [
    ["ChannelAdapter", "sự kiện vào MessageEvent(nhóm, người gửi, text, mentions, reply_to, file); send(nhóm, bot, text); send_file; pin", "Telegram trước; Teams/Slack sau"],
    ["AgentRuntime", "run(workspace, session_id, prompt hệ thống, tin cần xử lý, file luật quyền, danh sách công cụ lõi, schema tín hiệu, timeout) → kết quả", "Kết quả: văn bản, tín hiệu, session mới, file đổi, mức dùng, lỗi"],
    ["Repository", "CRUD cho User, Group, RoleAssignment, Thread, Turn, AgentSession, SavedTeam, Skill, gắn vai–skill; nhật ký nhóm", "SQLite → Postgres không đổi lõi"],
    ["AuditSink", "write(bản ghi lượt / sự kiện từ chối)", "audit.jsonl"],
    ["WorkspaceStore", "tạo workspace, liệt kê file thay đổi sau lượt, lưu file vào input/, chép bản sao quyết định", "Ổ đĩa cục bộ hoặc volume"],
    ["CoreTools (MCP)", "tools/list, tools/call theo giao thức MCP stdio; nhận gốc workspace khi khởi động", "docx trước; thêm công cụ khi skill cần chạy mã"],
    ["SkillStore", "liệt kê, đọc skill theo tên + phiên bản, kiểm tra một thư mục skill → báo cáo", "Thư mục skills/; sau có thể là kho Git nội bộ"],
], [3.2, 9.0, 4.8])
H("5.3 Mô hình dữ liệu", 2)
P("Điểm khác biệt chính so với các gateway có sẵn: vai gắn với cặp (nhóm, bot), không gắn vào bot. Cùng một bot có thể "
  "là “Giải pháp” ở nhóm này và “Thư ký” ở nhóm khác. Phiên CLI (AgentSession) cũng khoá theo (nhóm, bot) và lưu dấu "
  "vai + skill + provider; dấu đổi thì tạo phiên mới để bot không làm theo vai cũ còn trong transcript. GroupMember ghi ai "
  "thuộc nhóm nào. Tài liệu công việc không nằm trong CSDL, chỉ nằm trong workspace.")
FIG("h3_domain", "Hình 3. Logical view – mô hình dữ liệu")
H("5.4 Hợp đồng tín hiệu của agent", 2)
P("Tín hiệu là hợp đồng điều khiển giữa agent và lõi. Lõi chỉ hành động theo tín hiệu, không đoán ý từ văn bản tự do.")
B([("Tách khỏi bài viết: ", "với Claude Code, lượt chạy `claude -p --output-format json --json-schema <schema>` để tín hiệu "
    "về dưới dạng structured output, tách khỏi văn bản (Claude Code 2.1.327 trên VM có cờ này). Với CLI khác: một khối "
    "JSON trong thẻ cố định ở cuối bài, lõi cắt ra theo thẻ."),
   ("Không tách được hoặc sai schema: ", "không tạo lượt tiếp theo, ghi audit, báo lỗi ngắn (mục 6.8)."),
   ("Không bao giờ đăng tín hiệu: ", "chuỗi tín hiệu không bao giờ đi vào tin Telegram."),
   ("Mọi trường có chữ (reply, câu hỏi ask, góp ý review) ", "đều đi qua cùng bộ chính sách; ở nhóm Nội bộ chúng chỉ được ghi vào file, tin đăng theo mẫu cố định.")])
T(["Trường", "Ý nghĩa", "Lõi xử lý"], [
    ["reply", "Nội dung trả lời", "Thoải mái: đăng. Nội bộ: ghi vào workspace, đăng mẫu cố định"],
    ["ask", "Danh sách {bot, câu hỏi}", "số_ask + số bot ≤ 3 thì tạo lượt cho từng bot; vượt thì không tạo lượt nào, leo thang"],
    ["escalate", "{lý do, câu hỏi}", "Tag chủ nhóm; Thread → chờ người"],
    ["request_review", "{files, ghi chú}", "Tạo lượt review cho reviewer hợp lệ (do chủ giao, khác tác giả); không có → tag chủ nhóm"],
    ["verdict", "dat | chua_dat | null (chỉ reviewer)", "dat → Thread Đạt (chủ nhóm mở lại được); chua_dat → lượt sửa nếu còn vòng"],
    ["files", "File đã tạo/sửa trong workspace", "Báo đường dẫn; nhóm Thoải mái có thể gửi file"],
], [3.0, 5.5, 8.5])
H("5.5 Thư viện skill", 2)
P("Skill là cách thêm năng lực cho bot mà không sửa mã lõi: soạn Word theo mẫu, review tài liệu, tóm tắt nhận xét "
  "đối tác… Skill theo đúng định dạng Agent Skills của Claude Code (thư mục có SKILL.md), nên dùng lại được skill có sẵn "
  "như docx. Vì lượt agent chạy --restricted và không có shell, lõi nạp nội dung SKILL.md vào ngữ cảnh lượt (mọi CLI như "
  "nhau), còn phần script của skill được bọc thành công cụ của lõi (mục 7.4).")
T(["Thành phần", "Nội dung"], [
    ["Một skill", "skills/<tên>/<phiên bản>/SKILL.md (+ mẫu). Phần đầu SKILL.md khai báo: tên, mô tả, mức cho phép (noi_bo / thoai_mai), công cụ của lõi cần dùng. Skill có script: script phải được bọc thành công cụ của lõi (việc của người phát triển bản cài) trước khi duyệt."],
    ["Trạng thái", "mới nạp → chờ duyệt → đã duyệt → ngừng dùng. Chỉ skill “đã duyệt” được gắn và chạy."],
    ["Kiểm tra tự động khi nạp", "Có SKILL.md hợp lệ; chỉ khai báo công cụ của lõi đã có; skill kèm script không được duyệt cho tới khi script được viết lại thành công cụ của lõi; skill cần mạng không cho Nội bộ. Lõi không bao giờ nạp hay chạy script nằm trong thư mục skill."],
    ["Ai làm gì", "Quản trị viên: nạp, duyệt, ngừng. Chủ nhóm: xem, gắn/bỏ skill cho vai. Kỹ sư thành viên: xem."],
    ["Gắn skill", "Theo vai trong nhóm (RoleAssignment ↔ Skill). Lõi nạp SKILL.md vào ngữ cảnh mỗi lượt của vai (không cài vào .claude/skills/ vì lượt chạy --restricted). Ngừng một skill thì các lượt sau không còn nhận nó; báo trong các nhóm đang dùng."],
    ["Skill có sẵn (MVP)", "docx: hướng dẫn soạn Word theo mẫu, dùng công cụ docx_read / docx_build của lõi. Các skill khác thêm dần theo nhu cầu."],
], [4.0, 13.0])
H("5.6 Tra cứu vai và trạng thái", 2)
P("Các câu hỏi tra cứu được trả lời thẳng từ CSDL, không chạy agent, nên không tốn hạn mức và trả lời ngay. Có thể hỏi "
  "bằng lời (“@Bot1 đang làm vai gì?”) hoặc bằng lệnh.")
T(["Hỏi", "Trả lời", "Phạm vi"], [
    ["/vai @Bot1 hoặc “@Bot1 đang làm vai gì?”", "Vai, chỉ dẫn (rút gọn), provider, skill đã gắn, có là reviewer, Thread đang làm", "Nhóm hiện tại"],
    ["/vai @Bot1 tatca", "Danh sách (nhóm, vai) của Bot1", "Chỉ các nhóm mà người hỏi là thành viên; quản trị viên thấy hết"],
    ["/vai", "Bảng vai của cả nhóm (như tin ghim)", "Nhóm hiện tại"],
    ["/skills", "Skill dùng được trong nhóm và skill đang gắn cho từng vai", "Nhóm hiện tại"],
    ["/status", "Thread đang mở, lượt đang chạy / chờ, hạn mức", "Nhóm hiện tại"],
], [5.0, 7.0, 5.0])
page_break()

# ================= 6 PROCESS =================
H("6. Process view", 1)
H("6.1 Mô hình chạy", 2)
P("Toàn bộ hệ thống là một tiến trình Python dùng asyncio. Mỗi bot có một poller long polling. Tin đi qua khử trùng "
  "lặp, kiểm soát truy cập, định tuyến, rồi vào hàng đợi riêng của (nhóm, bot). Worker pool lấy lượt từ hàng đợi, chạy "
  "agent CLI thành tiến trình con ở chế độ hạn chế (không shell; luật quyền và công cụ MCP do lõi cấp), rồi đưa kết quả qua bộ lọc chính sách trước khi đăng.")
FIG("h4_process", "Hình 4. Process view – luồng chạy trong tiến trình")
B([("Tuần tự theo nhóm: ", "một nhóm chỉ chạy một lượt CLI tại một lúc, vì các bot cùng nhóm ghi chung một workspace; phiên CLI vẫn riêng theo (nhóm, bot). Tra cứu không chạy CLI nên không bị khoá."),
   ("Ai tạo lượt: ", "chỉ tin của chủ nhóm. Tin của thành viên vào nhật ký Thread, bot đọc ở lượt sau."),
   ("Song song có giới hạn: ", "giữa các nhóm khác nhau, tối đa 3 lượt đồng thời (cấu hình được), để không vượt RAM và hạn mức."),
   ("Không chặn: ", "khi một lượt đang chạy, tin mới vẫn được nhận và xếp hàng."),
   ("Trạng thái bền: ", "Thread, lượt và phiên lưu trong CSDL, nên tiến trình khởi động lại vẫn chạy tiếp được.")])
H("6.2 Giao vai bằng lời", 2)
FIG("h5_seq_roles", "Hình 5. Giao vai bằng lời (R3, R4)")
B([("Lượt diễn giải vai ", "chỉ nhận câu nói và danh sách bot, không nhận file workspace."),
   ("Vai mới ở trạng thái chờ; ", "“ok” chỉ có hiệu lực khi chủ nhóm reply đúng tin xác nhận. Trước đó bot giữ vai cũ và từ chối việc mới."),
   ("Khi vai có hiệu lực: ", "huỷ phiên CLI cũ của (nhóm, bot); sửa nội dung tin ghim vai (không ghim tin mới).")])
H("6.3 Bot hỏi bot và leo thang", 2)
FIG("h6_seq_ask", "Hình 6. Bot hỏi bot và leo thang (R8)")
H("6.4 Review và kết thúc “đạt”", 2)
P("Luồng bot↔bot vẫn chuyển trong lõi (AD-04) để lõi đếm được vòng, nhưng mỗi bước review đều được đăng lên nhóm "
  "để mọi người theo dõi và chủ nhóm chen vào được bất cứ lúc nào (“đạt”, “dừng”, góp ý thêm).")
B([("Reviewer ", "là quyền chủ nhóm giao cho một bot (là_reviewer). Tác giả là bot đã ghi các file nằm trong request_review; tác giả không được review các file đó (file thảo luận do lõi ghi không tính); "
    "không có reviewer hợp lệ thì tag chủ nhóm."),
   ("Mở lại: ", "sau tin ĐẠT, chủ nhóm reply “không đạt: …” → Thread về Đang làm, số_vòng_review về 0, gỡ ghim tin ĐẠT, lý do được giao cho bot soạn."),
   ("Hai tin ghim: ", "tin vai (một tin, sửa nội dung khi đổi vai) và tin ĐẠT (tin mới mỗi lần đạt).")])
FIG("h7_seq_review", "Hình 7. Review và kết thúc “đạt”, hiển thị trên nhóm")
T(["Bước", "Tin trên nhóm (bot đăng)", "Nhóm Nội bộ", "Nhóm Thoải mái"], [
    ["Gửi review", "[Soạn Word] Xong v1 → nhờ @Bot2 review (vòng 1/3)", "Đường dẫn file", "Kèm file"],
    ["Chưa đạt", "[Phản biện] Vòng 1/3: CHƯA ĐẠT – 3 góp ý", "Mẫu cố định: số góp ý + đường dẫn review/v1.md", "Góp ý đầy đủ"],
    ["Đã sửa", "[Soạn Word] Đã sửa v2 theo 3 góp ý → review lại (vòng 2/3)", "Như trên", "Như trên"],
    ["Đạt", "ĐẠT – file kết quả, người duyệt, số vòng; tin được ghim", "Đường dẫn file", "Kèm file"],
    ["Hết 3 vòng / không có reviewer", "Tag @chủ nhóm: cần người duyệt, kèm số vòng và đường dẫn các file review/", "Như cột trên", "Như cột trên"],
    ["Chủ nhóm nói “đạt”", "ĐẠT – duyệt: chủ nhóm; tin được ghim", "Đường dẫn file", "Kèm file"],
    ["Chủ nhóm “không đạt”", "[Hệ thống] Mở lại Thread – lý do giao cho @Bot3", "Mẫu cố định", "Đầy đủ"],
], [3.0, 6.6, 4.0, 3.4])
H("6.5 Thêm, duyệt và gắn skill", 2)
FIG("h8_seq_skill", "Hình 8. Thêm, duyệt và gắn skill (R13)")
H("6.6 Chốt quyết định giải pháp", 2)
FIG("h9_seq_decide", "Hình 9. Chốt quyết định giải pháp (R7)")
H("6.7 Vòng đời Thread", 2)
P("Mở Thread: mỗi tin của chủ nhóm nhắc @bot mà không reply vào Thread đang mở. Gắn Thread: tin reply, và mọi lượt "
  "ask/review/sửa sinh ra từ một lượt, thuộc Thread của lượt đó.")
P("Quy tắc giới hạn (chốt một cách hiểu cho chữ, hình và nghiệm thu):", bold_prefix="")
T(["Trần", "Quy tắc", "Khi chạm trần"], [
    ["Ask", "Đủ 3 ask thì ask kế tiếp không chạy. Một ask hỏi n bot được tính n, cộng trước khi tạo lượt; không fan-out vượt trần.", "Tag chủ nhóm; chủ trả lời → số_ask về 0"],
    ["Vòng review", "Đủ 3 vòng thì vòng kế tiếp không chạy. Độc lập với đếm ask.", "Tag chủ nhóm duyệt; chủ trả lời → số_vòng_review về 0"],
    ["Lượt CLI của Thread", "Mỗi lần gọi CLI đều tính (bot hỏi, bot trả lời, bot chạy tiếp, review, sửa). Đề xuất trần 12, cấu hình được.", "Tag chủ nhóm; chủ cho chạy tiếp → cấp thêm một lượng"],
    ["Đồng thời", "Mỗi nhóm một lượt CLI tại một lúc; giữa các nhóm tối đa 3.", "Xếp hàng"],
], [3.2, 9.0, 4.8])
P("Hệ quả hạn mức: một ask trong Hình 6 tốn ba lần gọi CLI (bot hỏi, bot trả lời, bot hỏi chạy tiếp). Ba ask và ba vòng "
  "review có thể thành khoảng 15 lần gọi model, nên trần 3 không phải trần số lần gọi model; trần lượt CLI là để chặn việc này.")
FIG("h8_state", "Hình 10. Vòng đời của một Thread", width=16)
H("6.8 Xử lý lỗi", 2)
T(["Tình huống", "Hệ thống làm gì"], [
    ["Claude hết hạn mức", "Bot báo trong nhóm kèm giờ dự kiến hồi phục; chỉ gợi ý provider chính sách nhóm cho phép (Nội bộ: không có Gemini); không tự đổi."],
    ["Lượt quá thời gian", "Dừng tiến trình con; lượt → “loi”, không tự chạy lại; báo trong nhóm; chủ nhóm quyết định chạy lại."],
    ["CLI lỗi / tín hiệu không đọc được", "Ghi audit; đăng thông báo ngắn; không tạo lượt tiếp theo; không đăng chuỗi tín hiệu."],
    ["File quyết định bị đổi ngoài lõi", "Băm không khớp → không chạy lượt, tag chủ nhóm, khôi phục từ bản gốc ở data/ (phiên bản + băm lưu trong CSDL)."],
    ["Tiến trình labour dừng", "Tự khởi động lại (Task Scheduler / Docker restart). Lượt đang “dang_chay” lúc dừng chuyển thành “loi” và không tự chạy lại (tránh soạn Word hai lần); báo trong nhóm; chủ nhóm quyết định chạy lại."],
    ["Mất kết nối Telegram", "Poller thử lại có giãn cách; tin đến sau được xử lý bình thường."],
    ["Một tin đến qua nhiều bot", "Khử trùng lặp theo (chat_id, message_id), chỉ xử lý một lần. Tin nhắc nhiều bot: một lượt cho từng bot được nhắc, theo thứ tự nhắc, không bỏ tin và không nhân đôi."],
    ["Skill không qua kiểm tra", "Không cho duyệt; báo lý do cho quản trị viên."],
    ["Skill lỗi khi chạy", "Báo trong nhóm, ghi audit tên + phiên bản skill; quản trị viên có thể ngừng skill."],
], [5.0, 12.0])
page_break()

# ================= 7 DEV =================
H("7. Development view", 1)
H("7.1 Cấu trúc gói mã nguồn", 2)
P("Quy tắc phụ thuộc: labour.core chỉ phụ thuộc labour.ports; các adapter triển khai interface trong ports; labour.app "
  "tạo và tiêm adapter vào lõi lúc khởi động. Thêm một kênh hay một nhà cung cấp AI là thêm một gói adapter.")
FIG("h9_dev", "Hình 11. Development view – gói mã nguồn và chiều phụ thuộc")
H("7.2 Công nghệ", 2)
T(["Hạng mục", "Lựa chọn", "Lý do"], [
    ["Ngôn ngữ", "Python 3.12, quản lý gói bằng uv", "Đã có trên VM; hệ sinh thái bot và AI tốt"],
    ["Telegram", "aiogram 3", "Một tiến trình chạy nhiều bot, async"],
    ["Lưu trữ", "SQLAlchemy + Alembic; SQLite (MVP), Postgres (sau)", "Đổi CSDL không đổi lõi"],
    ["Agent mặc định", "Claude Code CLI: `claude -p --resume --output-format json --json-schema … --restricted --settings <luật của nhóm> --tools Read,Write,Edit,Glob,Grep --mcp-config <công cụ lõi> --strict-mcp-config --permission-mode dontAsk`", "Subscription hiện có; cách ly đã thử đạt trên Windows (mục 7.4)"],
    ["Công cụ Word", "MCP stdio server của lõi, Python + python-docx (không cần gói mcp)", "Thay cho script của skill docx; đã thử đạt"],
    ["Phiên bản Claude Code", "Ghim một phiên bản, tắt tự cập nhật; nâng có kiểm soát", "Hành vi quyền có thể đổi giữa các bản"],
    ["Agent tuỳ chọn", "cursor-agent, Gemini CLI", "Chỉ khi chạy headless được"],
    ["Đóng gói", "Dockerfile + docker-compose.yml (bản sản phẩm)", "Khách cài bằng một lệnh"],
    ["Kiểm thử", "pytest; FakeChannel, FakeRuntime", "Kiểm lõi không cần mạng"],
], [3.0, 7.0, 7.0])
H("7.3 Chiến lược kiểm thử", 2)
B([("Đơn vị: ", "lõi chạy với FakeChannel + FakeRuntime: định tuyến, quyền chủ nhóm, đếm lượt, leo thang, reviewer, chính sách bảo mật."),
   ("Tích hợp: ", "ClaudeCodeRuntime chạy thật một lượt trong workspace tạm; Telegram chạy thật với nhóm thử."),
   ("Nghiệm thu: ", "chạy trọn kịch bản mục 9.2 với nhận xét đối tác thật (đã lọc) và các kiểm tra ở mục 10, 12."),
   ("Kiểm thử cách ly: ", "hai bộ thử ở mục 7.4 thành test tự động; chạy lại mỗi lần nâng Claude Code.")])
H("7.4 Kết quả thử trên VM (19/11/2026)", 2)
P("Hai lần thử trên VM Windows, gọi `claude.exe` thẳng từ Python. Kết quả được kiểm bằng hệ thống file và git remote, "
  "không dựa vào lời bot. Chi tiết và cách chạy lại: spike/2026-11-19-windows-denylist/README.md và spike/2026-11-19-docx-mcp/README.md.")
T(["Cấu hình", "Kết quả", "Kết luận"], [
    ["A – luật trong workspace/.claude/settings.json (HLD v0.4)", "Luật cho phép bị bỏ vì workspace chưa “trust”: bot không ghi được cả output/; agent có thể sửa file luật của chính nó", "Loại"],
    ["B – luật do lõi cấp (--settings --restricted), agent có shell", "Chặn đúng Read/Write/Edit, git push, make; nhưng `git -c x=y push` lách được (đã push lên remote) và `python -c` đọc được workspace nhóm khác", "Loại"],
    ["C – như B, không có shell", "Đạt cả 10 ca: không đọc/ghi nhóm khác, không ghi decisions/, không push; --json-schema trả tín hiệu tách khỏi bài", "Chọn"],
    ["C + công cụ Word của lõi (Sonnet)", "Soạn đạt theo mẫu có ô {{…}} (28 s) và theo bản phản hồi cũ làm mẫu (22 s, không sót nội dung cũ); bot cố đọc nhóm khác / ghi decisions/ qua công cụ đều bị từ chối", "Chọn"],
], [4.6, 9.4, 3.0])
P("Hệ quả: agent không có Bash/PowerShell; mọi việc cần chạy mã đi qua công cụ của lõi; luật quyền nằm ngoài workspace; "
  "ghim phiên bản Claude Code (đã tự cập nhật từ 2.1.327 lên 2.1.328 ngay trong lúc thử). Luật chỉ cho ghi output/, review/ dùng cùng cơ chế "
  "đã đạt với decisions/; cần đưa input/, templates/ vào bộ thử.")

# ================= 8 PHYSICAL =================
H("8. Physical view", 1)
P("Cùng một mã nguồn chạy hai kiểu triển khai:")
T(["", "Bản cá nhân (MVP)", "Bản sản phẩm"], [
    ["Máy chạy", "VM người dùng, Windows 10, không WSL, không Docker", "Máy chủ khách, Linux, Docker Compose"],
    ["Tự khởi động lại", "Task Scheduler (tuỳ chọn)", "restart: always"],
    ["AI", "Claude Code subscription đã đăng nhập; ghim phiên bản", "API key / gói doanh nghiệp của khách; ghim phiên bản"],
    ["Workspace", "C:\\Works\\Labour\\workspaces, mở thẳng bằng Word", "Volume trên máy chủ; đồng bộ Syncthing/SMB tuỳ khách bật"],
    ["Cổng mạng", "Không mở cổng vào", "Không mở cổng vào"],
    ["Tài nguyên", "≤ 3 tiến trình CLI đồng thời trên 16 core / 14,6 GB", "Theo số kỹ sư; tách worker khi tải lớn"],
], [3.2, 6.9, 6.9])
H("8.1 Bản cá nhân (MVP)", 2)
P("Chạy thẳng trên Windows của VM: Claude Code đã cài và đăng nhập ở đây, workspace nằm sẵn trên ổ C: để mở bằng Word, "
  "tránh WSL đọc /mnt/c chậm. Không mở cổng vào; mọi kết nối là HTTPS đi ra.")
FIG("h10_phys_mvp", "Hình 12. Physical view – bản cá nhân (MVP)")
H("8.2 Bản sản phẩm", 2)
P("Công ty khách tự cài trên máy chủ Linux của mình bằng Docker Compose. Dữ liệu nằm trên máy chủ của khách; AI dùng "
  "tài khoản/API key của khách. Đồng bộ workspace về máy kỹ sư (Syncthing/SMB) là đường dữ liệu thứ hai ngoài Telegram: "
  "tuỳ khách bật, do chính sách mạng của khách bảo vệ, và nằm ngoài phạm vi mức Nội bộ của hệ thống.")
FIG("h11_phys_prod", "Hình 13. Physical view – bản sản phẩm")
page_break()

# ================= 9 SCENARIOS =================
H("9. Scenarios (+1)", 1)
H("9.1 Ca sử dụng", 2)
FIG("h12_usecase", "Hình 14. Các ca sử dụng", width=15.5)
T(["Ca sử dụng", "Tác nhân", "Chức năng", "Đi qua view"], [
    ["UC-01 Đăng ký nhóm, chọn mức bảo mật", "Chủ nhóm", "F-01, F-02, F-04", "Logical (Nhóm & vai), Physical (workspace)"],
    ["UC-02 Giao / sửa vai bằng lời", "Chủ nhóm", "F-06, F-07, F-08", "Process – Hình 5"],
    ["UC-03 Thảo luận giải pháp với bot", "Chủ nhóm (kỹ sư góp ý vào nhật ký)", "F-10, F-11, F-12", "Process – Hình 4"],
    ["UC-04 Chốt quyết định giải pháp", "Chủ nhóm", "F-15", "Process – Hình 9"],
    ["UC-05 Giao việc soạn tài liệu theo mẫu", "Chủ nhóm", "F-10, F-11", "Process – Hình 4; mục 9.2"],
    ["UC-06 Bot hỏi bot, leo thang", "Bot", "F-13, F-14", "Process – Hình 6, 10"],
    ["UC-07 Review, “đạt” – hiện trên nhóm", "Bot reviewer, chủ nhóm", "F-16, F-27", "Process – Hình 7, 10"],
    ["UC-08 Đổi provider AI bằng lời", "Chủ nhóm", "F-09, F-19", "Logical (Chính sách)"],
    ["UC-09 Đưa file vào, nhận kết quả", "Chủ nhóm, kỹ sư", "F-17, F-18", "Physical – Hình 12; mục 10"],
    ["UC-10 Quản lý User, bể bot, giới hạn", "Quản trị viên", "F-03, F-04, F-20", "Physical (cấu hình)"],
    ["UC-11 Lưu đội để dùng lại (sau)", "Chủ nhóm", "F-22", "Logical (Nhóm & vai)"],
    ["UC-12 Xem, thêm, gắn skill", "Quản trị viên, chủ nhóm", "F-23, F-24, F-25", "Process – Hình 8; mục 5.5"],
    ["UC-13 Xem vai của một bot", "Chủ nhóm, kỹ sư", "F-26", "Logical – mục 5.6"],
], [5.0, 3.0, 3.0, 6.0])
H("9.2 Kịch bản chính: nhận xét đối tác → file Word", 2)
P("Kịch bản nghiệm thu MVP. Mỗi bước ghi chức năng được dùng, để thấy bốn view khớp nhau.")
T(["#", "Bước", "Chức năng", "Chế độ"], [
    ["1", "Tạo nhóm Telegram, thêm Bot1–Bot3, gõ /start, chọn Nội bộ → hệ thống tạo workspaces/phan-hoi-doi-tac-x/", "F-01, F-02", "—"],
    ["2", "Trên đĩa: chép file nhận xét của đối tác (lấy từ SharePoint) vào input/ và file mẫu vào templates/mau_phan_hoi.docx (nhóm Nội bộ không nhận file qua Telegram)", "—", "—"],
    ["3", "Giao vai: Bot1 Giải pháp, Bot2 Phản biện + reviewer, Bot3 Soạn Word (skill docx); các bot nhắc lại vai; “ok”; vai được ghim. Kỹ sư hỏi “@Bot2 đang làm vai gì?” để kiểm tra", "F-06, F-07, F-25, F-26", "—"],
    ["4", "Thảo luận với Bot1, Bot2; Bot2 hỏi Bot1 (≤ 3 ask); chat chỉ hiện mẫu tin cố định, nội dung trong thao-luan/", "F-10, F-11, F-13, F-18", "Tương tác"],
    ["5", "Chủ nhóm “chốt” → Bot1 soạn bản quyết định vào output/ → chủ reply “ok” → lõi lưu bản gốc ở data/, chép sang decisions/", "F-15", "Bàn giao"],
    ["6", "“@Bot3 soạn file phản hồi theo mẫu templates/mau_phan_hoi.docx”; Bot3 vướng hỏi Bot1", "F-11, F-13", "Giao việc"],
    ["7", "Bot3 xong → Bot2 (reviewer do chủ giao, không phải tác giả) review → chưa đạt → Bot3 sửa → Bot2 đạt; từng vòng hiện trên nhóm", "F-16, F-27", "Giao việc"],
    ["8", "Bot2 đăng “ĐẠT – output/phan_hoi_v2.docx · 2 vòng”, tin được ghim; chủ nhóm mở file trên máy", "F-16, F-18, F-21, F-27", "—"],
], [0.7, 10.8, 3.3, 2.2])

# ================= 10 SECURITY =================
H("10. Bảo mật (xuyên suốt các view)", 1)
P("Mỗi nhóm khai báo mức bảo mật khi tạo, mặc định là Nội bộ. Chính sách thực thi ở hai lớp độc lập: chỉ dẫn cho agent "
  "(prompt hệ thống, chỉ dẫn nhóm) và lõi chặn cứng trên mọi tin ra và file. Agent có làm sai thì lõi vẫn chặn.")
T(["", "Nội bộ (mặc định)", "Thoải mái"], [
    ["Nội dung bot đăng lên Telegram", "Chỉ mẫu tin cố định ghép từ trường có kiểu: [Vai], loại việc (danh mục cố định), con số, đường dẫn file. Không chữ nào lấy từ văn bản của agent; reply, câu ask, góp ý review ghi nguyên văn vào file. Áp cho mọi tin: trả lời, ask, review, ĐẠT, chốt", "Đầy đủ"],
    ["Nhận file thả vào Telegram", "Từ chối", "Có, ≤ 20 MB, lưu vào input/"],
    ["Gửi file kết quả lên Telegram", "Không (FR-32), chỉ báo đường dẫn", "Có"],
    ["Gemini", "Cấm, kể cả khi Claude hết hạn mức", "Chỉ khi chủ nhóm bật; chạy trong thư mục trống riêng; prompt chỉ gồm câu vừa gửi, không nhật ký nhóm"],
    ["Grok (Cursor)", "Cấm mặc định; quản trị viên chỉ bật khi hợp đồng của công ty với nhà cung cấp cho phép", "Được khi chủ nhóm chọn; chạy trong workspace như Claude"],
], [4.4, 7.6, 5.0])
T(["Lớp kiểm soát", "Cơ chế", "Yêu cầu"], [
    ["Ai được dùng", "Allowlist User + nhóm đã đăng ký; người lạ → im lặng + audit", "FR-02"],
    ["Quyền trong nhóm", "Chỉ chủ nhóm giao vai, chốt, nói đạt, đổi bảo mật, bật Gemini", "1a"],
    ["Cách ly thư mục", "Agent chạy với cwd = workspace, --restricted; luật quyền do lõi giữ ở data/<nhóm>/, truyền qua --settings; agent chỉ ghi output/ và review/, các thư mục khác chỉ đọc; công cụ của lõi tự kiểm đường dẫn", "FR-22, SEC-01, SEC-04"],
    ["File quyết định", "Chỉ lõi ghi decisions/; luật quyền cấm agent Write/Edit thư mục này; agent không có shell; công cụ của lõi không chạm decisions/; lõi kiểm tra băm trước mỗi lượt", "R7, SEC-03"],
    ["Lệnh nguy hiểm", "Agent không có shell (Bash/PowerShell bị bỏ khỏi --tools). Lý do: cấm lệnh theo tiền tố bị lách được, và cho python là mất cách ly (mục 7.4)", "FR-09, FR-19, SEC-02, SEC-03"],
    ["Chạy mã", "Agent không chạy mã. Lõi là nơi duy nhất chạy mã, qua công cụ MCP do người phát triển bản cài viết và quản trị viên duyệt; mỗi công cụ tự kiểm đường dẫn. Lõi không nạp script trong thư mục skill lúc chạy", "SEC-03"],
    ["Mạng", "Long polling, chỉ HTTPS đi ra, không mở cổng vào", "FR-03"],
    ["Bí mật", "Token bot, API key trong .env, không commit, agent bị deny đọc", "NFR-06, SEC-04"],
    ["Truy vết", "Audit mọi lượt và mọi lần từ chối; giữ ≥ 90 ngày", "FR-34, NFR-07, SEC-06"],
    ["Skill", "Chỉ quản trị viên nạp; kiểm tra tự động + duyệt tay; script chỉ chạy qua công cụ của lõi; nhóm Nội bộ chỉ dùng skill cho phép Nội bộ; audit ghi skill + phiên bản của mỗi lượt", "R13, SEC-02, SEC-03"],
    ["Tra cứu vai", "/vai tatca chỉ hiện nhóm mà người hỏi là thành viên", "1a"],
], [3.6, 9.4, 4.0])
P("Sáu kiểm tra phải đạt trước khi dùng tài liệu thật (4 kiểm tra của chuyên gia + 2 kiểm tra mới). Cả sáu kiểm bằng mã "
  "(test tự động), không chỉ dựa vào prompt. Kiểm tra 2, 4, 6 đã đạt ở mức lượt agent đơn lẻ trong lần thử 19/11 (mục 7.4); "
  "cần chạy lại trên hệ thống hoàn chỉnh:", bold_prefix="")
B(["Người lạ và nhóm chưa đăng ký bị từ chối.",
   "Agent của nhóm này không đọc được workspace của nhóm khác, kể cả bằng đường dẫn tuyệt đối.",
   "Nhóm Nội bộ không nhận và không gửi file tài liệu qua Telegram.",
   "Lệnh make / git push và ghi file ngoài workspace bị chặn.",
   "Nhóm Nội bộ: agent cố trả về nguyên văn hoặc diễn giải tài liệu trong reply/ask/góp ý → tin đăng chỉ có mẫu cố định.",
   "Agent không ghi được decisions/, input/, templates/ (Write/Edit và công cụ của lõi); file quyết định bị đổi ngoài lõi thì lượt không chạy."], style="List Number")

# ================= 11 ADR =================
H("11. Quyết định kiến trúc", 1)
T(["Mã", "Quyết định", "Lý do", "Phương án đã loại"], [
    ["AD-01", "Một dịch vụ, chia khối bên trong (modular monolith)", "Dễ cài cho khách, dễ vận hành; vẫn tách được worker khi tải lớn", "Microservices + hàng đợi (khó cài)"],
    ["AD-02", "Tự xây lõi, không dựng trên OpenClaw hay framework đa agent", "Vai động theo nhóm, trần lượt, reviewer, chế độ Nội bộ đều phải tự viết; tránh bề mặt tấn công lớn và hai hệ quyền", "OpenClaw; LangGraph/CrewAI"],
    ["AD-03", "Vai gắn với (nhóm, bot)", "Đáp ứng bể bot (R2) và giao vai bằng lời (R3)", "Vai gắn cứng vào bot trong cấu hình"],
    ["AD-04", "Tin bot↔bot chuyển trong lõi", "Không phụ thuộc Telegram có cho bot đọc tin bot; lõi đếm được lượt", "Dựa vào chế độ bot-to-bot của Telegram"],
    ["AD-05", "Claude Code CLI là runtime mặc định", "Dùng subscription hiện có; đọc/ghi file văn bản, giữ phiên, structured output; Word qua công cụ của lõi (F-29)", "API key ngay từ đầu (tốn tiền)"],
    ["AD-06", "Lưu trữ qua repository, SQLite trước", "MVP đơn giản; đổi Postgres không đổi lõi", "Postgres ngay từ đầu"],
    ["AD-07", "MVP chạy thẳng trên Windows", "Claude Code và workspace đã ở Windows; tránh /mnt/c chậm", "WSL2, Docker trên VM"],
    ["AD-08", "Tin không nhắc bot nào thì không chạy bot", "Tiết kiệm hạn mức", "Bot tự đọc và trả lời mọi tin"],
    ["AD-09", "Nhóm mặc định là Nội bộ", "An toàn khi người dùng quên chọn", "Mặc định Thoải mái"],
    ["AD-10", "Skill theo định dạng Agent Skills (SKILL.md) của Claude Code", "Dùng lại phần hướng dẫn của skill có sẵn (docx…); lõi nạp SKILL.md vào ngữ cảnh lượt; script bọc thành công cụ lõi", "Định dạng plugin riêng của hệ thống"],
    ["AD-11", "Skill phải được quản trị viên duyệt trước khi dùng", "Skill có thể chứa script chạy được → rủi ro mã độc, lộ dữ liệu", "Chủ nhóm tự thả skill vào nhóm và dùng ngay"],
    ["AD-12", "Mọi bước review đăng lên nhóm; tin ĐẠT được ghim", "Người thấy tiến trình, chen vào được; vẫn đếm vòng trong lõi", "Review ngầm, chỉ báo kết quả cuối"],
    ["AD-13", "Nhóm Nội bộ chỉ đăng mẫu cố định do lõi dựng", "Lọc theo độ dài / trùng nguyên văn không chặn được agent diễn giải lại tài liệu", "Bộ lọc nội dung trên reply tự do"],
    ["AD-14", "Chỉ lõi ghi decisions/; “chốt” có xác nhận", "Agent ghi được mọi thứ trong workspace; lượt sau sẽ đọc bản agent sửa", "Chỉ cảnh báo khi agent sửa"],
    ["AD-15", "Hai bộ đếm (ask, review) độc lập + trần lượt CLI mỗi Thread", "Một cách hiểu cho chữ, hình, nghiệm thu; chặn số lần gọi model thật", "Một bộ đếm chung"],
    ["AD-16", "Tín hiệu qua structured output (--json-schema)", "Tách hẳn khỏi bài viết; sai schema thì dừng", "Đoán JSON trong văn bản"],
    ["AD-17", "Gemini chạy trong thư mục trống riêng", "Lời khẳng định của người không chặn được file đã có trong input/", "Tin vào lời khẳng định của chủ nhóm"],
    ["AD-18", "Agent không có shell; việc cần chạy mã đi qua công cụ MCP của lõi", "Thử trên VM: cấm lệnh theo tiền tố bị lách; python đọc được nhóm khác; không shell thì đạt mọi ca và vẫn soạn Word đạt", "Deny-list lệnh shell; cho phép python cho skill"],
    ["AD-19", "Luật quyền do lõi giữ ngoài workspace, truyền --settings, chạy --restricted", "Luật trong workspace bị bỏ khi chưa trust và agent sửa được", "settings.json trong workspace"],
    ["AD-20", "Ghim phiên bản Claude Code; chạy lại bộ thử cách ly khi nâng", "Claude Code tự cập nhật; hành vi quyền có thể đổi", "Để tự cập nhật"],
    ["AD-21", "Nhóm Nội bộ mặc định chỉ dùng Claude", "Mỗi provider thêm là một nơi tài liệu đi tới; cần quyết định có hợp đồng", "Cho mọi provider trừ Gemini"],
    ["AD-22", "Một lượt CLI mỗi nhóm tại một lúc", "Các bot cùng nhóm ghi chung workspace", "Khoá theo (nhóm, bot)"],
    ["AD-23", "Chỉ chủ nhóm tạo lượt agent", "Theo 1a; thành viên không đổi được file hay tốn hạn mức", "Mọi thành viên gọi được bot"],
], [1.3, 4.6, 6.4, 4.7], size=9)

# ================= 12 RISKS =================
H("12. Rủi ro, câu hỏi mở và nghiệm thu", 1)
T(["Rủi ro / việc cần kiểm tra", "Mức", "Cách xử lý"], [
    ["Điều khoản Anthropic khi gọi `claude -p` từ một dịch vụ riêng, và khi bán sản phẩm", "Cao", "Kiểm tra chính sách hiện hành trước khi xây; bản bán dùng API key / tài khoản của khách"],
    ["Agent làm lộ nội dung ở nhóm Nội bộ", "Cao", "Mẫu tin cố định (AD-13) + 6 kiểm tra bắt buộc"],
    ["Hạn mức subscription khi nhiều bot hỏi nhau", "Trung bình", "Một ask = 3 lần gọi CLI; trần lượt CLI mỗi Thread; đo trong luồng thật rồi chỉnh trần"],
    ["Telegram: bot có thấy mọi tin khi tắt privacy mode; bot-to-bot", "Thấp", "Thiết kế không phụ thuộc (AD-04); kiểm lại Bot API"],
    ["cursor-agent, Gemini CLI chưa cài, chưa rõ chạy headless", "Thấp", "Không chạy được thì MVP chỉ dùng Claude"],
    ["Một tiến trình dừng là cả đội dừng", "Thấp", "Tự khởi động lại; trạng thái bền trong CSDL"],
    ["Skill lấy từ bên ngoài chứa mã độc hoặc làm lộ dữ liệu", "Cao", "Duyệt tay + kiểm tra tự động; lõi không chạy script trong skill; chỉ lấy skill từ nguồn tin cậy"],
    ["Tin review làm nhóm bị nhiễu", "Thấp", "Mỗi bước một tin ngắn; chi tiết trong file review/"],
    ["Công cụ Word thiếu thao tác cho mẫu thật phức tạp (đầu/chân trang, ảnh, đánh số, sửa v1 → v2)", "Trung bình", "Thử với mẫu thật đã lọc; bổ sung thao tác trong LLD"],
    ["Skill có script phải bọc thành công cụ lõi → thêm skill chậm hơn", "Trung bình", "Chấp nhận để giữ cách ly; skill chỉ hướng dẫn (không script) vẫn thêm ngay"],
    ["Claude Code đổi cờ / hành vi quyền khi nâng cấp", "Trung bình", "Ghim phiên bản (AD-20); bộ thử mục 7.4 chạy trong CI"],
    ["Nhóm Nội bộ khó thảo luận vì chat chỉ có mẫu tin và đường dẫn", "Trung bình", "Nội dung đầy đủ ở thao-luan/ trên VM; chấp nhận như R11 đã chốt"],
], [7.6, 2.0, 7.4])
P("Câu hỏi mở: số bot trong bể (gợi ý 4); có cần bot báo tiến độ giữa chừng không; chủ nhóm có được tự thêm skill "
  "cho riêng nhóm mình không (đề xuất: không, ở bản đầu); trần lượt CLI mỗi Thread (đề xuất 12); bản nhiều kỹ sư: "
  "ai được quyền tạo nhóm (đề xuất: quản trị viên khai báo); có cho thành viên tạo lượt theo cấu hình nhóm không (đề xuất: để sau).", bold_prefix="")
P("Tiêu chí nghiệm thu MVP:", bold_prefix="")
B(["Chạy trọn kịch bản 9.2 với một bộ nhận xét đối tác thật (đã lọc); chủ nhóm hoặc bot reviewer nói “đạt”.",
   "Giao vai bằng lời cho bot trong bể ở một nhóm mới, không sửa cấu hình tay.",
   "Sau 3 ask, ask thứ 4 không chạy và tag chủ nhóm; sau 3 vòng review, vòng thứ 4 không chạy và tag chủ nhóm; hai đếm không ảnh hưởng nhau.",
   "Chủ nhóm reply “không đạt” vào tin ĐẠT → Thread về Đang làm.",
   "Khởi động lại khi đang chạy lượt → lượt đó thành lỗi, không tự chạy lại.",
   "Audit ghi đủ mọi lượt.",
   "Tin của thành viên nhắc @bot không tạo lượt; hai bot cùng nhóm không bao giờ chạy đồng thời.",
   "Lịch sử Telegram của nhóm Nội bộ không có file hoặc nội dung nguyên văn tài liệu.",
   "Thêm một skill mới, duyệt, gắn cho bot bằng lời và dùng được ở lượt kế tiếp, không khởi động lại dịch vụ.",
   "“@Bot đang làm vai gì?” trả lời đúng vai, provider, skill trong nhóm.",
   "Mỗi vòng review và tin ĐẠT hiện trên nhóm; tin ĐẠT được ghim.",
   "Đạt đủ 6 kiểm tra bảo mật ở mục 10; bộ thử cách ly mục 7.4 chạy lại đạt trên phiên bản Claude Code đã ghim."])

doc.save(OUT)
print("saved", OUT)
