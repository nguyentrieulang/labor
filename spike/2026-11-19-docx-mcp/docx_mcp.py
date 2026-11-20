"""Minimal MCP stdio server: Word tools owned by the core, confined to one workspace.

Agent has no shell; this is its only way to read/write .docx.
Rules: every path is relative to the workspace root; reads allowed from input/, templates/, output/;
writes only to output/; decisions/ never readable/writable through this tool (core feeds it separately).
Usage (from mcp config): python -X utf8 docx_mcp.py --root <workspace>
"""
import argparse, copy, json, sys, traceback
from pathlib import Path
import docx
from docx.text.paragraph import Paragraph
from docx.table import Table

ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--log")
A = ap.parse_args()
ROOT = Path(A.root).resolve()
READ_DIRS, WRITE_DIRS = ("input", "templates", "output"), ("output",)


def log(msg):
    if A.log:
        with open(A.log, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


def safe(rel, dirs):
    p = (ROOT / rel).resolve()
    try:
        r = p.relative_to(ROOT)
    except ValueError:
        raise PermissionError(f"đường dẫn ngoài workspace: {rel}")
    if not r.parts or r.parts[0] not in dirs:
        raise PermissionError(f"chỉ được dùng thư mục {', '.join(dirs)}: {rel}")
    if p.suffix.lower() != ".docx":
        raise PermissionError("chỉ xử lý file .docx")
    return p


def blocks(d):
    out = []
    for el in d.element.body.iterchildren():
        tag = el.tag.split("}")[1]
        if tag == "p":
            out.append(Paragraph(el, d))
        elif tag == "tbl":
            out.append(Table(el, d))
    return out


def tool_read(path):
    d = docx.Document(safe(path, READ_DIRS))
    res = []
    for i, b in enumerate(blocks(d)):
        if isinstance(b, Paragraph):
            res.append({"i": i, "type": "paragraph", "style": b.style.name, "text": b.text})
        else:
            res.append({"i": i, "type": "table", "rows": [[c.text for c in r.cells] for r in b.rows]})
    return json.dumps(res, ensure_ascii=False)


def set_text(par, text):
    """Replace paragraph text, keep the formatting of the first run."""
    runs = par.runs
    if not runs:
        par.add_run(text); return
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def tool_build(template, output, operations):
    src = safe(template, READ_DIRS)
    dst = safe(output, WRITE_DIRS)
    d = docx.Document(src)
    bl = blocks(d)          # indices refer to the template as read by docx_read
    tables = [b for b in bl if isinstance(b, Table)]
    done = []
    for op in operations:
        k = op.get("op")
        if k == "replace_text":
            n = 0
            pars = list(d.paragraphs) + [p for t in d.tables for row in t.rows for c in row.cells for p in c.paragraphs]
            for p in pars:
                if op["find"] in p.text:
                    set_text(p, p.text.replace(op["find"], op["replace"])); n += 1
            done.append(f"replace_text {op['find']!r}: {n}")
        elif k == "set_paragraph":
            b = bl[op["index"]]; assert isinstance(b, Paragraph), "index không phải đoạn văn"
            set_text(b, op["text"]); done.append(f"set_paragraph {op['index']}")
        elif k == "insert_paragraphs_after":
            b = bl[op["index"]]; assert isinstance(b, (Paragraph, Table))
            anchor = b._element if isinstance(b, Table) else b._p
            for item in op["paragraphs"]:
                new = copy.deepcopy(anchor) if isinstance(b, Paragraph) else None
                if new is None:
                    new = d.add_paragraph()._p
                anchor.addnext(new); anchor = new
                p = Paragraph(new, b._parent if isinstance(b, Paragraph) else d)
                set_text(p, item.get("text", ""))
                if item.get("style"):
                    p.style = d.styles[item["style"]]
            done.append(f"insert_paragraphs_after {op['index']}: {len(op['paragraphs'])}")
        elif k == "table_fill_rows":
            t = tables[op["table"]]
            tmpl_row = t.rows[op.get("template_row", len(t.rows) - 1)]
            for cells in op["rows"]:
                new = copy.deepcopy(tmpl_row._tr); t._tbl.append(new)
                row = t.rows[-1]
                for c, v in zip(row.cells, cells):
                    pars = c.paragraphs
                    set_text(pars[0], str(v))
                    for extra in pars[1:]:
                        extra._p.getparent().remove(extra._p)
            if op.get("remove_template_row", True):
                t._tbl.remove(tmpl_row._tr)
            done.append(f"table_fill_rows {op['table']}: {len(op['rows'])}")
        elif k == "delete_block":
            el = bl[op["index"]]._element if isinstance(bl[op["index"]], Table) else bl[op["index"]]._p
            el.getparent().remove(el); done.append(f"delete_block {op['index']}")
        else:
            raise ValueError(f"op không hỗ trợ: {k}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    d.save(dst)
    return "Đã ghi " + str(dst.relative_to(ROOT)) + "\n" + "\n".join(done)


TOOLS = [
    {"name": "docx_read",
     "description": "Đọc file .docx trong input/, templates/ hoặc output/ của workspace. Trả về danh sách khối theo thứ tự: "
                    "đoạn văn (i, style, text) và bảng (i, rows). Dùng chỉ số i cho docx_build.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string", "description": "đường dẫn tương đối, ví dụ templates/mau.docx"}},
                     "required": ["path"]}},
    {"name": "docx_build",
     "description": "Tạo file .docx mới trong output/ từ một file mẫu, giữ nguyên định dạng mẫu, rồi áp các thao tác theo thứ tự. "
                    "Chỉ số index và table lấy theo kết quả docx_read của file mẫu (bảng đánh số 0,1,2… theo thứ tự xuất hiện). Thao tác: "
                    "replace_text{find,replace}; set_paragraph{index,text}; insert_paragraphs_after{index,paragraphs:[{text,style?}]}; "
                    "table_fill_rows{table,rows:[[ô,…]],template_row?,remove_template_row?=true} (nhân bản dòng mẫu, mặc định dòng cuối); "
                    "delete_block{index}. Nên làm insert/delete sau cùng vì index tính theo bản mẫu.",
     "inputSchema": {"type": "object", "properties": {
         "template": {"type": "string"}, "output": {"type": "string", "description": "phải nằm trong output/"},
         "operations": {"type": "array", "items": {"type": "object"}}},
         "required": ["template", "output", "operations"]}},
]


def handle(req):
    m = req.get("method")
    if m == "initialize":
        return {"protocolVersion": req["params"].get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {}}, "serverInfo": {"name": "labour-docx", "version": "0.1"}}
    if m == "tools/list":
        return {"tools": TOOLS}
    if m == "tools/call":
        name, args = req["params"]["name"], req["params"].get("arguments", {})
        log(f"CALL {name} {json.dumps(args, ensure_ascii=False)[:500]}")
        try:
            text = tool_read(**args) if name == "docx_read" else tool_build(**args)
            log("  OK"); return {"content": [{"type": "text", "text": text}]}
        except Exception as e:
            log(f"  ERR {e}")
            return {"content": [{"type": "text", "text": f"Lỗi: {e}"}], "isError": True}
    if m == "ping":
        return {}
    raise KeyError(m)


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    req = json.loads(line)
    if "id" not in req:      # notification
        continue
    try:
        resp = {"jsonrpc": "2.0", "id": req["id"], "result": handle(req)}
    except Exception as e:
        resp = {"jsonrpc": "2.0", "id": req["id"], "error": {"code": -32601, "message": str(e)}}
    sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n"); sys.stdout.flush()
