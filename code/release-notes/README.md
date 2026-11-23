# Release notes – Labour

Labour là hệ thống đội AI agent làm việc trong nhóm Telegram: chủ nhóm giao việc bằng tin nhắn, các bot (mỗi bot một vai) soạn, hỏi nhau, review và giao kết quả. Mỗi lần bàn giao là một bản phát hành, có đúng một file release note trong thư mục này.

## Cách đánh số bản

- Mỗi lần bàn giao một bản, số tăng dần: **1.1, 1.2, 1.3, …** Mỗi bản thường ứng với một giai đoạn của lộ trình.
- Sửa lỗi cho một bản đã phát hành thì thêm chữ cái, ví dụ **1.1a**. Trong `pyproject.toml` ghi là `1.1.post1` (chuẩn Python hiểu `1.1a` là bản thử trước 1.1).
- Mỗi bản có git tag cùng tên trong repo `C:\Works\Labour` (mã nằm trong `code/`), bắt đầu từ `1.1a`; bản 1.1 không có tag. Xem toàn bộ thay đổi của một bản: `git diff 1.1a 1.2 -- code`.

## Danh sách bản

| Bản | Ngày | Giai đoạn | Nội dung | Trạng thái |
|---|---|---|---|---|
| [1.1](RELEASE_NOTES_1.1.md) | 20/11/2026 | P1 – Nền móng | CSDL, nhận tin Telegram, đăng ký nhóm, hiểu ý chủ nhóm, lệnh chat. Chưa gọi AI | thay bằng 1.1a |
| [1.1a](RELEASE_NOTES_1.1a.md) | 20/11/2026 | P1 – Nền móng | Sửa lỗi sau review 1.1: luật hiểu ý quá rộng, chọn bot hệ thống, tên bot viết hoa, lệnh cho bot ngoài bể, chia tin dài, `/thanhvien bo`; review lần 2: “huy động”, “không đặt”, “chót” không bị đoán nhầm | chờ nghiệm thu Telegram |

## Các bản dự kiến

| Bản | Giai đoạn | Nội dung |
|---|---|---|
| 1.2 | P2 – Việc và lượt | việc (Thread), hàng đợi lượt, giới hạn hỏi / review, lập lịch (AI giả lập) |
| 1.3 | P3 – Claude Code thật | chạy agent thật, giao vai, chốt quyết định, kiểm bảo mật |
| 1.4 | P4 – Word và file | công cụ Word của lõi, file vào / ra |
| 1.5 | P5 – Skill và vận hành | skill, cài đặt trên VM, nghiệm thu toàn bộ |

## Tài liệu thiết kế

Đường dẫn tính từ `C:\Works\Labour`:
- Yêu cầu: `Requirement_v2.1.docx`, `notes/2026-11-18-yeu-cau-v2.2.md`
- Thiết kế tổng thể (HLD): `docs/2026-11-19-HLD-agent-team-v2.2-phuong-an-A-v0.6.docx`
- Thiết kế chi tiết (LLD): `docs/2026-11-19-LLD-agent-team-v2.2-v0.2.docx`
- Lộ trình và kế hoạch: `docs/plans/2026-11-19-lo-trinh-trien-khai.md`, `docs/plans/2026-11-19-p1-nen-mong.md`
