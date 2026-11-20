"""Tiny SVG helpers for HLD diagrams."""
from html import escape

FONT = "Segoe UI, Arial, sans-serif"
INK = "#1f2937"
QUIET = "#4b5563"
EDGE = "#6b7280"
ACC = "#2563eb"
ACC_FILL = "#e8effd"
EXT_FILL = "#f3f4f6"
FUT = "#9ca3af"
CONT_FILL = "#fafafa"


def t(x, y, s, size=13, weight=400, anchor="middle", fill=INK, italic=False):
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{fill}"{st}>{escape(s)}</text>')


def box(x, y, w, h, title, lines=(), kind="n", size=13):
    """kind: n normal, core accent, ext external, fut future (dashed)."""
    stroke, fill, sw, dash = EDGE, "#ffffff", 1.2, ""
    if kind == "core":
        stroke, fill, sw = ACC, ACC_FILL, 2
    elif kind == "ext":
        fill = EXT_FILL
    elif kind == "fut":
        stroke, dash = FUT, ' stroke-dasharray="5 4"'
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" '
           f'stroke="{stroke}" stroke-width="{sw}"{dash}/>']
    cx = x + w / 2
    n = len(lines)
    block = 18 + 16 * n
    y0 = y + (h - block) / 2 + 13
    tc = FUT if kind == "fut" else INK
    out.append(t(cx, y0, title, size, 600, fill=tc))
    for i, ln in enumerate(lines):
        out.append(t(cx, y0 + 19 + 16 * i, ln, 11.5, 400, fill=FUT if kind == "fut" else QUIET))
    return "\n".join(out)


def container(x, y, w, h, title, dashed=True):
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{CONT_FILL}" '
            f'stroke="{EDGE}" stroke-width="1.2"{dash}/>' + t(x + 14, y + 22, title, 13, 700, "start"))


def line(pts, label=None, lx=None, ly=None, dashed=False, both=False, head=True,
         color=EDGE, lanchor="middle", lsize=11.5):
    d = "M" + " L".join(f"{a} {b}" for a, b in pts)
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    me = ' marker-end="url(#arr)"' if head else ""
    ms = ' marker-start="url(#arr)"' if both else ""
    out = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.3"{dash}{me}{ms}/>'
    if label:
        if lx is None:
            (x1, y1), (x2, y2) = pts[0], pts[-1]
            lx, ly = (x1 + x2) / 2, (y1 + y2) / 2 - 6
        parts = label.split("\n")
        for i, p in enumerate(parts):
            out += t(lx, ly + 14 * i, p, lsize, 400, lanchor, QUIET)
    return out


def actor(cx, y, name, sub=None):
    s = [f'<circle cx="{cx}" cy="{y + 10}" r="9" fill="none" stroke="{INK}" stroke-width="1.4"/>',
         f'<path d="M{cx} {y + 19} V{y + 42} M{cx - 14} {y + 28} H{cx + 14} '
         f'M{cx} {y + 42} L{cx - 11} {y + 58} M{cx} {y + 42} L{cx + 11} {y + 58}" '
         f'fill="none" stroke="{INK}" stroke-width="1.4"/>',
         t(cx, y + 76, name, 12.5, 600)]
    if sub:
        s.append(t(cx, y + 92, sub, 11, 400, fill=QUIET))
    return "\n".join(s)


def ellipse(cx, cy, rx, ry, label):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#ffffff" stroke="{EDGE}" stroke-width="1.2"/>'
            + t(cx, cy + 4, label, 12.5))


def svg(w, h, body, title=None, subtitle=None):
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">'
            '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{EDGE}"/></marker>'
            '<marker id="tri" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="11" markerHeight="11" '
            f'orient="auto"><path d="M0 0L12 6L0 12z" fill="#ffffff" stroke="{EDGE}"/></marker></defs>'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>')
    parts = [head]
    if title:
        parts.append(t(20, 28, title, 15, 700, "start"))
    if subtitle:
        parts.append(t(20, 48, subtitle, 12, 400, "start", QUIET))
    parts.append(body)
    parts.append("</svg>")
    return "\n".join(parts)


def sequence(parts, msgs, w, title, subtitle=None, row=34, top=70):
    """parts: [(key, label, sub)]; msgs: ('m', a, b, text, dashed) | ('self', a, text)
    | ('note', a, b, text)."""
    n = len(parts)
    margin = 90
    xs = {k: margin + i * (w - 2 * margin) / (n - 1) for i, (k, _, _) in enumerate(parts)}
    body = []
    y = top + 78
    rows = []
    for m in msgs:
        rows.append((m, y))
        y += row + (10 if m[0] in ("note", "self") else 0)
    h_end = y + 10
    for k, label, sub in parts:
        x = xs[k]
        body.append(f'<line x1="{x}" y1="{top + 44}" x2="{x}" y2="{h_end}" stroke="{FUT}" stroke-dasharray="4 4"/>')
        body.append(box(x - 75, top, 150, 44, label, [sub] if sub else [], "ext"))
    num = 0
    for m, yy in rows:
        if m[0] == "m":
            _, a, b, text, dashed = m
            num += 1
            x1, x2 = xs[a], xs[b]
            body.append(line([(x1, yy), (x2, yy)], dashed=dashed))
            lx = (x1 + x2) / 2
            body.append(t(lx, yy - 6, f"{num}. {text}", 11.5, 400, fill=INK))
        elif m[0] == "self":
            _, a, text = m
            num += 1
            x = xs[a]
            body.append(line([(x, yy - 8), (x + 30, yy - 8), (x + 30, yy + 10), (x + 4, yy + 10)]))
            body.append(t(x + 38, yy + 5, f"{num}. {text}", 11.5, 400, "start"))
        elif m[0] == "note":
            _, a, b, text = m
            x1, x2 = xs[a] - 60, xs[b] + 60
            body.append(f'<rect x="{x1}" y="{yy - 16}" width="{x2 - x1}" height="26" rx="4" '
                        f'fill="#fff8e1" stroke="#d4a72c"/>')
            body.append(t((x1 + x2) / 2, yy + 2, text, 11.5, 600, fill=INK))
    return svg(w, h_end + 20, "\n".join(body), title, subtitle)
