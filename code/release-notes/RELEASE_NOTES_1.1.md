# Labour – Bản 1.1: Nền móng (giai đoạn P1)

> **Đã có bản sửa lỗi [1.1a](RELEASE_NOTES_1.1a.md); nghiệm thu bằng bản 1.1a.** Các chỗ ghi sai trong file này đã được sửa, đánh dấu “(sửa sau review)”.

| | |
|---|---|
| Bản | 1.1 – bản phát hành đầu tiên |
| Giai đoạn | P1 – Nền móng |
| Ngày | 20/11/2026 |
| Trạng thái | Xong mã, 163 test tự động đạt; **chờ nghiệm thu với Telegram thật** |
| Tag git | `1.1` |
| Bản trước | — (bản đầu) |

## Tóm tắt

Bản này dựng nền cho cả hệ thống. Labour đã nhận tin từ một bể 4 bot Telegram, đăng ký nhóm làm việc, hiểu tin của chủ nhóm và trả lời các lệnh quản lý. Bản này **chưa gọi AI**: chưa có agent soạn bài, chưa có hàng đợi việc. Phần đó thuộc các bản sau.

## Tính năng

### 1. Đăng ký nhóm làm việc
- Người được phép gõ `/start` (hoặc `/start@tên_bot`) trong nhóm Telegram. Người đó thành chủ nhóm, bot nhận lệnh thành bot hệ thống của nhóm.
- Nhóm mới luôn ở mức bảo mật **Nội bộ**.
- Tạo thư mục làm việc của nhóm (`input`, `templates`, `output`, `review`, `thao-luan`, `decisions`) và file chỉ dẫn nhóm.
- Kiểm quyền từng bot trong nhóm và báo rõ bot nào thiếu quyền (chưa là admin, chưa tắt privacy mode).
- Im lặng khi: người gõ không có quyền, gõ trong chat riêng, nhóm đã đăng ký rồi, hoặc lệnh gửi cho bot ngoài bể.

### 2. Nhận tin và kiểm soát truy cập
- Một tin mà cả 4 bot cùng thấy chỉ được xử lý một lần.
- Người lạ, nhóm chưa đăng ký, người đã bị bỏ khỏi nhóm: bot im lặng, chỉ ghi nhật ký audit.
- Người có trong danh sách cấu hình, lần đầu nhắn vào nhóm: tự thành thành viên.
- **Chỉ chủ nhóm giao được việc cho bot.** Tin của thành viên chỉ được ghi nhật ký.
- Tin bị sửa không được xử lý lại. Nhóm nâng cấp thành supergroup vẫn được giữ.

### 3. Hiểu ý chủ nhóm (không dùng AI)

| Ý | Ví dụ |
|---|---|
| Xác nhận | reply “ok”, “đồng ý” vào tin chờ xác nhận |
| Đạt / mở lại | reply “Đạt!” vào tin của việc; reply “không đạt…” vào tin ĐẠT |
| Chạy lại / dừng | reply “chạy lại” vào tin lỗi; “dừng”, “huỷ” trong một việc |
| Gán skill / đổi provider | “@bot2 dùng thêm skill X”; “@bot2 chuyển sang gemini” |
| Chốt quyết định | “@bot1 chốt phương án B” |
| Giao vai / sửa vai | “@bot1 giao vai: phân tích yêu cầu”; “@bot2 thêm việc phản biện” |
| Giao việc | “@bot1 soạn bảng phản hồi…”, hoặc reply vào tin của bot |

Gõ có dấu hay không dấu đều được. Các từ mà bỏ dấu sẽ đổi nghĩa thì được phân biệt (đúng / dừng / dùng, bỏ / bộ, đổi / đối, đạt / đặt, vai / vài). (sửa sau review) Luật ở bản này còn quá rộng: câu giao việc có chữ “việc”, “dùng claude”, “chốt” ở giữa câu bị hiểu nhầm thành sửa vai, đổi provider, chốt; đã sửa ở 1.1a. Ở bản này hệ thống mới nhận ra ý và ghi lại; hành động tương ứng có từ bản 1.2.

### 4. Lệnh trên chat

| Lệnh | Ai dùng | Kết quả |
|---|---|---|
| `/baomat noi_bo` · `/baomat thoai_mai` | chủ nhóm | đổi mức bảo mật |
| `/gemini bat` · `/gemini tat` | chủ nhóm | bản này luôn từ chối: nhóm Nội bộ “Lệnh này chỉ dùng ở nhóm Thoải mái”, nhóm Thoải mái “Provider chưa hỗ trợ ở bản này” (sửa sau review) |
| `/thanhvien them` · `/thanhvien bot` | chủ nhóm | reply vào tin của một người để thêm hoặc bỏ người đó |
| `/vai [@bot] [tatca]` | mọi thành viên | xem vai các bot; chỉ hiện lời chủ nhóm, không hiện chỉ dẫn do AI viết |
| `/skills` | mọi thành viên | skill dùng được và skill gắn với vai |
| `/status` | mọi thành viên | số việc mở, lượt chờ / đang chạy, chi phí hôm nay |

Thành viên thường gõ lệnh của chủ nhóm sẽ nhận “Lệnh này chỉ dành cho chủ nhóm”, và không có gì thay đổi.

### 5. Bảo mật nhóm Nội bộ
- Ở nhóm Nội bộ, bot chỉ được gửi tin dựng từ **mẫu cố định** (T01–T15 và tin hệ thống). Mọi tin khác bị chặn ngay trước khi gửi.
- Tên file hiện trên chat được chuẩn hoá về ký tự an toàn, tối đa 60 ký tự.
- File gửi vào nhóm Nội bộ bị từ chối.
- Nhật ký audit (`data/audit/audit-YYYY-MM.jsonl`) không bao giờ chứa nội dung tin hay tài liệu.

### 6. Gửi tin ổn định
- Mỗi nhóm chat: hai tin cách nhau ít nhất 3 giây. Khi Telegram báo gửi quá nhanh thì chờ rồi gửi lại.
- (sửa sau review) Có hàm chia tin dài hơn 4 096 ký tự nhưng **chưa bật**; bật ở 1.1a.

## Cài đặt và chạy

```powershell
cd C:\Works\Labour\code
python -m uv sync
python -m uv run pytest -q                              # 163 đạt, 2 bỏ qua
copy .env.example .env                                  # điền BOT1_TOKEN … BOT4_TOKEN
copy config.example.yaml config.yaml                    # điền tg_user_id thật
python -m uv run python -X utf8 -m labour.app
```

Cấu hình thiếu hoặc sai thì dịch vụ báo rõ rồi dừng, ví dụ `thiếu token của @labour_bot1: biến BOT1_TOKEN`.

## Nghiệm thu (người dùng làm cùng)

1. Tạo 4 bot qua BotFather, tắt privacy mode; lập nhóm thử, thêm 4 bot, cho `labour_bot1` làm admin.
2. Gõ `/start@labour_bot1` → nhận tin “[Hệ thống] Đã đăng ký nhóm – mức Nội bộ…”; thư mục nhóm có 6 thư mục con.
3. Gõ `/start` lần nữa → im lặng. Gõ `/start` trong chat riêng với bot → im lặng.
4. Người thứ hai (có trong cấu hình, không phải chủ) gõ `/baomat thoai_mai` → “Lệnh này chỉ dành cho chủ nhóm”.
5. Chủ nhóm gõ `/vai`, `/skills`, `/status` → có trả lời; `/gemini bat` → bị từ chối.
6. Mở `data/audit/audit-2026-11.jsonl` → có `startup`, `group_registered`, `update_rejected`; không dòng nào chứa nội dung tin.

## Thay đổi kỹ thuật

| Phần | File chính |
|---|---|
| Cấu hình | `labour/app/config.py`, `config.example.yaml`, `.env.example` |
| CSDL (16 bảng, migration) | `labour/adapters/storage/models.py`, `db.py`, `migrations/` |
| Lưu trữ, audit | `labour/adapters/storage/repos.py`, `audit.py` |
| Interface cho lõi | `labour/ports/` |
| Chuẩn hoá chữ, mẫu tin | `labour/core/text.py`, `templates.py` |
| Nhận diện ý | `labour/core/intents.py` |
| Gửi tin | `labour/core/outbox.py` |
| Đăng ký nhóm | `labour/core/groups.py` |
| Lệnh chat | `labour/core/commands.py` |
| Đường đi của tin | `labour/core/ingest.py` |
| Telegram | `labour/adapters/telegram/convert.py`, `channel.py` |
| Khởi động | `labour/app/wiring.py`, `main.py` |

Python 3.12, uv, aiogram 3, SQLAlchemy 2 + Alembic, SQLite (WAL). Phần lõi (`labour/core`) không phụ thuộc Telegram hay CSDL cụ thể; có test kiểm quy tắc này.

## Tài liệu tương ứng

- LLD v0.2 mục 2, 3, 4, 5, 7.1–7.3, 8.1, 11, 12, 15.
- HLD v0.6: F-01..F-05, F-21, F-26, F-28; AD-09 (mặc định Nội bộ), AD-14 (Nội bộ không có nguyên văn), AD-21 (Grok không ở Nội bộ), AD-23 (chỉ chủ nhóm tạo việc).
- Kế hoạch: `docs/plans/2026-11-19-p1-nen-mong.md` (đã sửa trước khi viết mã: luật xác nhận khớp cả câu, luật vai khớp chữ có dấu, Outbox chặn tin Nội bộ không mẫu).

## Kiểm thử

163 test tự động đạt. 2 test với Telegram thật bỏ qua vì chưa có token; chúng chạy khi có biến `TG_TEST_TOKEN_1`, `TG_TEST_TOKEN_2`, `TG_TEST_CHAT`.
Các ca quan trọng: một tin qua 4 bot đồng thời chỉ xử lý một lần; 51 câu mẫu nhận diện ý có dấu và không dấu; thành viên không chạy được lệnh của chủ nhóm; `/vai` không lộ chỉ dẫn; nhóm Nội bộ chặn tin không mẫu; ràng buộc “một chủ mỗi nhóm”, “một vai hiệu lực mỗi bot” được kiểm trên CSDL dựng bằng migration.

## Khác với thiết kế (sẽ cập nhật vào LLD v0.3)

- Dùng SQLAlchemy đồng bộ thay cho aiosqlite.
- Thêm cột `bots.can_read_all`, `group_log.template_code`; thêm vai thành viên `da_bo` (đã bị bỏ).
- Thêm mã cho tin hệ thống (`S_REGISTERED`, `S_LEVEL`, `S_ROLES`, `S_STATUS`…) để kiểm được mọi tin ở nhóm Nội bộ.
- Reply vào tin hệ thống không thuộc việc nào được coi là “không có ý”.

## Giới hạn của bản này

- Chưa gọi AI; các ý của chủ nhóm mới được nhận ra và ghi lại, chưa có hành động (bản 1.2).
- Nhóm Thoải mái nhận file: mới ghi audit, chưa lưu file.
- `/skill` trong chat riêng trả lời “chưa có ở bản này”.

## Cần người dùng chuẩn bị

- Cho nghiệm thu bản này: 4 bot đã tắt privacy mode, `.env`, `config.yaml`.
- Trước các bản có AI: kiểm điều khoản Anthropic về dùng subscription cho dịch vụ tự viết; một bộ nhận xét đối tác và mẫu Word thật đã lọc.

## Xem mã

Bản đầu tiên, toàn bộ mã trong repo: `git ls-tree -r --name-only 1.1` (danh sách file) hoặc `git log --stat 1.1` (từng commit). (sửa sau review)
