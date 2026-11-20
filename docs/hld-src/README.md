# Nguồn sinh HLD (Word)
- `diagrams.py` (+ `svgkit.py`): vẽ 14 hình SVG, chụp PNG bằng Chrome headless vào `img/`.
- `build_docx.py <file.docx>`: dựng file Word từ nội dung trong script + ảnh ở `img/`.
- Chạy: `python -X utf8 diagrams.py` rồi `python -X utf8 build_docx.py ..\2026-11-19-HLD-...-v0.6.docx`;
  mở file trong Word để cập nhật mục lục (hoặc Update Field).
