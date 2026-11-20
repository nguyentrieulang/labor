# Thiết kế v2.2 – Đội AI Agent trên Telegram

> Ngày: 2026-11-18 · Trạng thái: **bản nháp, chờ người dùng duyệt**
> Bối cảnh: dự án đang ở giai đoạn đánh giá/làm rõ yêu cầu; **chưa có code v2.1** → làm mới (greenfield). **Bản đầu chạy ngay trên máy người dùng đang làm việc** (chính là VM công ty: QEMU, 16 core, 15 GB, Windows 10 + WSL Ubuntu-26.04) [Người dùng chốt].
> Nguồn: `notes/2026-11-18-yeu-cau-v2.2.md` (yêu cầu), `notes/2026-11-18-brainstorm-team-agent.md` (nhật ký quyết định), `Requirement_v2.1.docx` (nền tảng kế thừa).
> Ký hiệu: **[Người dùng chốt]** · **[Claude quyết]** = lựa chọn của người thiết kế, người dùng có thể bác · **[Để người xây]** = tự quyết khi làm, không đổi hành vi.

---

## 1. Mục đích và lý do

Một lập trình viên mất nhiều thời gian nhất cho việc **cân nhắc giải pháp, thiết kế và soạn tài liệu** (ví dụ trả lời nhận xét của đối tác bằng một file Word). Hệ thống cho người đó làm **trưởng nhóm của một đội AI agent** trong nhóm chat: giao vai bằng lời, cùng các bot nghĩ giải pháp, rồi giao việc soạn tài liệu và chỉ review kết quả.

Dài hạn, hệ thống được **bán cho công ty, công ty tự cài trên máy chủ của họ** cho cả nhóm kỹ sư dùng, hoặc phát triển thành framework lớn hơn. Bản đầu chạy cho riêng người dùng trên VM công ty nhưng phải có hình dạng của sản phẩm đó.

## 2. Mục tiêu, không phải mục tiêu, phản mục tiêu

**Mục tiêu bản đầu (MVP)**
- G1. Chạy trọn vẹn luồng **"nhận xét đối tác → file Word"** trong một nhóm Telegram có người dùng + nhiều bot.
- G2. Giao vai/giao việc bằng lời tự nhiên trên chat; vai gắn theo nhóm, bot lấy từ bể dùng chung.
- G3. Bot tự hỏi nhau khi vướng (có giới hạn), leo thang lên người chủ nhóm khi cần.
- G4. Tôn trọng mức bảo mật theo nhóm (nội bộ / thoải mái).
- G5. Kiến trúc có ranh giới rõ cho: kênh chat, nhà cung cấp AI, nhiều người dùng, đóng gói cài đặt.

**Không phải mục tiêu bản đầu**
- Các luồng khác (slide, code, thuyết minh đề tài) – làm sau, không cần thiết kế riêng vì cơ chế là chung.
- Kênh Teams/Slack/web, giao diện quản trị web, Postgres, chạy nhiều phiên bản song song cho tải lớn.
- Kênh xem nội dung nhóm nội bộ trên điện thoại (người dùng chấp nhận là hạn chế).
- Đăng ký/tính tiền trực tuyến, đa khách hàng dùng chung một bản cài.

**Phản mục tiêu (dù chạy được vẫn coi là thất bại)**
- Tài liệu/nội dung công việc của nhóm *nội bộ* lọt lên Telegram, hoặc tài liệu công ty lọt sang Gemini.
- Các bot tự cãi nhau vô hạn, đốt hết hạn mức Claude mà không hỏi người.
- Bot tự thay đổi quyết định giải pháp đã chốt mà người chủ không biết.
- Lõi điều phối bị viết dính chặt vào Telegram hoặc vào `claude` CLI đến mức muốn bán phải viết lại.
- Phải soạn file cấu hình/mẫu trước mới dùng được (người dùng muốn giao việc thẳng trên chat).

## 3. Ràng buộc

- **Công cụ AI của bản cá nhân:** Claude Code (gói subscription – giới hạn là hạn mức theo khung giờ), Cursor trả phí (Grok qua `cursor-agent`), Google Pro (Gemini CLI đăng nhập tài khoản Google, không có API). Bản thương mại: khách tự mang tài khoản AI (API key / gói doanh nghiệp).
- **Hạ tầng bản cá nhân:** chạy trên chính máy người dùng đang làm việc (VM công ty, Windows 10, 16 core / 15 GB RAM). Hiện có: Python 3.12, Claude Code (cài qua npm trên Windows); **chưa có** `cursor-agent`, Gemini CLI, `uv`, Docker. Không có code v2.1 để kế thừa – chỉ dùng lại *ý tưởng* từ v2.1: cách tổ chức thư mục dự án, `CLAUDE.md`, `.claude/settings.json` (deny-list), mẫu tác vụ dạng Claude Code skills, audit log.
- **Telegram:** bot tạo thủ công qua @BotFather; tên bot chung cho mọi nhóm; theo hiểu biết hiện tại bot không nhận tin nhắn của bot khác (cần kiểm lại – mục 10); file bot tải về tối đa 20 MB; Telegram không mã hoá đầu-cuối với bot.
- **Phải sửa so với v2.1:** mục 9.8 (`/setjoingroups → Disable`) phải bật cho bot trong bể; allowlist mở rộng từ "chỉ user ID" sang "user ID + nhóm đã đăng ký".
- **Bảo mật kế thừa v2.1:** FR-32, NFR-03, NFR-04 (áp dụng theo mức nhóm – mục 5.7).

## 4. Phương án đã cân nhắc

| | Phương án | Đánh đổi | Kết luận |
|---|---|---|---|
| **A** | **Một dịch vụ Python duy nhất, chia khối rõ ràng bên trong** (modular monolith), đóng gói Docker Compose. Khối: lõi điều phối, bộ nối kênh, bộ nối AI, lưu trữ. | Một tiến trình: dễ cài cho khách (`docker compose up`), dễ theo dõi; chết là cả đội dừng → cần tự khởi động lại. Có đường tách khối chạy agent ra riêng khi cần tải lớn. | **[Người dùng chốt]** |
| B | Nhiều dịch vụ nhỏ ngay từ đầu (cổng kênh, lõi, worker agent) + hàng đợi Redis/NATS + CSDL. | Mở rộng và cô lập lỗi tốt; khách khó cài/vận hành, MVP phải dựng hệ thống lớn cho một luồng. | Loại |
| C | Dựng trên framework đa agent (LangGraph, CrewAI…). | Có sẵn điều phối; không chạy bằng subscription, mất năng lực làm việc với file như Claude Code, khoá sản phẩm vào framework người khác trong khi điều phối chính là giá trị riêng. | Loại |

## 5. Thiết kế

### 5.1 Tổng quan

```
             ┌───────────────────────── Dịch vụ "labour" (1 tiến trình Python) ─────────────────────────┐
 Telegram ◄──┤ Bộ nối kênh            Lõi điều phối                       Bộ nối AI                    │
 (nhiều bot) │ (TelegramAdapter) ───► - Nhóm, người chủ, vai trò  ───────► - ClaudeCodeCLI              │
             │  ▲ ChannelAdapter      - Định tuyến lượt (turn)              - CursorAgentCLI (Grok)      │
             │  │ (interface)         - Hỏi nhau / leo thang                - GeminiCLI                  │
             │  │                     - Chính sách bảo mật nhóm             - (sau) ClaudeAgentSDK/API   │
             │  └──── đăng tin bằng ◄─ - Kết thúc việc ("đạt")              ▲ AgentRuntime (interface)    │
             │        đúng bot                    │                          │ chạy trong thư mục nhóm   │
             │                          Lưu trữ (SQLite, qua lớp repository) │                           │
             └──────────────────────────────────┼─────────────────────────────┼──────────────────────────┘
                                                │                             ▼
                                     data/labour.db, audit.jsonl     workspaces/<nhóm>/  (trên ổ C: máy người dùng)
```

Nguyên tắc: **lõi điều phối không import Telegram hay tên CLI cụ thể**; mọi thứ bên ngoài đi qua interface (`ChannelAdapter`, `AgentRuntime`, repository lưu trữ). Đây là điều kiện để thêm Teams/Slack hoặc API key về sau mà không viết lại lõi.

### 5.2 Khái niệm và dữ liệu

| Khái niệm | Ý nghĩa | Trường chính |
|---|---|---|
| **User** | Một kỹ sư trong công ty. | id, tên, danh tính kênh (telegram_user_id), là_quản_trị |
| **BotIdentity** | Một bot trong bể (token BotFather). Không mang vai. | id, tên hiển thị, username, token (bí mật), kênh |
| **Group** | Một nhóm chat đã đăng ký với hệ thống. | id, chat_id kênh, **owner_user_id**, **security_level** (`noi_bo` \| `thoai_mai`), workspace_path, trạng thái |
| **Member** | Người hoặc bot trong nhóm. | group_id, user_id \| bot_id |
| **RoleAssignment** | Vai của một bot **trong một nhóm**. | group_id, bot_id, tên_vai (ngắn, làm tiền tố), **chỉ_dẫn** (nguyên văn lời dặn kỹ của người chủ + phần bổ sung), provider (`claude` \| `grok` \| `gemini`), là_reviewer, trạng thái (`cho_xac_nhan` \| `hieu_luc`) |
| **AgentSession** | Phiên hội thoại của một bot trong một nhóm (để agent nhớ ngữ cảnh). | group_id, bot_id, provider, session_id của CLI |
| **Thread** | Một chuỗi việc bắt đầu từ lời giao của người (dùng để đếm lượt hỏi nhau và kết thúc việc). | id, group_id, mở_bởi, trạng thái (`dang_lam` \| `cho_nguoi` \| `dat`), số_lượt_bot_hỏi_bot |
| **Turn** | Một lần chạy agent. | thread_id, bot_id, đầu vào, đầu ra, file thay đổi, tín hiệu, thời gian, mức dùng |
| **SavedTeam** | "Lưu đội này lại" (R5). | tên, owner, danh sách (tên_vai, chỉ_dẫn, provider) |

### 5.3 Bộ nối kênh – Telegram

Interface `ChannelAdapter` (lõi chỉ thấy cái này):
- sự kiện vào: `MessageEvent(group, sender, text, mentions[], reply_to, attachments[])`
- lệnh ra: `send(group, as_bot, text, reply_to?)`, `send_file(group, as_bot, path)`, `pin(group, as_bot, message)`

Triển khai Telegram **[Claude quyết]**:
- Thư viện **aiogram 3** (một tiến trình chạy được nhiều bot, async).
- Mọi bot trong bể chạy long polling trong cùng tiến trình (không mở cổng nghe – giữ tiêu chí v2.1 "không có cổng nghe của bridge").
- Một tin của người trong nhóm có thể đến qua nhiều bot → **khử trùng lặp theo (chat_id, message_id)**.
- Để mọi bot thấy được tin không nhắc tên (cần cho ngữ cảnh), tắt *privacy mode* của bot trong BotFather **[Để người xây kiểm tra lại]**.
- Tin bot gửi luôn có **tiền tố vai**: `[Phản biện] …` (R4).
- Bot không đọc được tin bot khác → các bot "thấy" nhau qua **nhật ký nhóm do lõi giữ**, không qua Telegram.
- Đăng ký nhóm: khi người được allowlist thêm bot vào nhóm và gõ `/start` (hoặc nói "bắt đầu"), hệ thống tạo Group với người đó làm **chủ**, hỏi mức bảo mật (nút *Nội bộ* / *Thoải mái*, mặc định **Nội bộ** **[Claude quyết]**). Nhóm chưa đăng ký hoặc người không trong allowlist → bot im lặng, ghi audit.

### 5.4 Lõi điều phối

**a) Giao vai bằng lời (R3, R4)**
- Người chủ viết tự nhiên, ví dụ: "@Bot1 em lo giải pháp, đọc nhận xét đối tác trong thư mục, đề xuất 2 phương án có sơ đồ. @Bot2 em phản biện Bot1. @Bot3 em soạn Word theo mẫu mau_phan_hoi.docx, xong thì Bot2 review".
- Lõi nhận ra đây là lời giao vai (một lượt gọi AI nhỏ để phân loại + tách ra từng `RoleAssignment`: tên_vai, chỉ_dẫn, là_reviewer, provider nếu có nhắc). **Chỉ_dẫn lưu nguyên văn phần người chủ viết cho bot đó**, không tóm lược mất ý.
- Mỗi bot đáp bằng câu nhắc lại vai ("[Giải pháp] Đã nhận vai: …. Bắt đầu nhé?"). Người chủ xác nhận ("ok") → vai `hieu_luc`, lõi ghim một tin tổng hợp các vai.
- Sửa vai giữa chừng ("@Bot2 từ giờ trả lời bằng bảng") → bổ sung vào chỉ_dẫn, nhắc lại ngắn, cập nhật tin ghim.
- Chỉ **người chủ** được giao/sửa vai và đổi mức bảo mật; người khác gõ lệnh giao vai → bot từ chối lịch sự.

**b) Định tuyến lượt**
- Tin của người **có nhắc @BotX** (hoặc reply vào tin của BotX) → lượt của BotX.
- Tin không nhắc ai → chỉ ghi vào nhật ký nhóm, không bot nào chạy **[Claude quyết – tránh tốn hạn mức]**.
- Người không phải chủ nhắc bot → bot vẫn trả lời/trao đổi, nhưng không nhận việc mới làm thay đổi vai hay kết thúc việc.

**c) Một lượt chạy agent**
Lõi dựng đầu vào cho `AgentRuntime` gồm: chỉ_dẫn vai của bot, danh sách vai các bot khác trong nhóm, mức bảo mật và quy tắc tương ứng, phần nhật ký nhóm gần đây (tin người + tin bot), file "quyết định giải pháp" nếu có, và tin nhắn cần xử lý. Agent làm việc **trong thư mục của nhóm**.

Agent kết thúc bằng một **khối tín hiệu có cấu trúc** (JSON ở cuối đầu ra, hoặc file `.labour/signal.json` trong workspace **[Để người xây chọn]**):
```json
{ "reply": "nội dung đăng ra nhóm",
  "ask": [{"bot": "Bot1", "question": "..."}],
  "escalate": {"reason": "thay đổi quyết định đã chốt", "question": "..."},
  "request_review": {"files": ["output/phan_hoi_v1.docx"], "note": "..."},
  "verdict": "dat | chua_dat | null",
  "files": ["output/phan_hoi_v1.docx"] }
```

**Thread – mở, gắn, đóng [Claude quyết]**
- **Mở:** mỗi tin của **người chủ** nhắc @bot mà *không* reply vào tin thuộc một Thread đang mở → mở Thread mới. Phần tương tác nghĩ giải pháp cũng theo quy tắc này (mỗi chủ đề người chủ khởi xướng là một Thread; reply tiếp thì vẫn cùng Thread).
- **Gắn:** tin reply vào tin thuộc Thread nào thì thuộc Thread đó. Mọi `ask`, `request_review`, lượt review/sửa sinh ra từ một lượt thì **kế thừa Thread của lượt đó** → hai việc chạy song song không lẫn bộ đếm.
- **Đặt lại bộ đếm:** chỉ khi **người chủ** viết trong Thread (tin của thành viên khác không đặt lại).
- **Đóng:** `dat` (người chủ nói đạt hoặc reviewer `verdict: dat`), hoặc người chủ nói "dừng/huỷ". Thread `cho_nguoi` không có lượt bot nào chạy cho tới khi người chủ trả lời.

**d) Hỏi nhau và leo thang (R8)**
- `ask` → lõi đăng câu hỏi ra nhóm bằng bot hỏi (để người thấy), rồi tạo lượt cho bot được hỏi với câu hỏi đó. Mỗi lần như vậy tăng `số_lượt_bot_hỏi_bot` của Thread.
- Giới hạn **3 lượt mỗi Thread** (cấu hình được). Đến giới hạn → lõi dừng chuỗi, tag người chủ: "Các bot chưa thống nhất được: … Anh/chị quyết giúp?" Thread chuyển `cho_nguoi`.
- `escalate` → tag người chủ ngay, không chờ hết lượt. Chỉ_dẫn hệ thống bắt buộc agent dùng `escalate` khi câu trả lời **làm thay đổi file quyết định giải pháp đã chốt**.
- Người trả lời trong nhóm → đếm lượt về 0, tiếp tục.

**e) Quyết định giải pháp (R7) [Claude quyết]**
- Kết thúc phần tương tác, người chủ nói "chốt" → bot đang giữ vai giải pháp (hoặc bot được chỉ định) ghi `decisions/quyet-dinh-giai-phap.md` trong workspace; đăng tóm tắt; người chủ xác nhận.
- Các lượt giao việc sau đó luôn được nạp file này. Sửa file này chỉ qua người chủ (agent được dặn không tự sửa; lõi kiểm tra file thay đổi sau mỗi lượt và báo nếu bị sửa).

**f) Kết thúc việc – "đạt" (yêu cầu mục 6.1)**
- Thread đạt khi **người chủ nói đạt** hoặc **bot có `là_reviewer` trả `verdict: "dat"`**. Lõi đăng thông báo kết thúc kèm đường dẫn file kết quả và ghim/đánh dấu.
- **Bắt đầu review [Claude quyết]:** bot soạn thảo tự coi là xong thì trả `request_review`. Lõi chuyển cho bot có `là_reviewer` trong nhóm (nếu có nhiều, ưu tiên bot được nêu trong chỉ_dẫn của bot soạn thảo); nhóm không có reviewer → tag người chủ để duyệt. Lượt review là lượt riêng có nhãn `review`, không phải `ask`, nên không tính vào giới hạn hỏi nhau.
- Reviewer trả `chua_dat` → nội dung góp ý được chuyển thành lượt `sua` cho bot soạn thảo. Vòng review/sửa có giới hạn riêng, mặc định 3 vòng, hết thì tag người chủ **[Claude quyết]**. `ask` phát sinh trong lượt review/sửa vẫn tính vào giới hạn hỏi nhau của Thread.

**g) Chạy song song**
- Mỗi bot trong một nhóm xử lý **tuần tự** (hàng đợi riêng theo (nhóm, bot)) để phiên CLI không bị chạy chồng.
- Giới hạn toàn hệ thống số lượt chạy đồng thời (mặc định 3, cấu hình được) để không vượt RAM/hạn mức.

### 5.5 Bộ nối AI

Interface `AgentRuntime.run(request) -> result`:
- vào: workspace_path, session_id (có thể rỗng), prompt hệ thống (vai + quy tắc), tin cần xử lý, mức bảo mật, giới hạn thời gian
- ra: văn bản đầu ra, khối tín hiệu đã parse, session_id mới, file đã thay đổi, thời gian, thông tin mức dùng nếu có, lỗi (hết hạn mức / quá thời gian / CLI lỗi)

Triển khai:
| Provider | Bản đầu | Cách chạy |
|---|---|---|
| `claude` | Có – **mặc định** cho mọi vai | `claude -p … --resume <session> --output-format json`, cwd = workspace nhóm; quyền theo `.claude/settings.json` của workspace (kế thừa deny-list v2.1, chế độ không hỏi – chỉ chạy những gì trong allow-list). Skill `docx` để đọc mẫu và tạo/sửa Word. |
| `grok` | Có, nếu `cursor-agent` chạy headless được trên bản đã cài | `cursor-agent` chế độ in kết quả, cwd = workspace. |
| `gemini` | Có, nhưng **chỉ trong nhóm Thoải mái** và **tắt mặc định** | Gemini CLI. Bật cho một nhóm khi người chủ nói rõ nhóm đó không chứa tài liệu công ty (NFR-03, R12) **[Claude quyết]**. |
| `claude_api` | Sau (bản thương mại) | Claude Agent SDK với API key của khách. |

Người chủ đổi provider bằng lời ("@Bot3 dùng Grok"). Lõi từ chối nếu vi phạm chính sách (ví dụ Gemini trong nhóm nội bộ).
Hết hạn mức/lỗi → bot báo trong nhóm ("[Thư ký] Claude đang hết hạn mức đến ~15:00, chuyển sang Grok không?"), không tự đổi provider **[Claude quyết]**.

### 5.6 Thư mục làm việc của nhóm (R9, R10)

```
workspaces/<group-slug>/
├── input/        # file người dùng đưa vào (đồng bộ từ máy, hoặc thả vào Telegram nếu nhóm Thoải mái)
├── output/       # file kết quả
├── decisions/    # quyet-dinh-giai-phap.md
├── templates/    # file mẫu người dùng chỉ (tuỳ chọn)
├── CLAUDE.md     # quy tắc chung + mức bảo mật (sinh tự động)
├── .claude/settings.json   # deny-list kế thừa v2.1
└── .labour/      # nhật ký, tín hiệu, không đồng bộ
```
- **Bản đầu không cần đồng bộ:** dịch vụ chạy trên chính máy người dùng, workspace nằm trên ổ đĩa của máy (mặc định `C:\Works\Labour\workspaces\`, cấu hình được) → người dùng mở trực tiếp bằng Word/Explorer [Người dùng chốt: chạy trên máy đang làm việc]. Đồng bộ sang máy khác (Syncthing/SMB/OneDrive) để **sau**, khi dịch vụ chuyển lên máy chủ riêng.
- Nhóm Thoải mái: file thả vào Telegram (≤ 20 MB) được lưu vào `input/`; file kết quả được gửi lại vào nhóm.
- Mẫu đầu ra không cố định: người dùng chỉ "theo mẫu `templates/x.docx`" hoặc mô tả định dạng; agent tự xử lý như đang làm trong Claude Code.

### 5.7 Bảo mật

| | Nội bộ (mặc định) | Thoải mái |
|---|---|---|
| Nội dung bot đăng lên Telegram | Chỉ tóm tắt / tham chiếu (mục, đường dẫn file), không trích nguyên văn tài liệu | Đầy đủ |
| Nhận file thả vào Telegram | Từ chối, nhắc dùng thư mục đồng bộ | Có (≤ 20 MB) |
| Gửi file kết quả lên Telegram | Không – chỉ "đã xong: output/…" (FR-32) | Có |
| Gemini | Cấm | Chỉ khi người chủ bật và khẳng định không có tài liệu công ty |

Thực thi hai lớp:
1. **Chỉ dẫn cho agent** (trong prompt hệ thống và `CLAUDE.md` của workspace).
2. **Lõi chặn cứng**: ở nhóm Nội bộ lõi không bao giờ gọi `send_file`, không tải file từ Telegram; tin đăng ra quá dài (ngưỡng cấu hình) hoặc chứa đoạn trùng nguyên văn file trong `input/` sẽ bị thay bằng tóm tắt + đường dẫn **[Để người xây chọn cách so trùng]**.

Kế thừa v2.1: deny-list, chế độ chỉ chạy lệnh trong allow-list, chạy bằng user không root; token bot và khoá API để trong file `.env`/secret, không commit; audit mọi lượt (`audit.jsonl`: ai, nhóm, bot, provider, file thay đổi, tín hiệu, thời gian).

### 5.8 Nhiều người dùng

- Danh sách User + quản trị viên khai báo trong file cấu hình (bản đầu); sau có giao diện quản trị.
- Chỉ User trong danh sách được tạo nhóm (trở thành chủ). Thành viên khác của nhóm phải là User trong danh sách mới được bot trả lời **[Claude quyết]**.
- Quyền chủ nhóm: giao/sửa vai, chốt quyết định giải pháp, nói "đạt", đổi mức bảo mật, bật Gemini. Quản trị viên: quản lý bể bot, danh sách User, giới hạn.
- Bản đầu chỉ có một User (người dùng) nhưng mã kiểm quyền vẫn chạy đầy đủ.

### 5.9 Lưu trữ

SQLite (`data/labour.db`) qua một lớp repository, schema theo mục 5.2; dùng thư viện ORM/migration hỗ trợ cả Postgres để chuyển sau **[Để người xây chọn, gợi ý SQLAlchemy + Alembic]**. Nhật ký nhóm giữ trong DB; giới hạn số tin đưa vào ngữ cảnh mỗi lượt.

### 5.10 Đóng gói và chạy

- Python 3.12, quản lý gói bằng `uv` **[Claude quyết]**.
- **Bản cá nhân:** chạy **trực tiếp trên Windows** (không qua WSL, không Docker) **[Claude quyết]**: Claude Code đã cài và đăng nhập trên Windows, workspace nằm trên ổ C: để người dùng mở bằng Word, tránh chậm khi WSL đọc `/mnt/c`. Khởi chạy bằng một lệnh trong terminal; tự khởi động lại bằng Task Scheduler là tuỳ chọn. Mã phải chạy được trên cả Windows và Linux (đường dẫn qua `pathlib`, không gọi lệnh riêng của một hệ điều hành) để bản sản phẩm chạy Docker/Linux.
- **Bản sản phẩm:** `Dockerfile` + `docker-compose.yml` (dịch vụ + Syncthing), cấu hình qua `.env` + `config.yaml`, dùng provider API. Bản đầu có sẵn Dockerfile chạy được với provider `claude` nhưng không bắt buộc kiểm thử đầy đủ.

### 5.11 Luồng mẫu: nhận xét đối tác → Word

1. Người dùng tạo nhóm Telegram "Phản hồi đối tác X", thêm Bot1–Bot3, gõ `/start` → chọn **Nội bộ**. Hệ thống tạo `C:\Works\Labour\workspaces\phan-hoi-doi-tac-x\`.
2. Người dùng chép file nhận xét vào `input/` của thư mục đó.
3. Giao vai bằng lời (5.4a): Bot1 giải pháp, Bot2 phản biện + reviewer, Bot3 soạn Word theo mẫu. Các bot nhắc lại vai, người dùng "ok", tin vai được ghim.
4. **Tương tác:** người dùng thảo luận với Bot1/Bot2; Bot2 hỏi Bot1 (≤ 3 lượt) – trong nhóm chỉ thấy tóm tắt vì là nhóm Nội bộ, chi tiết nằm trong file `output/`/`decisions/`.
5. Người dùng "chốt" → `decisions/quyet-dinh-giai-phap.md`.
6. **Giao việc:** "@Bot3 soạn file phản hồi theo mẫu templates/mau_phan_hoi.docx". Bot3 vướng "mục 4 dùng phương án nào?" → hỏi Bot1 → Bot1 trả lời theo file quyết định.
7. Bot3 xong → Bot2 review → `chua_dat` kèm góp ý → Bot3 sửa → Bot2 `dat`.
8. Lõi đăng "[Phản biện] Đạt. Kết quả: output/phan_hoi_v2.docx". Người dùng mở file ngay trên máy.

## 6. Kiểm thử và tiêu chí nghiệm thu MVP

- **Đơn vị:** lõi điều phối kiểm thử với `FakeChannel` + `FakeRuntime` (không gọi Telegram/AI thật): định tuyến, quyền chủ, đếm lượt/leo thang, reviewer kết thúc, chính sách bảo mật (không có `send_file` ở nhóm Nội bộ).
- **Tích hợp:** `ClaudeCodeCLI` chạy thật một lượt trong workspace tạm; Telegram chạy thật với nhóm thử.
- **Nghiệm thu:** chạy trọn luồng 5.11 với một bộ nhận xét đối tác thật (đã lọc) và người dùng (hoặc bot reviewer) nói "đạt"; audit ghi đủ; nhóm Nội bộ không có file/nội dung nguyên văn trong lịch sử Telegram.

## 7. Phạm vi bản đầu và sau

| Bản đầu (MVP) | Sau |
|---|---|
| Telegram; bể bot; giao vai bằng lời; hỏi nhau ≤3; leo thang; reviewer; quyết định giải pháp; Nội bộ/Thoải mái; workspace trên ổ đĩa máy người dùng; provider claude (grok, gemini chỉ thêm nếu cài và chạy headless được); SQLite; chạy trực tiếp trên Windows của máy người dùng; Dockerfile cơ bản; nhiều User qua file cấu hình | Đồng bộ workspace sang máy khác khi chuyển lên máy chủ; Teams/Slack; Claude Agent SDK/API; Postgres; giao diện quản trị web; "Lưu đội này lại" (R5) nếu chưa kịp; báo tiến độ giữa chừng; tách worker agent; model local (Phase 2 của v2.1) |

## 8. Phần để người xây tự quyết

Cách parse khối tín hiệu (JSON cuối đầu ra hay file); cách so trùng nguyên văn để chặn ở nhóm Nội bộ; ORM/migration; cấu trúc gói Python; định dạng log; câu chữ các tin hệ thống; số tin nhật ký đưa vào ngữ cảnh.

## 9. Câu hỏi còn mở (không chặn thiết kế)

- Số bot trong bể (gợi ý bắt đầu với 4).
- Có cần bot báo tiến độ giữa chừng (hiện chỉ báo khi xong / vướng / lỗi).

## 10. Rủi ro và việc phải kiểm tra trước khi làm

1. **Telegram bot↔bot:** xác nhận lại trong Bot API hiện hành bot có nhận tin của bot khác không. Thiết kế không phụ thuộc (lõi tự chuyển), nhưng ảnh hưởng chuyện khử trùng lặp.
2. **Privacy mode & nhóm:** xác nhận tắt privacy mode giúp bot thấy mọi tin trong nhóm.
3. **`cursor-agent` và Gemini CLI hiện chưa cài** trên máy: cài thử, kiểm chạy headless, đăng nhập, hạn mức. Không chạy được → MVP chỉ dùng `claude`.
4. **Hạn mức Claude subscription** khi nhiều bot và hỏi nhau: đo trong luồng thật; giới hạn đồng thời + giới hạn lượt là phanh chính.
5. **Điều khoản dùng subscription** cho sản phẩm bán: bản thương mại mặc định dùng API/tài khoản của khách; kiểm điều khoản trước khi bán.
