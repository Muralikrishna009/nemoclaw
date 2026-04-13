"""
Image / diagram generation service.
Supports: flowchart (PIL), org_chart (PIL), bar_chart (PIL).
Falls back to dummy_data process flows when no nodes/edges provided.
"""

import os
import uuid
from PIL import Image, ImageDraw, ImageFont

from dummy_data.financial import PROCESS_FLOWS, QUARTERLY_REVENUE, DEPARTMENTS

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Palette ────────────────────────────────────────────────────────────────────
BG          = (250, 251, 252)
PRIMARY     = (26, 26, 46)
ACCENT      = (15, 52, 96)
HIGHLIGHT   = (233, 69, 96)
GREEN_NODE  = (39, 174, 96)
ORANGE_NODE = (230, 126, 34)
LIGHT_BG    = (248, 249, 250)
BORDER      = (222, 226, 230)
TEXT_DARK   = (33, 37, 41)
TEXT_MUTED  = (108, 117, 125)
SHADOW_C    = (195, 200, 210)


def _blend(rgb: tuple, alpha: float) -> tuple:
    """Blend rgb with white; alpha=1.0 → full colour, 0.0 → white."""
    return tuple(int(c * alpha + 255 * (1 - alpha)) for c in rgb)


# ── Fonts ──────────────────────────────────────────────────────────────────────

_REGULAR_PATHS = [
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
_BOLD_PATHS = [
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _font(size: int, bold: bool = False):
    for path in (_BOLD_PATHS if bold else _REGULAR_PATHS):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ── Low-level drawing helpers ──────────────────────────────────────────────────

def _rrect(draw, xy, radius, fill, outline=None, lw=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=lw)


def _shadow(draw, xy, radius=10, offset=5):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(
        [x0 + offset, y0 + offset, x1 + offset, y1 + offset],
        radius=radius, fill=SHADOW_C,
    )


def _arrow_v(draw, x1, y1, x2, y2, color, lw=2, aw=8):
    """Downward arrow with filled triangular head."""
    draw.line([(x1, y1), (x2, y2 - aw)], fill=color, width=lw)
    draw.polygon(
        [(x2, y2), (x2 - aw, y2 - int(aw * 1.4)), (x2 + aw, y2 - int(aw * 1.4))],
        fill=color,
    )


def _arrow_h_right(draw, x1, y1, x2, y2, label, font, color, lw=2, aw=8):
    """
    Horizontal right-pointing arrow from (x1,y1) to (x2,y2).
    Renders an optional label bubble centred above the midpoint.
    """
    draw.line([(x1, y1), (x2 - aw, y2)], fill=color, width=lw)
    draw.polygon(
        [(x2, y2), (x2 - int(aw * 1.4), y2 - int(aw * 0.7)),
         (x2 - int(aw * 1.4), y2 + int(aw * 0.7))],
        fill=color,
    )
    if label:
        lx, ly = (x1 + x2) // 2, y1 - 14
        try:
            bbox = font.getbbox(label)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            pad = 5
            _rrect(draw,
                   [lx - tw // 2 - pad, ly - th - pad, lx + tw // 2 + pad, ly + pad],
                   radius=4, fill=_blend(color, 0.15), outline=color, lw=1)
        except AttributeError:
            pass
        draw.text((lx, ly), label, fill=color, font=font, anchor="mb")


# ── Flowchart ──────────────────────────────────────────────────────────────────

def generate_flowchart(title: str, nodes: list, edges: list, conditionals: dict = None) -> str:
    """Generate a production-ready top-down flowchart using PIL."""
    filename = f"flowchart_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    NW, NH   = 280, 68    # node width / height
    V_GAP    = 90         # vertical centre-to-centre gap
    H_GAP    = 90         # gap between right-edge of main col and left-edge of branch
    MX       = 80         # horizontal margin
    HEADER_H = 100
    FOOTER_H = 48

    cx = MX + NW // 2
    pos: dict = {node: (cx, HEADER_H + 54 + i * (NH + V_GAP))
                 for i, node in enumerate(nodes)}

    # Branch nodes to the right of their parent, same Y
    extra: dict = {}
    if conditionals:
        for parent, branches in conditionals.items():
            if parent not in pos:
                continue
            px, py = pos[parent]
            bx = px + NW // 2 + H_GAP + NW // 2
            for lbl, bnode in branches.items():
                extra[bnode] = (bx, py)
                pos[bnode]   = (bx, py)

    has_extra = bool(extra)
    cw = MX * 2 + NW + (H_GAP + NW if has_extra else 0) + 40
    ch = max(pos[n][1] for n in pos) + NH // 2 + FOOTER_H + 44
    cw, ch = max(cw, 560), max(ch, 500)

    img  = Image.new("RGB", (cw, ch), BG)
    draw = ImageDraw.Draw(img)

    f_title = _font(22, bold=True)
    f_sub   = _font(13)
    f_node  = _font(14, bold=True)
    f_lbl   = _font(11)

    # ── Header ─────────────────────────────────────────────────────────────────
    draw.rectangle([0, 0, cw, HEADER_H], fill=PRIMARY)
    draw.rectangle([0, HEADER_H - 6, cw, HEADER_H], fill=HIGHLIGHT)
    draw.text((cw // 2, HEADER_H // 2 - 10), title,
              fill=(255, 255, 255), font=f_title, anchor="mm")
    draw.text((cw // 2, HEADER_H - 26), "Process Flow Diagram",
              fill=(150, 175, 210), font=f_sub, anchor="mm")

    # ── Main-flow edges ─────────────────────────────────────────────────────────
    for src, dst in edges:
        if src not in pos or dst not in pos:
            continue
        sx, sy = pos[src]
        dx, dy = pos[dst]
        _arrow_v(draw, sx, sy + NH // 2, dx, dy - NH // 2, color=ACCENT)

    # ── Conditional (branch) edges ──────────────────────────────────────────────
    if conditionals:
        for parent, branches in conditionals.items():
            if parent not in pos:
                continue
            px, py = pos[parent]
            for lbl, bnode in branches.items():
                if bnode not in pos:
                    continue
                bx, by = pos[bnode]
                _arrow_h_right(
                    draw,
                    x1=px + NW // 2, y1=py,
                    x2=bx - NW // 2, y2=by,
                    label=lbl, font=f_lbl, color=ORANGE_NODE,
                )

    # ── Main-column nodes ───────────────────────────────────────────────────────
    for i, node in enumerate(nodes):
        x, y = pos[node]
        x0, y0, x1, y1 = x - NW // 2, y - NH // 2, x + NW // 2, y + NH // 2
        is_start = (i == 0)
        is_end   = (i == len(nodes) - 1)
        r    = NH // 2 if (is_start or is_end) else 12
        fill = GREEN_NODE if is_start else (HIGHLIGHT if is_end else ACCENT)

        _shadow(draw, [x0, y0, x1, y1], radius=r)
        _rrect(draw, [x0, y0, x1, y1], radius=r, fill=fill, outline=PRIMARY)
        draw.text((x, y), node, fill=(255, 255, 255), font=f_node, anchor="mm")

    # ── Branch (conditional failure) nodes ─────────────────────────────────────
    for node, (x, y) in extra.items():
        x0, y0, x1, y1 = x - NW // 2, y - NH // 2, x + NW // 2, y + NH // 2
        _shadow(draw, [x0, y0, x1, y1], radius=12)
        _rrect(draw, [x0, y0, x1, y1], radius=12,
               fill=_blend(ORANGE_NODE, 0.12), outline=ORANGE_NODE)
        draw.text((x, y), node, fill=ORANGE_NODE, font=f_node, anchor="mm")

    # ── Footer ──────────────────────────────────────────────────────────────────
    fy = ch - FOOTER_H
    draw.rectangle([0, fy, cw, ch], fill=_blend(PRIMARY, 0.05))
    draw.line([(0, fy), (cw, fy)], fill=BORDER, width=1)
    draw.text((cw // 2, ch - FOOTER_H // 2),
              "NemoClaw Financial Platform",
              fill=TEXT_MUTED, font=f_sub, anchor="mm")

    img.save(filepath, "PNG", dpi=(200, 200))
    return filepath


# ── Bar Chart ──────────────────────────────────────────────────────────────────

def generate_bar_chart(title: str, params: dict) -> str:
    filename = f"chart_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    period = params.get("period", "Q1 2025")
    data   = QUARTERLY_REVENUE.get(period, list(QUARTERLY_REVENUE.values())[0])

    labels   = [r["month"] for r in data]
    revenues = [r["revenue"] for r in data]
    expenses = [r["expenses"] for r in data]
    profits  = [r["profit"] for r in data]

    cw, ch     = 900, 560
    ML, MR     = 92, 40
    MT, MB     = 110, 92
    chart_w    = cw - ML - MR
    chart_h    = ch - MT - MB

    img  = Image.new("RGB", (cw, ch), BG)
    draw = ImageDraw.Draw(img)

    f_title  = _font(22, bold=True)
    f_axis   = _font(11)
    f_label  = _font(10)
    f_legend = _font(13)

    # Header
    draw.rectangle([0, 0, cw, 74], fill=PRIMARY)
    draw.rectangle([0, 68, cw, 74], fill=HIGHLIGHT)
    draw.text((cw // 2, 37),
              title or f"Revenue vs Expenses — {period}",
              fill=(255, 255, 255), font=f_title, anchor="mm")

    max_val = max(revenues) * 1.18
    n       = len(labels)
    group_w = chart_w / n
    bar_w   = int(group_w * 0.21)

    def to_y(val: float) -> int:
        return MT + chart_h - int((val / max_val) * chart_h)

    # Horizontal grid lines + Y labels
    for i in range(6):
        gy   = MT + int(chart_h * i / 5)
        gcol = TEXT_DARK if i == 5 else BORDER
        draw.line([(ML, gy), (ML + chart_w, gy)], fill=gcol, width=1)
        v = max_val * (5 - i) / 5
        draw.text((ML - 10, gy), f"${v/1000:.0f}k",
                  fill=TEXT_MUTED, font=f_axis, anchor="rm")

    # Subtle vertical group dividers
    for gi in range(1, n):
        vx = ML + int(gi * group_w)
        draw.line([(vx, MT), (vx, MT + chart_h)],
                  fill=_blend(BORDER, 0.45), width=1)

    # Axes
    draw.line([(ML, MT),          (ML, MT + chart_h)],         fill=TEXT_DARK, width=2)
    draw.line([(ML, MT + chart_h), (ML + chart_w, MT + chart_h)], fill=TEXT_DARK, width=2)

    bar_colors   = [ACCENT, (211, 84, 73), GREEN_NODE]
    series       = [revenues, expenses, profits]
    series_names = ["Revenue", "Expenses", "Profit"]

    for gi in range(n):
        group_x = ML + gi * group_w + group_w * 0.085
        base_y  = MT + chart_h
        lx = ML + gi * group_w + group_w / 2
        draw.text((lx, base_y + 12), labels[gi],
                  fill=TEXT_DARK, font=f_label, anchor="mt")

        for bi, (vals, col) in enumerate(zip(series, bar_colors)):
            bx  = int(group_x) + bi * (bar_w + 3)
            top = to_y(vals[gi])
            bar_h = base_y - top

            if bar_h > bar_w // 2:
                # Rectangle body + ellipse rounded top
                draw.rectangle([bx, top + bar_w // 2, bx + bar_w, base_y], fill=col)
                draw.ellipse([bx, top, bx + bar_w, top + bar_w], fill=col)
            else:
                draw.rectangle([bx, top, bx + bar_w, base_y], fill=col)

            # Value label above the revenue (tallest) bar per group
            if bi == 0:
                draw.text((bx + bar_w // 2, top - 6),
                          f"${vals[gi] // 1000}k",
                          fill=col, font=f_label, anchor="mb")

    # Legend
    leg_y = ch - 52
    for i, (lbl, col) in enumerate(zip(series_names, bar_colors)):
        lx = ML + i * 175
        _rrect(draw, [lx, leg_y + 2, lx + 18, leg_y + 18], radius=4, fill=col)
        draw.text((lx + 26, leg_y + 10), lbl, fill=TEXT_DARK, font=f_legend, anchor="lm")

    # Footer strip
    draw.line([(0, ch - 22), (cw, ch - 22)], fill=BORDER, width=1)
    draw.text((cw // 2, ch - 11), "NemoClaw Financial Platform",
              fill=TEXT_MUTED, font=f_label, anchor="mm")

    img.save(filepath, "PNG", dpi=(200, 200))
    return filepath


# ── Org Chart ──────────────────────────────────────────────────────────────────

def generate_org_chart(title: str, params: dict) -> str:
    filename = f"orgchart_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    sub = {
        "Engineering": ["Frontend", "Backend", "DevOps"],
        "Sales":       ["Inside Sales", "Enterprise"],
    }

    NW, NH     = 160, 44
    cw, ch     = 1100, 510
    HEADER_H   = 72
    FOOTER_H   = 34

    img  = Image.new("RGB", (cw, ch), BG)
    draw = ImageDraw.Draw(img)

    f_title = _font(20, bold=True)
    f_node  = _font(12)

    # Header
    draw.rectangle([0, 0, cw, HEADER_H], fill=PRIMARY)
    draw.rectangle([0, HEADER_H - 5, cw, HEADER_H], fill=HIGHLIGHT)
    draw.text((cw // 2, HEADER_H // 2 - 2),
              title or "Organization Chart",
              fill=(255, 255, 255), font=f_title, anchor="mm")

    dept_list = list(DEPARTMENTS.keys())
    level1_y  = 210
    ceo_x     = cw // 2
    ceo_y     = 120
    positions = {"CEO": (ceo_x, ceo_y)}

    spacing = cw // (len(dept_list) + 1)
    for i, dept in enumerate(dept_list):
        positions[dept] = (spacing * (i + 1), level1_y)

    level2_y  = 340
    sub_nodes = []
    for dept, subs in sub.items():
        if dept not in positions:
            continue
        dx = positions[dept][0]
        sub_sp = NW + 18
        start_x = dx - (len(subs) - 1) * sub_sp // 2
        for j, s in enumerate(subs):
            positions[s] = (start_x + j * sub_sp, level2_y)
            sub_nodes.append((dept, s))

    def _edge(px, py, cx, cy):
        """Elbow connector: parent-bottom → midpoint → child-top."""
        mid_y = (py + NH // 2 + cy - NH // 2) // 2
        draw.line([(px, py + NH // 2), (px, mid_y)],   fill=BORDER, width=2)
        draw.line([(px, mid_y),        (cx, mid_y)],   fill=BORDER, width=2)
        draw.line([(cx, mid_y),        (cx, cy - NH // 2)], fill=BORDER, width=2)

    def _node(x, y, label, fill=ACCENT, is_root=False):
        x0, y0 = x - NW // 2, y - NH // 2
        x1, y1 = x + NW // 2, y + NH // 2
        r = NH // 2 if is_root else 8
        _shadow(draw, [x0, y0, x1, y1], radius=r, offset=4)
        _rrect(draw, [x0, y0, x1, y1], radius=r, fill=fill, outline=PRIMARY)
        draw.text((x, y), label, fill=(255, 255, 255), font=f_node, anchor="mm")

    # Edges first (behind nodes)
    for child in dept_list:
        if child in positions:
            _edge(*positions["CEO"], *positions[child])
    for dept, subs in sub.items():
        for s in subs:
            if dept in positions and s in positions:
                _edge(*positions[dept], *positions[s])

    # Nodes
    _node(*positions["CEO"], "CEO", fill=HIGHLIGHT, is_root=True)
    for dept in dept_list:
        if dept in positions:
            _node(*positions[dept], dept, fill=ACCENT)
    for _, s in sub_nodes:
        if s in positions:
            _node(*positions[s], s, fill=_blend(ACCENT, 0.65))

    # Footer
    draw.line([(0, ch - FOOTER_H), (cw, ch - FOOTER_H)], fill=BORDER, width=1)
    draw.text((cw // 2, ch - FOOTER_H // 2),
              "NemoClaw Financial Platform",
              fill=TEXT_MUTED, font=f_node, anchor="mm")

    img.save(filepath, "PNG", dpi=(200, 200))
    return filepath


# ── Dispatcher ─────────────────────────────────────────────────────────────────

def generate_image(diagram_type: str, title: str, params: dict,
                   nodes: list = None, edges: list = None) -> str:
    if diagram_type == "bar_chart":
        return generate_bar_chart(title=title, params=params)

    if diagram_type == "org_chart":
        return generate_org_chart(title=title, params=params)

    # flowchart (default)
    flow_key     = params.get("flow", "order_processing")
    flow         = PROCESS_FLOWS.get(flow_key, PROCESS_FLOWS["order_processing"])
    final_nodes  = nodes if nodes else flow["nodes"]
    final_edges  = [tuple(e) for e in edges] if edges else flow["edges"]
    conditionals = flow.get("conditionals") if not nodes else None

    return generate_flowchart(
        title=title or f"Flowchart — {flow_key.replace('_', ' ').title()}",
        nodes=final_nodes,
        edges=final_edges,
        conditionals=conditionals,
    )
