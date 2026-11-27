# Labour – Bản 1.1c: Thêm lại thành viên đã bỏ

| | |
|---|---|
| Bản | 1.1c – bản sửa lỗi của 1.1b |
| Giai đoạn | P1 – Nền móng |
| Ngày | 27/11/2026 |
| Trạng thái | 202 test tự động đạt; **nghiệm thu Telegram thật đạt** (27/11/2026, bước 2–8 trên siêu nhóm) |
| Tag git | `1.1c` |
| Bản trước | [1.1b](RELEASE_NOTES_1.1b.md) |

## Tóm tắt

Lỗi lộ ra ở bước 8 khi nghiệm thu bản 1.1b với Telegram thật. Chủ nhóm bỏ được người thứ hai khỏi nhóm, nhưng khi reply vào tin người đó gửi **sau khi bị bỏ** và gõ `/thanhvien them`, bot trả lời “Thành viên ?: reply vào tin của người đó…” mà không thêm lại.

## Sửa lỗi

### `/thanhvien them` không thêm lại được người đã bỏ

Nguyên nhân: bản 1.1b tìm người cần thêm bằng cách lấy số tin được reply rồi tra trong nhật ký tin (`group_log`). Tin của người đã bị bỏ thì bị bỏ qua từ đầu và **không được ghi vào nhật ký**, nên tra không ra người viết.

Trong khi đó, tin reply mà Telegram gửi về đã có sẵn người viết tin gốc. Ví dụ bản tin thật lúc nghiệm thu:

```
"text": "/thanhvien them",
"reply_to_message": {
  "message_id": 30,
  "from": { "id": 5943471923, "is_bot": false, ... },
  "text": "Test"
}
```

Bản 1.1c lấy thẳng `reply_to_message.from.id` từ Telegram:

| Tình huống | Bản 1.1b | Bản 1.1c |
|---|---|---|
| Reply tin gửi **trước** khi bỏ, `/thanhvien them` | thêm lại | thêm lại (không đổi) |
| Reply tin gửi **sau** khi bỏ, `/thanhvien them` | “Thành viên ?” | thêm lại |
| Reply tin của bot | “Thành viên ?” | “Thành viên ?” (không đổi) |
| Reply tin của người không có trong `config.yaml` | “Thành viên ?” | “Thành viên ?” (không đổi) |
| Reply tin của chủ nhóm, `/thanhvien bo` | “chủ nhóm – không đổi” | không đổi |

Không lưu thêm gì: tin của người đã bỏ vẫn không được ghi vào nhật ký, chỉ có audit `update_rejected` / `removed_member` như cũ. Người viết tin gốc do máy chủ Telegram gửi, nên không giả mạo được.

### Tên trong câu trả lời của `/thanhvien`

Bot gọi người được thêm hoặc bỏ bằng **username Telegram** lấy từ tin được reply (`reply_to_message.from.username`), ví dụ “[Hệ thống] Thành viên @ntlang: thành viên”. Người không đặt username thì dùng tên trong `config.yaml` (trường `name`).

Username chỉ gồm chữ không dấu, số và `_` (Telegram kiểm), nên an toàn khi đưa vào mẫu tin ở nhóm Nội bộ. Tên hiển thị Telegram (`first_name`, `last_name`) thì người dùng đặt tuỳ ý, nên không dùng.

## Lưu ý

- “Bỏ khỏi nhóm” trong Labour chỉ làm bot không nhận tin của người đó. Người đó **vẫn ở trong nhóm Telegram**. Muốn chặn hẳn thì xoá họ khỏi nhóm trên Telegram.
- Mỗi tin bị từ chối vẫn ghi một dòng audit. Chống spam audit (gộp theo người theo phút, xoay vòng file) đã được đưa vào kế hoạch P5.

## Nâng cấp từ 1.1b

Không đổi CSDL, không đổi config, không cần xoá dữ liệu. Dừng bot, lấy mã mới, rồi chạy:

```powershell
cd C:\Works\Labour\code
python -m uv sync
python -m uv run pytest -q                              # 202 đạt, 2 bỏ qua
python -m uv run python -X utf8 -m labour.app
```

## Nghiệm thu bước 8 (người dùng làm cùng)

Người thứ hai (ID 5943471923) đang ở trạng thái đã bỏ.

1. Người thứ hai gửi một tin bất kỳ → không bot nào trả lời (đã bỏ).
2. Chủ nhóm reply vào tin vừa rồi, gõ `/thanhvien them` → “Thành viên @ntlang: thành viên”.
3. Người thứ hai gõ `/vai` → có trả lời (đã là thành viên).
4. Chủ nhóm reply một tin của người thứ hai, gõ `/thanhvien bo` → “… đã bỏ khỏi nhóm”; người thứ hai gõ `/vai` → im lặng.
5. Reply lại tin bất kỳ của người thứ hai, `/thanhvien them` → thêm lại được.
6. Audit có `startup` (`version: 1.1c`), `member_added`, `member_removed`, `update_rejected` / `removed_member`.

## Thay đổi kỹ thuật

| Sửa | File |
|---|---|
| `MessageEvent.reply_to_user_id`, `reply_to_username` | `labour/ports/models.py` |
| Lấy `reply_to_message.from.id` và `.username` (bỏ qua khi tin gốc của bot) | `labour/adapters/telegram/convert.py` |
| `/thanhvien` tìm người qua `users.by_tg(reply_to_user_id)`, không tra `group_log`; gọi bằng `@username` | `labour/core/commands.py` |
| Số bản | `pyproject.toml` (`1.1.post3`), `labour/app/main.py` |

## Kiểm thử

202 test tự động đạt (1.1b: 195), 2 test Telegram thật bỏ qua. Test mới hoặc sửa:
- Chuyển tin: lấy được ID và username người viết tin gốc; tin gốc của bot thì không có.
- `/thanhvien` gọi người bằng `@username`; không có username thì dùng tên trong config.
- `/thanhvien them` reply tin gửi sau khi bị bỏ (không có trong `group_log`) → thêm lại được.
- Reply tin của bot hoặc của người không có trong config → hiện hướng dẫn.
- `/thanhvien bo` / `bot` / `them` và không bỏ được chủ nhóm: dùng ID người viết tin gốc thay vì `group_log`.

## Tài liệu tương ứng

- LLD v0.2 mục 11 (lệnh). Thay đổi đưa vào LLD v0.3.
- Kế hoạch: `docs/plans/2026-11-19-p1-nen-mong.md`, mục “Bản sửa 1.1c”.

## Xem mã

`git diff 1.1b 1.1c -- code` (repo ở `C:\Works\Labour`).
