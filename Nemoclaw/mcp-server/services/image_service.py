"""
Image / diagram generation service.
Supports: flowchart (graphviz), org_chart (PIL), bar_chart (PIL).
Falls back to dummy_data process flows when no nodes/edges provided.
"""

import os
import uuid
from PIL import Image, ImageDraw, ImageFont

from dummy_data.financial import PROCESS_FLOWS, QUARTERLY_REVENUE, DEPARTMENTS

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Colors
BG = (255, 255, 255)
PRIMARY = (26, 26, 46)       # #1a1a2e
ACCENT = (15, 52, 96)        # #0f3460
HIGHLIGHT = (233, 69, 96)    # #e94560
GREEN = (39, 174, 96)
LIGHT = (248, 249, 250)
BORDER = (222, 226, 230)
TEXT_DARK = (33, 37, 41)
TEXT_MUTED = (108, 117, 125)


def _try_font(size: int):
    """Try to load a system font, fall back to default."""
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _try_font_bold(size: int):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def colors_rgb(rgb: tuple, alpha: float):
    """Blend with white for lighter fill."""
    return tuple(int(c + (255 - c) * (1 - alpha)) for c in rgb)


# ── Flowchart ─────────────────────────────────────────────────────────────────

def _draw_rounded_rect(draw, xy, radius, fill, outline, width=2):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)


def generate_flowchart(title: str, nodes: list[str], edges: list[tuple], conditionals: dict = None) -> str:
    """Generate a top-down flowchart using PIL."""
    filename = f"flowchart_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    node_w, node_h = 200, 50
    h_gap, v_gap = 60, 80
    margin = 60

    # Layout: single column top-down
    positions = {}
    for i, node in enumerate(nodes):
        x = margin + (node_w // 2)
        y = margin + 80 + i * (node_h + v_gap)
        positions[node] = (x, y)

    # Also add conditional failure nodes (offset to right)
    extra_nodes = {}
    if conditionals:
        for parent, branches in conditionals.items():
            px, py = positions[parent]
            for branch_label, branch_node in branches.items():
                extra_nodes[branch_node] = (px + node_w + h_gap + node_w // 2, py)
                positions[branch_node] = extra_nodes[branch_node]

    total_nodes = len(nodes) + len(extra_nodes)
    canvas_w = margin * 2 + node_w + (node_w + h_gap + node_w if extra_nodes else 0) + 80
    canvas_h = margin + 80 + total_nodes * (node_h + v_gap) + margin

    img = Image.new("RGB", (canvas_w, canvas_h), BG)
    draw = ImageDraw.Draw(img)

    font_title = _try_font_bold(20)
    font_node = _try_font(13)
    font_label = _try_font(10)

    # Title
    draw.rectangle([0, 0, canvas_w, 60], fill=PRIMARY)
    draw.text((canvas_w // 2, 30), title, fill=(255, 255, 255), font=font_title, anchor="mm")

    # Draw edges first (behind nodes)
    for src, dst in edges:
        if src not in positions or dst not in positions:
            continue
        sx, sy = positions[src]
        dx, dy = positions[dst]
        # Arrow from bottom-center of src to top-center of dst
        x1, y1 = sx, sy + node_h // 2
        x2, y2 = dx, dy - node_h // 2
        draw.line([(x1, y1), (x2, y2)], fill=ACCENT, width=2)
        # Arrowhead
        aw = 7
        draw.polygon([(x2, y2), (x2 - aw, y2 - aw), (x2 + aw, y2 - aw)], fill=ACCENT)

    # Draw conditional edges
    if conditionals:
        for parent, branches in conditionals.items():
            if parent not in positions:
                continue
            px, py = positions[parent]
            for branch_label, branch_node in branches.items():
                if branch_node not in positions:
                    continue
                bx, by = positions[branch_node]
                x1, y1 = px + node_w // 2, py
                x2, y2 = bx - node_w // 2, by
                mid_x = (x1 + x2) // 2
                draw.line([(x1, y1), (mid_x, y1), (mid_x, y2), (x2, y2)], fill=HIGHLIGHT, width=2)
                # Label
                draw.text(((x1 + x2) // 2, (y1 + y2) // 2), branch_label, fill=HIGHLIGHT, font=font_label, anchor="mm")

    # Draw nodes
    for i, node in enumerate(nodes):
        x, y = positions[node]
        x0, y0 = x - node_w // 2, y - node_h // 2
        x1, y1 = x + node_w // 2, y + node_h // 2
        # First and last nodes are rounded differently (start/end)
        is_terminal = (i == 0 or i == len(nodes) - 1)
        fill = HIGHLIGHT if is_terminal else ACCENT
        _draw_rounded_rect(draw, [x0, y0, x1, y1], radius=25 if is_terminal else 8, fill=fill, outline=PRIMARY, width=2)
        draw.text((x, y), node, fill=(255, 255, 255), font=font_node, anchor="mm")

    # Draw conditional/extra nodes
    for node, (x, y) in extra_nodes.items():
        x0, y0 = x - node_w // 2, y - node_h // 2
        x1, y1 = x + node_w // 2, y + node_h // 2
        _draw_rounded_rect(draw, [x0, y0, x1, y1], radius=8, fill=colors_rgb(HIGHLIGHT, 0.2), outline=HIGHLIGHT, width=2)
        draw.text((x, y), node, fill=HIGHLIGHT, font=font_node, anchor="mm")

    img.save(filepath, "PNG", dpi=(150, 150))
    return filepath


# ── Bar Chart ─────────────────────────────────────────────────────────────────

def generate_bar_chart(title: str, params: dict) -> str:
    filename = f"chart_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    period = params.get("period", "Q1 2025")
    data = QUARTERLY_REVENUE.get(period, list(QUARTERLY_REVENUE.values())[0])

    labels = [r["month"] for r in data]
    revenues = [r["revenue"] for r in data]
    expenses = [r["expenses"] for r in data]
    profits = [r["profit"] for r in data]

    canvas_w, canvas_h = 900, 550
    margin_left, margin_right = 80, 40
    margin_top, margin_bottom = 100, 80
    chart_w = canvas_w - margin_left - margin_right
    chart_h = canvas_h - margin_top - margin_bottom

    img = Image.new("RGB", (canvas_w, canvas_h), BG)
    draw = ImageDraw.Draw(img)

    font_title = _try_font_bold(22)
    font_axis = _try_font(12)
    font_label = _try_font(11)
    font_legend = _try_font(13)

    # Header
    draw.rectangle([0, 0, canvas_w, 70], fill=PRIMARY)
    draw.text((canvas_w // 2, 35), title or f"Revenue vs Expenses — {period}", fill=(255, 255, 255), font=font_title, anchor="mm")

    max_val = max(revenues) * 1.15
    n = len(labels)
    group_w = chart_w / n
    bar_w = group_w * 0.22

    def val_to_y(val):
        return margin_top + chart_h - int((val / max_val) * chart_h)

    # Grid lines
    for i in range(6):
        y = margin_top + int(chart_h * i / 5)
        draw.line([(margin_left, y), (margin_left + chart_w, y)], fill=BORDER, width=1)
        v = max_val * (5 - i) / 5
        draw.text((margin_left - 8, y), f"${v/1000:.0f}k", fill=TEXT_MUTED, font=font_axis, anchor="rm")

    # Axes
    draw.line([(margin_left, margin_top), (margin_left, margin_top + chart_h)], fill=TEXT_DARK, width=2)
    draw.line([(margin_left, margin_top + chart_h), (margin_left + chart_w, margin_top + chart_h)], fill=TEXT_DARK, width=2)

    bar_colors = [ACCENT, (231, 76, 60), GREEN]
    series = [revenues, expenses, profits]
    series_labels = ["Revenue", "Expenses", "Profit"]

    for gi in range(n):
        group_x = margin_left + gi * group_w + group_w * 0.1
        lx = margin_left + gi * group_w + group_w / 2
        draw.text((lx, margin_top + chart_h + 16), labels[gi], fill=TEXT_DARK, font=font_label, anchor="mt")

        for bi, (vals, color) in enumerate(zip(series, bar_colors)):
            bx = group_x + bi * (bar_w + 2)
            by = val_to_y(vals[gi])
            base_y = margin_top + chart_h
            draw.rectangle([bx, by, bx + bar_w, base_y], fill=color, outline=None)

    # Legend
    legend_x = margin_left
    for i, (label, color) in enumerate(zip(series_labels, bar_colors)):
        lx = legend_x + i * 180
        draw.rectangle([lx, canvas_h - 35, lx + 16, canvas_h - 19], fill=color)
        draw.text((lx + 22, canvas_h - 35), label, fill=TEXT_DARK, font=font_legend)

    img.save(filepath, "PNG", dpi=(150, 150))
    return filepath


# ── Org Chart ─────────────────────────────────────────────────────────────────

def generate_org_chart(title: str, params: dict) -> str:
    filename = f"orgchart_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    org = {
        "CEO": ["Sales", "Engineering", "Marketing", "Operations", "HR"],
    }
    sub = {
        "Engineering": ["Frontend", "Backend", "DevOps"],
        "Sales": ["Inside Sales", "Enterprise"],
    }

    node_w, node_h = 160, 44
    canvas_w, canvas_h = 1100, 480
    img = Image.new("RGB", (canvas_w, canvas_h), BG)
    draw = ImageDraw.Draw(img)

    font_title = _try_font_bold(20)
    font_node = _try_font(12)

    draw.rectangle([0, 0, canvas_w, 60], fill=PRIMARY)
    draw.text((canvas_w // 2, 30), title or "Organization Chart", fill=(255, 255, 255), font=font_title, anchor="mm")

    # CEO at top center
    ceo_x, ceo_y = canvas_w // 2, 100
    positions = {"CEO": (ceo_x, ceo_y)}

    # Level 1: departments
    dept_list = list(DEPARTMENTS.keys())
    level1_y = 210
    spacing = canvas_w // (len(dept_list) + 1)
    for i, dept in enumerate(dept_list):
        x = spacing * (i + 1)
        positions[dept] = (x, level1_y)

    # Level 2: sub-departments
    level2_y = 330
    sub_nodes = []
    for dept, subs in sub.items():
        if dept not in positions:
            continue
        dx = positions[dept][0]
        sub_spacing = node_w + 20
        start_x = dx - (len(subs) - 1) * sub_spacing // 2
        for j, s in enumerate(subs):
            positions[s] = (start_x + j * sub_spacing, level2_y)
            sub_nodes.append((dept, s))

    def draw_node(x, y, label, is_root=False):
        x0, y0 = x - node_w // 2, y - node_h // 2
        x1, y1 = x + node_w // 2, y + node_h // 2
        fill = HIGHLIGHT if is_root else ACCENT
        _draw_rounded_rect(draw, [x0, y0, x1, y1], radius=8, fill=fill, outline=PRIMARY, width=2)
        draw.text((x, y), label, fill=(255, 255, 255), font=font_node, anchor="mm")

    # Draw edges
    for parent, children in [("CEO", dept_list)] + list(sub.items()):
        if parent not in positions:
            continue
        px, py = positions[parent]
        for child in children:
            if child not in positions:
                continue
            cx, cy = positions[child]
            draw.line([(px, py + node_h // 2), (cx, cy - node_h // 2)], fill=BORDER, width=2)

    # Draw nodes
    draw_node(*positions["CEO"], "CEO", is_root=True)
    for dept in dept_list:
        if dept in positions:
            draw_node(*positions[dept], dept)
    for _, s in sub_nodes:
        if s in positions:
            draw_node(*positions[s], s)

    img.save(filepath, "PNG", dpi=(150, 150))
    return filepath


# ── Dispatcher ────────────────────────────────────────────────────────────────

def generate_image(diagram_type: str, title: str, params: dict, nodes: list = None, edges: list = None) -> str:
    if diagram_type == "bar_chart":
        return generate_bar_chart(title=title, params=params)

    if diagram_type == "org_chart":
        return generate_org_chart(title=title, params=params)

    # flowchart (default)
    flow_key = params.get("flow", "order_processing")
    flow = PROCESS_FLOWS.get(flow_key, PROCESS_FLOWS["order_processing"])

    final_nodes = nodes if nodes else flow["nodes"]
    final_edges = [tuple(e) for e in edges] if edges else flow["edges"]
    conditionals = flow.get("conditionals") if not nodes else None

    return generate_flowchart(
        title=title or f"Flowchart — {flow_key.replace('_', ' ').title()}",
        nodes=final_nodes,
        edges=final_edges,
        conditionals=conditionals,
    )
