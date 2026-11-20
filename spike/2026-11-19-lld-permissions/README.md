# Spike 3 – Kiểm đúng luật quyền và cờ CLI của LLD v0.1 (mục 6.1, 6.2)

Ngày: 19/11/2026 · claude.exe 2.1.328 · model haiku · tổng chi phí ≈ 0,04 USD · chạy: `python -X utf8 run_check.py`

Lý do: review LLD v0.1 chỉ ra luật quyền mục 6.2 (chỉ `Edit(./output/**)`, `Edit(./review/**)`, không có `Write(...)`)
khác cấu hình đã spike (spike 1 cho `Edit(./**)` rồi cấm decisions/). Spike này chạy **đúng** file settings.json của LLD,
prompt qua **stdin**, có `--append-system-prompt-file`, `--permission-prompts none`, `--json-schema`, `--restricted`,
`--tools Read,Write,Edit,Glob,Grep`, cwd = workspace. Kết luận lấy từ hệ thống file.

| Ca | Mong đợi | Kết quả |
|---|---|---|
| Write file mới review/t1-v1.md | ghi được | ĐẠT |
| Write file mới output/v2.md | ghi được | ĐẠT |
| Edit output/v1.md | sửa được | ĐẠT |
| Write input/x.md | bị chặn | ĐẠT (denial Write) |
| Edit input/brief.md | bị chặn | ĐẠT (denial Edit) |
| Write templates/x.md | bị chặn | ĐẠT |
| Write đè decisions/quyet-dinh-giai-phap.md | bị chặn | ĐẠT |
| Write thao-luan/x.md | bị chặn | ĐẠT |
| Write ghi-chu.md ở gốc workspace (không có allow) | bị chặn | ĐẠT |
| system.md qua --append-system-prompt-file; prompt qua stdin | reply theo chỉ dẫn system.md | ĐẠT |

Kết luận:
- Luật `Edit(<thư mục>/**)` ở mục allow cho phép cả **Write** file mới trong thư mục đó; không cần `Write(...)`.
- Ở chế độ dontAsk, đường dẫn không có allow bị từ chối (ca ghi gốc workspace) – deny chỉ là lớp thứ hai.
- `-p` không kèm prompt trên dòng lệnh đọc prompt từ stdin; `--append-system-prompt-file` và `--permission-prompts none` hoạt động trên 2.1.328.
- Tên biến `DISABLE_AUTOUPDATER` có trong claude.exe 2.1.328 (tìm trong binary); hành vi tắt cập nhật vẫn cần quan sát khi cài.

Kết quả thô: `results.jsonl`. Bộ này chuyển vào `tests/security` (LLD 14.3 #6) và chạy lại mỗi lần đổi pinned_version hoặc mẫu settings.json.
