# Labour – Bản 1.1a: Sửa lỗi sau review bản 1.1

| | |
|---|---|
| Bản | 1.1a – bản sửa lỗi của 1.1 |
| Giai đoạn | P1 – Nền móng |
| Ngày | 20/11/2026 |
| Trạng thái | 181 test tự động đạt; **chờ nghiệm thu với Telegram thật** |
| Tag git | `1.1a` |
| Bản trước | [1.1](RELEASE_NOTES_1.1.md) |

## Tóm tắt

Bản này sửa các lỗi reviewer tìm thấy ở bản 1.1, không thêm tính năng. Lỗi nặng nhất là luật hiểu ý chủ nhóm quá rộng: câu giao việc bình thường bị hiểu thành sửa vai, đổi provider hoặc chốt quyết định. Từ bản 1.2 các ý này sẽ có hành động thật, nên phải sửa trước. Bản 1.1a thay cho 1.1 khi nghiệm thu.

## Sửa lỗi

### 1. Hiểu ý chủ nhóm: lệnh phải đứng đầu câu
Gán skill, đổi provider, chốt, giao vai và sửa vai giờ chỉ được nhận khi lệnh đứng ngay sau tên bot. Lệnh nằm giữa câu thì cả câu là giao việc.

| Câu | Bản 1.1 | Bản 1.1a |
|---|---|---|
| @bot1 nhờ bot tóm tắt công việc tuần này | sửa vai | giao việc |
| @bot1 thêm phần kết luận vào báo cáo công việc | sửa vai | giao việc |
| @bot1 đổi font cho bảng nhiệm vụ | sửa vai | giao việc |
| @bot1 dùng claude viết lại đoạn 2 | đổi provider | giao việc |
| @bot1 viết lại mục chốt số liệu | chốt | giao việc |
| @bot2 thêm việc phản biện | sửa vai | sửa vai (không đổi) |
| @bot2 chuyển sang gemini | đổi provider | đổi provider (không đổi) |
| @bot1 chốt phương án B | chốt | chốt (không đổi) |

Đổi provider phải là cả câu (“@bot2 dùng gemini nhé” vẫn được). Chữ “bot” không còn được hiểu là “bớt”.

### 2. Chọn bot hệ thống khi gõ `/start` không kèm tên bot
Ở bản 1.1, cả 4 bot cùng nhận `/start`, và bot nào xử lý trước thì thành bot hệ thống. Bot đó có thể không phải admin, nên không ghim được tin.
Giờ hệ thống kiểm quyền cả 4 bot trước, rồi chọn bot đầu tiên theo thứ tự trong `config.yaml` mà là admin có quyền ghim. Nếu không bot nào đủ quyền thì chọn bot đầu tiên có trong nhóm và báo thiếu quyền. `/start@tên_bot` vẫn chọn đúng bot được gọi.

### 3. Tên bot viết hoa trong `config.yaml`
Ghi `Labour_Bot1` hay `@labour_bot1` trong config đều được đổi thành `labour_bot1` khi đọc. Ở bản 1.1, tên viết hoa làm `/start@…` bị từ chối và gửi tin bị lỗi.

### 4. Lệnh gửi cho bot ngoài bể bị bỏ qua
Mọi lệnh dạng `/lệnh@bot_khác` (bot không có trong config) đều bị bỏ qua và ghi audit `update_rejected` với lý do `foreign_bot`. Ở bản 1.1, chỉ `/start` được kiểm; ví dụ `/baomat@bot_khac thoai_mai` vẫn đổi được mức bảo mật.

### 5. Gửi tin dài và gửi tin lỗi
- Tin dài hơn 4 096 ký tự giờ **thật sự** được chia theo đoạn. Ở bản 1.1 hàm chia có sẵn nhưng chưa bật, nên tin `/vai`, `/skills` quá dài sẽ bị Telegram từ chối.
- Các phần của một tin dài được gửi liền nhau; tin khác trong cùng nhóm không chen vào giữa.
- Nếu một tin gửi lỗi (mạng, Telegram từ chối…), các tin sau vẫn được gửi; tin lỗi được ghi audit `send_failed` (chỉ tên lỗi, không nội dung).

### 6. `/thanhvien bo`
Lệnh bỏ người khỏi nhóm giờ là `/thanhvien bo`, để không nhầm “bot” với robot. Gõ `/thanhvien bot` như cũ vẫn được.

## Sửa release note bản 1.1

Release note 1.1 có bốn chỗ ghi sai so với mã. Các chỗ này đã được sửa trong file [RELEASE_NOTES_1.1.md](RELEASE_NOTES_1.1.md):
- Tin dài hơn 4 096 ký tự: ở 1.1 chưa chia (bật ở 1.1a).
- “Khi mơ hồ, hệ thống không đoán”: ở 1.1 không đúng với câu giao việc thông thường (sửa ở 1.1a, mục 1 trên).
- `/gemini` ở nhóm Nội bộ trả lời “Lệnh này chỉ dùng ở nhóm Thoải mái”; câu “Provider chưa hỗ trợ ở bản này” chỉ có ở nhóm Thoải mái.
- Cách xem mã: dùng `git ls-tree -r --name-only 1.1` (không phải `git show --stat 1.1`, lệnh đó chỉ hiện commit cuối).

## Không sửa ở bản này

- Bot chưa được thêm vào nhóm không bị báo thiếu quyền. Đây là đúng thiết kế: LLD 7.2 chỉ kiểm quyền bot có mặt trong nhóm. Khi bot được thêm vào nhóm sau, chủ nhóm có thể kiểm lại bằng tay; lệnh kiểm lại quyền sẽ xét ở bản sau.
- Cổng chặn tin ở nhóm Nội bộ chỉ kiểm mã mẫu, không kiểm nội dung. Mẫu có phần tự do (`S_ROLES`, `S_SKILLS`) hiện chỉ chứa tên vai, skill và lời giao của chủ nhóm. Cần xem lại mỗi khi thêm mẫu mới.
- Chưa có lệnh đổi bot hệ thống sau khi đăng ký (đưa vào LLD v0.3).

## Nâng cấp từ 1.1

Không đổi CSDL, không đổi config. Lấy mã mới rồi chạy lại:

```powershell
cd C:\Works\Labour\code
python -m uv sync
python -m uv run pytest -q                              # 181 đạt, 2 bỏ qua
python -m uv run python -X utf8 -m labour.app
```

## Nghiệm thu (người dùng làm cùng)

Giống bản 1.1, sửa bước 2 và thêm bước 7, 8:

1. Tạo 4 bot qua BotFather, tắt privacy mode; lập nhóm thử, thêm 4 bot, cho `labour_bot1` làm admin có quyền ghim.
2. Gõ `/start` (không kèm tên bot) → tin “[Hệ thống] Đã đăng ký nhóm – mức Nội bộ…” do **`labour_bot1`** gửi; thư mục nhóm có 6 thư mục con.
3. Gõ `/start` lần nữa → im lặng. Gõ `/start` trong chat riêng với bot → im lặng.
4. Người thứ hai (có trong cấu hình, không phải chủ) gõ `/baomat thoai_mai` → “Lệnh này chỉ dành cho chủ nhóm”.
5. Chủ nhóm gõ `/vai`, `/skills`, `/status` → có trả lời; `/gemini bat` → “Lệnh này chỉ dùng ở nhóm Thoải mái”.
6. Mở `data/audit/audit-2026-11.jsonl` → có `startup` (`version: 1.1a`), `group_registered`, `update_rejected`; không dòng nào chứa nội dung tin.
7. Chủ nhóm gõ `/baomat@bot_khong_co thoai_mai` → im lặng; gõ `/baomat` → vẫn báo mức Nội bộ (audit có `foreign_bot`).
8. Chủ nhóm reply vào tin của người thứ hai, gõ `/thanhvien bo` → “… đã bỏ khỏi nhóm”; gõ `/thanhvien them` để thêm lại.

## Thay đổi kỹ thuật

| Sửa | File |
|---|---|
| Luật hiểu ý (luật 6–10 đứng đầu câu) | `labour/core/intents.py` |
| Chọn bot hệ thống, kiểm quyền trước transaction | `labour/core/groups.py` |
| Username bot chữ thường | `labour/app/config.py` |
| Bỏ qua lệnh cho bot ngoài bể; tin lỗi không bỏ tin sau | `labour/core/ingest.py` |
| Luôn chia tin dài; khoá cả tin | `labour/core/outbox.py` |
| `/thanhvien bo` | `labour/core/commands.py` |
| Số bản | `pyproject.toml` (`1.1.post1`), `labour/app/main.py` |

Trong `pyproject.toml`, bản 1.1a ghi là `1.1.post1`, vì theo chuẩn số bản của Python, `1.1a` nghĩa là bản thử **trước** 1.1.

## Kiểm thử

181 test tự động đạt (bản 1.1: 163), 2 test Telegram thật bỏ qua vì chưa có token. Test mới:
- 10 câu nhận diện ý, trong đó có đủ 5 câu reviewer nêu (phải ra giao việc).
- `/start` không kèm tên bot chọn bot admin đầu tiên, không phải bot nhận tin; không có bot admin thì chọn bot đầu tiên trong nhóm và báo thiếu quyền.
- Tên bot viết hoa hoặc có `@` trong config; trùng tên khác hoa/thường bị báo lỗi.
- `/baomat@bot_khac` không đổi mức bảo mật; `/status@labour_bot3` vẫn được trả lời.
- Tin dài được chia mà không có tin khác chen vào giữa; phần đầu reply đúng tin gốc.
- Một tin gửi lỗi, tin sau vẫn gửi và có audit `send_failed`.
- `/thanhvien bo` và `/thanhvien bot`.

## Tài liệu tương ứng

- Review bản 1.1 (mục A1–A3, B1, B2, B4, B5, B6).
- LLD v0.2 mục 3.1 (config), 7.2 (đăng ký nhóm), 7.3 (luật hiểu ý), 11 (lệnh), 12 (Outbox).
- Kế hoạch: `docs/plans/2026-11-19-p1-nen-mong.md`, mục “Bản sửa 1.1a” ở cuối file (các lệch sẽ đưa vào LLD v0.3).

## Xem mã

`git diff 1.1 1.1a` – toàn bộ thay đổi so với bản 1.1.
