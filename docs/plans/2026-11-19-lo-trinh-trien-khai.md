# Lộ trình triển khai Labour (MVP – yêu cầu v2.2, phương án A)

**Spec:** `docs/2026-11-19-LLD-agent-team-v2.2-v0.2.docx` (LLD v0.2), dựa trên HLD v0.6.
**Mã nguồn:** repo git mới `C:\Works\Labour\code` (gói `labour`, thư mục `tests/`).

Chia 5 giai đoạn theo thứ tự chuyên gia đề xuất (CSDL + nhận tin → lập lịch → Claude Code → review + Word → vận hành).
Mỗi giai đoạn có một kế hoạch chi tiết riêng (`docs/plans/…-pN-….md`), viết khi giai đoạn trước xong, để dùng đúng
tên và interface đã có trong mã. Mỗi giai đoạn kết thúc bằng phần mềm chạy được và bộ test xanh.

| GĐ | Tên | Phạm vi (mục LLD) | Kết quả kiểm được (tiêu chí xong) |
|---|---|---|---|
| P1 | Nền móng: CSDL, nhận tin, lệnh | 2, 3, 4, 5 (kênh), 7.1–7.3, 8.1 (mẫu tin), 11, 12, 4.3 | Bot thật trong nhóm thử: /start đăng ký nhóm Nội bộ + tạo workspace; /vai /status /skills trả lời; thành viên thường gõ /baomat → T13; /start trong chat riêng bị bỏ qua; tin trùng qua 4 bot xử lý 1 lần; 40+ câu mẫu intents đúng. Chưa có AI. |
| P2 | Thread, lượt và lập lịch (FakeRuntime) | 5 (runtime ports), 7.4, 7.5, 7.7, 7.8 (logic), 7.10, 8.1–8.2, 13 | Với FakeRuntime: giao việc mở Thread, một lượt/nhóm, 3 nhóm song song; ask ≤3 + leo thang + chủ nhóm trả lời reset đúng đếm; trần CLI giữ chỗ; review/đạt/mở lại; Thread mới đóng Thread cũ (T15); khởi động lại → loi. Mọi tin Nội bộ chỉ là mẫu T01–T15. |
| P3 | Chạy Claude Code thật + vai | 3.2–3.3, 6.1–6.8, 7.6, 7.9, 14.3 #2 #4 #6 | Lượt thật bằng claude.exe 2.1.328: Job Object, settings.json/mcp.json/system.md sinh từ mã; giao vai bằng lời → T14 → ok → ghim vai; sửa vai giữa chừng; chốt quyết định + băm + khôi phục; bộ spike 1 + spike 3 chạy trong tests/security đạt. |
| P4 | Công cụ Word + file vào/ra | 9, 8.3, 14.2 | docx_mcp (docx_read, docx_build với op enum, mã lỗi) chạy như tiến trình con của claude.exe; soạn bản phản hồi đối tác từ mẫu thật đã lọc; nhóm Thoải mái nhận/gửi file; Nội bộ từ chối file. |
| P5 | Skill, vận hành, nghiệm thu | 10, 15, 14.3 đủ 6 kiểm tra, 16 | /skill nap/duyet/ngung ở chat riêng; skill có mã bị từ chối; cài trên VM theo mục 15 (Task Scheduler); 6 kiểm tra bảo mật tự động đạt; chạy thử 1 luồng thật “nhận xét đối tác → Word” ở nhóm Nội bộ. |

Ngoài vòng này (LLD mục 16): runtime Grok/Gemini, bản Docker, lưu đội (F-22).

Điểm dừng để người dùng xem: cuối mỗi giai đoạn (demo trên nhóm Telegram thử).
