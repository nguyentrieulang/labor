# Labour – Bản 1.1b: Chỉ nhận siêu nhóm

| | |
|---|---|
| Bản | 1.1b – bản sửa lỗi của 1.1a |
| Giai đoạn | P1 – Nền móng |
| Ngày | 27/11/2026 |
| Trạng thái | 195 test tự động đạt; **chờ nghiệm thu với Telegram thật** |
| Tag git | `1.1b` |
| Bản trước | [1.1a](RELEASE_NOTES_1.1a.md) |

## Tóm tắt

Lỗi này lộ ra khi nghiệm thu bản 1.1a với Telegram thật. Labour được thử trong một **nhóm thường** (chưa lên siêu nhóm, chat_id không bắt đầu bằng `-100`), và log ghi `UNIQUE constraint failed: group_log` khi chủ nhóm gõ `/skills` và `/gemini bat`. Từ bản này Labour chỉ chạy trong **siêu nhóm (supergroup)**. Bản 1.1b thay cho 1.1a khi nghiệm thu.

## Sửa lỗi

### Nhóm thường làm sai việc chống trùng tin

Một tin trong nhóm đến cả 4 bot. Labour dựa vào số tin (`message_id`) để chỉ xử lý tin đó một lần.
- Ở **siêu nhóm**, mọi bot thấy cùng một số tin, nên cách này đúng.
- Ở **nhóm thường**, mỗi bot tự đánh số tin riêng. Cùng tin `/skills`, bot hệ thống thấy là số 8, còn một bot khác thấy là số 7, trùng với số của câu trả lời `/vai` trước đó. Kết quả là tin có thể bị bỏ nhầm (vì coi là tin cũ), bị ghi lỗi, hoặc bị xử lý nhiều lần.

Bản 1.1b xử lý như sau:

| Tình huống | Bản 1.1a | Bản 1.1b |
|---|---|---|
| `/start` trong nhóm thường | đăng ký nhóm | không đăng ký; một bot trả lời “[Hệ thống] Labour chỉ chạy trong siêu nhóm… Chat history for new members → Visible, rồi gõ lại /start” |
| `/start` trong nhóm thường, người gõ không được tạo nhóm | im lặng | im lặng |
| Mọi tin khác trong nhóm thường | xử lý (có thể sai) | bỏ qua, không ghi nhật ký tin; audit `update_rejected` lý do `basic_group` |
| `/start` trong siêu nhóm | đăng ký | đăng ký (không đổi) |

Ở nhóm thường không chống trùng được, nên chỉ **một** bot ghi audit và trả lời: bot được gọi trong `/lệnh@tên_bot`, hoặc bot đầu tiên trong `config.yaml` (`laborassistleadbot`). Nếu bot đầu tiên không có trong nhóm thì nhóm thường sẽ không nhận được câu trả lời nào.

**Chuyển nhóm thường thành siêu nhóm:** vào Cài đặt nhóm → **Chat history for new members** → chọn **Visible**. Việc cho bot làm admin cũng có thể khiến Telegram tự nâng nhóm. Sau khi chuyển, chat_id mới bắt đầu bằng `-100`.

## Chưa sửa ở bản này

- Nhánh xử lý khi nhóm thường đã đăng ký được Telegram nâng lên siêu nhóm (`migrate_to_chat_id`) vẫn giữ. Từ 1.1b chỉ siêu nhóm mới được đăng ký nên nhánh này gần như không còn dùng. Cần xem lại khi viết LLD v0.3: sau khi nâng, Telegram có thể đánh số tin lại từ đầu, trùng với số tin cũ trong nhật ký.
- Nhóm thường đã đăng ký từ bản 1.1a: mọi tin đều bị bỏ qua. Cách xử lý là xoá dữ liệu thử rồi đăng ký lại trong siêu nhóm (xem phần Nâng cấp).

## Nâng cấp từ 1.1a

Không đổi CSDL, không đổi config. Dữ liệu thử của 1.1a được tạo trong nhóm thường, nên **xoá đi** trước khi nghiệm thu lại:

```powershell
cd C:\Works\Labour
Remove-Item -Recurse -Force data, workspaces
cd code
python -m uv sync
python -m uv run pytest -q                              # 195 đạt, 2 bỏ qua
python -m uv run python -X utf8 -m labour.app
```

## Nghiệm thu (người dùng làm cùng)

1. Chuyển nhóm thử thành siêu nhóm (Chat history for new members → Visible). Kiểm `laborassistleadbot` vẫn là admin có quyền ghim.
2. Gõ `/start` → “[Hệ thống] Đã đăng ký nhóm – mức Nội bộ…” do `laborassistleadbot` gửi; thư mục nhóm có 6 thư mục con.
3. Gõ `/start` lần nữa → im lặng. `/start` trong chat riêng với bot → im lặng.
4. (cần người thứ hai) Người thứ hai gõ `/baomat thoai_mai` → “Lệnh này chỉ dành cho chủ nhóm”.
5. Chủ nhóm gõ `/vai`, `/skills`, `/status` → có trả lời; `/gemini bat` → “Lệnh này chỉ dùng ở nhóm Thoải mái”.
6. `data/audit/audit-2026-11.jsonl` có `startup` (`version: 1.1b`), `group_registered`, `update_rejected`; không dòng nào chứa nội dung tin. **Log không có `UNIQUE constraint failed`.**
7. Chủ nhóm gõ `/baomat@bot_khong_co thoai_mai` → im lặng; gõ `/baomat` → vẫn báo mức Nội bộ.
8. (cần người thứ hai) Reply tin người thứ hai, gõ `/thanhvien bo` → “… đã bỏ khỏi nhóm”; `/thanhvien them` để thêm lại.
9. (tuỳ chọn) Trong một nhóm thường khác có 4 bot, gõ `/start` → đúng **một** tin “Labour chỉ chạy trong siêu nhóm…”, nhóm không được đăng ký.

## Thay đổi kỹ thuật

| Sửa | File |
|---|---|
| Nhóm thường: bỏ qua trước bước chống trùng; một bot audit `basic_group` và trả lời `/start` | `labour/core/ingest.py` |
| Chỉ đăng ký `supergroup` | `labour/core/groups.py` |
| Mẫu `S_NEED_SUPERGROUP` | `labour/core/templates.py` |
| Số bản | `pyproject.toml` (`1.1.post2`), `labour/app/main.py` |
| Test: tin mẫu mặc định là siêu nhóm; test chuyển nhóm ghi rõ nhóm thường | `tests/fakes.py`, `tests/unit/test_ingest.py` |

## Kiểm thử

195 test tự động đạt (1.1a: 190), 2 test Telegram thật bỏ qua. Test mới:
- `/start` từ 4 bot trong nhóm thường (mỗi bot một số tin) → một tin `S_NEED_SUPERGROUP` từ bot đầu tiên, không đăng ký nhóm.
- `/start@labour_bot3` trong nhóm thường → chỉ `labour_bot3` trả lời.
- `/start` trong nhóm thường của người không được tạo nhóm → im lặng, có audit.
- Nhóm thường đã đăng ký, 4 bot cùng thấy số tin 7 → không ghi `group_log`, không lỗi, một dòng audit.
- `GroupService.register` từ chối nhóm thường.

## Tài liệu tương ứng

- LLD v0.2 mục 7.1 (đường đi một tin, chống trùng), 7.2 (đăng ký nhóm). Thay đổi đưa vào LLD v0.3.
- Kế hoạch: `docs/plans/2026-11-19-p1-nen-mong.md`, mục “Bản sửa 1.1b”.

## Xem mã

`git diff 1.1a 1.1b -- code` (repo ở `C:\Works\Labour`).
