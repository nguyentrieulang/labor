# Spike 2 (2026-11-19) – Bot soạn Word không cần shell, qua công cụ docx của lõi

Câu hỏi: ở cấu hình C của spike 1 (không Bash, `--restricted`, settings do lõi cấp), bot có soạn được file Word đạt
chất lượng không, nếu chỉ dùng công cụ Word do lõi cung cấp?

## Dựng
- `docx_mcp.py`: MCP server stdio tự viết (~170 dòng, chỉ cần python-docx, không cần gói `mcp`). Hai công cụ:
  - `docx_read(path)` → danh sách khối (đoạn văn + style, bảng) có chỉ số.
  - `docx_build(template, output, operations)` → sao mẫu rồi áp thao tác: replace_text, set_paragraph,
    insert_paragraphs_after, table_fill_rows (nhân bản dòng mẫu), delete_block.
  - Ràng buộc trong server: đường dẫn phải nằm trong workspace; đọc từ input/ templates/ output/; ghi chỉ vào output/;
    chỉ file .docx; decisions/ không đọc/ghi qua công cụ này.
- `run_docx_spike.py`: tạo workspace giả (mẫu, nhận xét đối tác giả lập, file quyết định), chạy `claude -p`
  (Sonnet) với `--restricted --settings … --tools Read,Write,Edit,Glob,Grep --mcp-config … --strict-mcp-config`.

## Kết quả (model Sonnet)

| Ca | Thời gian | Chi phí | Kết quả |
|----|-----------|---------|---------|
| Soạn theo mẫu có ô `{{…}}` | 28 s, 6 lượt | 0,10 USD | Đạt. Giữ định dạng mẫu; 5 nhận xét → 5 dòng; phản hồi bám đúng file quyết định; không sót ô trống. Lần gọi đầu sai tên trường (`type` thay `op`), bot đọc lỗi và tự sửa. |
| Soạn theo "bản phản hồi cũ" làm mẫu (không có ô điền) | 22 s, 5 lượt | 0,05 USD | Đạt. Thay toàn bộ nội dung cũ (kiểm bằng mã: không còn chữ nào của bản cũ), giữ bố cục, văn phong. |
| Tấn công: đọc ../wsB và đường dẫn tuyệt đối, ghi decisions/ | 12 s | 0,01 USD | Bị server từ chối cả hai đường dẫn; không ghi gì vào decisions/. |

Ảnh kết quả: `lab/out_1.png`, `lab/out_2.png` (bản v1). File: `lab/wsA/output/phan_hoi_v1.docx`, `phan_hoi_v2.docx`.

## Kết luận
- Phương án "agent không có shell + công cụ Word do lõi cung cấp" **dùng được** cho luồng MVP (nhận xét đối tác → Word theo mẫu).
- Mỗi lượt soạn ~0,05–0,10 USD với Sonnet nếu tính theo giá API; với gói subscription thì trừ vào hạn mức.

## Việc để LLD
- Schema thao tác trong `docx_build` phải chặt (enum cho `op`, schema riêng từng thao tác) để bot không gọi sai.
- Bổ sung thao tác còn thiếu khi gặp mẫu phức tạp: định dạng chữ trong ô (đậm, nghiêng), ảnh, đầu trang/chân trang,
  mục lục, đánh số; sửa file có sẵn trong output/ (vòng review sửa v1 → v2).
- Skill khác cần chạy mã: theo cùng mẫu – lõi cung cấp công cụ, không cho agent shell.
- Chưa thử: mẫu thật của công ty (định dạng phức tạp hơn), file lớn, tiếng Việt trong header/footer.
