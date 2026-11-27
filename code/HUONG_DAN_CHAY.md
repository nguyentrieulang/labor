# Hướng dẫn chạy Labour trên máy này

Áp dụng cho bản 1.1c, máy Windows tại `C:\Works\Labour`. Labour viết bằng Python nên không cần dịch (build): cài thư viện xong là chạy thẳng mã nguồn.

## 1. Trạng thái máy hiện tại

Trên máy này mọi thứ đã sẵn sàng, không cần cài thêm gì:

- Python 3.12 và uv đã được cài. Thư viện đã nằm trong `code\.venv`.
- `code\.env` đã có token của 4 bot (từ `BOT1_TOKEN` đến `BOT4_TOKEN`).
- `code\config.yaml` đã khai báo:
  - 4 bot: `laborassistleadbot` (bot hệ thống, admin nhóm), `laborreviewleadbot`, `labordevleadBot`, `laboranalysisbot`.
  - Chủ nhóm: Telegram ID 1626411683.
  - Thư mục dữ liệu `C:/Works/Labour/data` và thư mục nhóm `C:/Works/Labour/workspaces`.
- Nhóm thử là một siêu nhóm (supergroup). Privacy mode của cả 4 bot đã tắt, và `laborassistleadbot` là admin có quyền ghim tin.

`.env` và `config.yaml` chứa thông tin riêng nên không đưa lên git.

## 2. Chạy bot

Mở PowerShell rồi gõ:

```powershell
cd C:\Works\Labour\code
python -m uv run python -X utf8 -m labour.app
```

- Bot đã sẵn sàng khi log hiện dòng `Labour đã chạy với 4 bot` và bốn dòng `Run polling for bot @...`.
- Bot chạy liên tục trong cửa sổ đó. Đóng cửa sổ hoặc tắt máy thì bot dừng.
- Phải đứng trong thư mục `code` khi chạy, vì chương trình đọc `config.yaml` và `.env` ở thư mục hiện tại.
- Bắt buộc có `-X utf8`, nếu không tiếng Việt trong log có thể bị lỗi.

## 3. Dừng bot

Bấm `Ctrl+C` trong cửa sổ đang chạy bot. Audit sẽ ghi một dòng `shutdown`.

## 4. Chỉ chạy một bản tại một thời điểm

Mỗi token bot chỉ cho một chương trình nhận tin cùng lúc. Nếu hai bản cùng chạy (hai cửa sổ, hoặc một bản do Claude chạy ngầm), log sẽ báo lỗi `Conflict: terminated by other getUpdates request` và tin bị chia cho hai bản.

Trước khi chạy, kiểm tra xem đã có bản nào đang chạy chưa:

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object CommandLine -like "*labour.app*" | Select-Object ProcessId, CommandLine
```

- Có kết quả: đã có bản đang chạy. Một bản thường hiện 3 dòng (uv, `.venv\Scripts\python.exe` và python thật). Dừng bản đó trước, bằng `Ctrl+C` ở cửa sổ của nó, hoặc dừng cả 3 tiến trình bằng `Stop-Process -Id <ProcessId>`, rồi chạy lại lệnh kiểm tra để chắc không còn dòng nào.
- Không có kết quả: có thể chạy.

## 5. Chạy test (nên làm sau mỗi lần lấy mã mới)

```powershell
cd C:\Works\Labour\code
python -m uv run pytest -q
```

Bản 1.1c đúng khi kết quả là `202 passed, 2 skipped`. Hai test bị bỏ qua là test với Telegram thật.

## 6. Lấy mã mới từ GitHub

```powershell
cd C:\Works\Labour
git pull
cd code
python -m uv sync
python -m uv run pytest -q
```

- `uv sync` cài đúng thư viện ghi trong `uv.lock`. Khi không có gì thay đổi, lệnh chạy rất nhanh.
- Đọc release note của bản mới trong `code\release-notes\` trước khi chạy: có bản yêu cầu xoá dữ liệu hoặc sửa config.

## 7. Dữ liệu và log

| Nội dung | Nơi lưu |
|---|---|
| CSDL (nhóm, thành viên, nhật ký tin) | `C:\Works\Labour\data\labour.db` |
| Audit (sự kiện, không chứa nội dung tin) | `C:\Works\Labour\data\audit\audit-YYYY-MM.jsonl` |
| Chỉ dẫn của từng nhóm | `C:\Works\Labour\data\groups\<số nhóm>\chi-dan.md` |
| Thư mục làm việc của nhóm | `C:\Works\Labour\workspaces\<tên nhóm>-<số nhóm>\` (6 thư mục con: input, templates, output, review, thao-luan, decisions) |
| Log chạy | in ra cửa sổ đang chạy bot, không ghi file |

Muốn giữ log ra file thì chạy:

```powershell
python -m uv run python -X utf8 -m labour.app *> C:\Works\Labour\data\labour.log
```

## 8. Làm lại từ đầu (xoá dữ liệu thử)

Dừng bot trước, rồi chạy:

```powershell
cd C:\Works\Labour
Remove-Item -Recurse -Force data, workspaces
```

Lần chạy sau, CSDL sẽ được tạo lại và nhóm phải gõ `/start` để đăng ký lại.

## 9. Dùng trên Telegram

- Labour chỉ chạy trong **siêu nhóm**. Để chuyển nhóm thường thành siêu nhóm: Cài đặt nhóm, mục Chat history for new members, chọn Visible.
- Đăng ký nhóm: chủ nhóm gõ `/start`.
- Các lệnh có ở bản 1.1c: `/vai`, `/skills`, `/status`, `/baomat`, `/baomat thoai_mai`, `/gemini bat`, `/thanhvien bo`, `/thanhvien them`.
- Bản 1.1c chưa gọi AI. Câu giao việc được nhận và phân loại, nhưng chưa có bot nào làm việc thật (đó là phần của P2 và P3).

## 10. Lỗi thường gặp

| Hiện tượng | Nguyên nhân và cách sửa |
|---|---|
| `Cấu hình lỗi: thiếu token của @...` | `.env` thiếu token hoặc chạy sai thư mục. Hãy `cd C:\Works\Labour\code` rồi chạy lại. |
| `Cấu hình lỗi: không đọc được ...config.yaml` | Chạy sai thư mục, hoặc chưa có `config.yaml` (chép từ `config.example.yaml`). |
| `Conflict: terminated by other getUpdates request` | Đang có bản khác chạy. Xem mục 4. |
| Cảnh báo `chưa tắt privacy mode` | Vào BotFather, `/setprivacy`, chọn Disable cho bot đó. Sau đó xoá bot khỏi nhóm rồi thêm lại. |
| Gõ `/start` thì nhận “Labour chỉ chạy trong siêu nhóm” | Nhóm đang là nhóm thường. Chuyển thành siêu nhóm (mục 9) rồi gõ lại `/start`. |
| Gõ lệnh mà không bot nào trả lời | Có thể bot chưa chạy, người gõ không có trong `config.yaml`, hoặc nhóm chưa `/start`. Xem lý do ở dòng `update_rejected` cuối cùng trong file audit. |
| Báo “Thiếu quyền” sau `/start` | Bot hệ thống chưa là admin hoặc chưa có quyền ghim tin. Cấp quyền trong cài đặt nhóm. |
| Chữ tiếng Việt trong log bị lỗi | Thiếu `-X utf8` trong lệnh chạy. |

## 11. Trên máy khác

Cài Python 3.12, chạy `python -m pip install uv`, rồi `git clone https://github.com/nguyentrieulang/labor.git`. Trong thư mục `code`: chép `.env.example` thành `.env` và điền token, chép `config.example.yaml` thành `config.yaml` và sửa tên bot, Telegram ID, thư mục dữ liệu. Sau đó chạy `python -m uv sync` và làm tiếp từ mục 2.
