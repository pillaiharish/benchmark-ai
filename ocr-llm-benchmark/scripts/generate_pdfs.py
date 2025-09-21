# scripts/generate_pdfs.py
import argparse, hashlib, json, os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

PT_PER_MM = 72.0/25.4
def mm(x): return x * PT_PER_MM

def sha256_of_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def _draw_text_center(cnv, x, y_top, w, h, text, font="Helvetica", size=9):
    """Center single-line text inside the rectangle with top-left (x, y_top), width w, height h."""
    cnv.setFont(font, size)
    text = "" if text is None else str(text)
    tw = cnv.stringWidth(text, font, size)
    tx = x + (w - tw) / 2.0
    ty = y_top - h/2.0 + size * 0.35  # small vertical tweak
    cnv.drawString(tx, ty, text)

def draw_table_manual_with_spans(cnv, x, y_top, col_widths, row_heights, data, spans):
    """
    Draw a table by hand (rects + text) and handle merged cells (row/col spans).
    (x, y_top) is top-left of the whole table.
    """
    rows = len(data)
    cols = len(data[0]) if rows else 0
    assert len({len(r) for r in data}) == 1, "All rows must have the same column count"
    assert len(col_widths) == cols, "col_widths length mismatch"
    assert len(row_heights) == rows, "row_heights length mismatch"

    # Precompute each cell's box (top-left x,y, width, height)
    cell_boxes = [[None]*cols for _ in range(rows)]
    cur_y = y_top
    for row in range(rows):
        h = row_heights[row]
        cur_x = x
        for col in range(cols):
            w = col_widths[col]
            cell_boxes[row][col] = (cur_x, cur_y, w, h)
            cur_x += w
        cur_y -= h

    # Map spans
    spans = spans or []
    span_anchor = {}  # {(row,col): (er,ec)}
    covered = set()   # covered cells (non-anchor)
    for (sr, sc, er, ec) in spans:
        assert 0 <= sr <= er < rows and 0 <= sc <= ec < cols, f"SPAN OOB: {(sr,sc,er,ec)}"
        span_anchor[(sr, sc)] = (er, ec)
        for rr in range(sr, er+1):
            for cc in range(sc, ec+1):
                if not (rr == sr and cc == sc):
                    covered.add((rr, cc))

    # Draw borders
    cnv.setLineWidth(0.5)
    # Non-merged, non-covered cells
    for row in range(rows):
        for col in range(cols):
            if (row, col) in covered or (row, col) in span_anchor:
                continue
            x0, y0, w, h = cell_boxes[row][col]
            cnv.rect(x0, y0 - h, w, h, stroke=1, fill=0)

    # Merged rectangles for anchors
    for (sr, sc), (er, ec) in span_anchor.items():
        x0, y0, _, _ = cell_boxes[sr][sc]
        w = sum(col_widths[sc:ec+1])
        h = sum(row_heights[sr:er+1])
        cnv.rect(x0, y0 - h, w, h, stroke=1, fill=0)

    # Draw text
    for row in range(rows):
        for col in range(cols):
            if (row, col) in covered:
                continue
            if (row, col) in span_anchor:
                er, ec = span_anchor[(row, col)]
                x0, y0, _, _ = cell_boxes[row][col]
                w = sum(col_widths[col:ec+1])
                h = sum(row_heights[row:er+1])
                _draw_text_center(cnv, x0, y0, w, h, data[row][col])
            else:
                x0, y0, w, h = cell_boxes[row][col]
                _draw_text_center(cnv, x0, y0, w, h, data[row][col])

def apply_spans_and_blank(data, spans):
    """
    spans: list of (sr, sc, er, ec) using row/col indices with inclusive end.
    - Safely handles spans=None
    - Mutates `data` to blank covered cells except the top-left anchor.
    - Returns a list of TableStyle ('SPAN', ...) commands (in (col,row) coords).
    """
    style_cmds = []
    if not spans:
        return style_cmds

    rows = len(data)
    cols = len(data[0]) if rows else 0

    for (sr, sc, er, ec) in spans:
        # sanity checks
        if not (0 <= sr <= er < rows and 0 <= sc <= ec < cols):
            raise ValueError(f"SPAN out of bounds: {(sr, sc, er, ec)} for table {rows}x{cols}")

        # blank all covered cells except the top-left anchor
        for r in range(sr, er + 1):
            for c in range(sc, ec + 1):
                if not (r == sr and c == sc):
                    data[r][c] = ""

        # ReportLab expects (col,row)
        style_cmds.append(("SPAN", (sc, sr), (ec, er)))

    return style_cmds
def draw_table(c, data, x, y, col_widths=None, row_heights=None, spans=None):
    """
    Robust against ReportLab 4.4.x SPAN+GRID bug:
      - Apply SPANs first
      - Use BOX + INNERGRID instead of GRID
      - Force layout calc before draw
    """
    # shallow copy so we don't mutate caller data
    data = [row[:] for row in data]
    # ensure rectangular
    assert len({len(r) for r in data}) == 1, "All rows must have the same column count"

    style = []

    # 1) SPAN styles FIRST (no blanking needed)
    if spans:
        for (sr, sc, er, ec) in spans:
            rows = len(data)
            cols = len(data[0])
            if not (0 <= sr <= er < rows and 0 <= sc <= ec < cols):
                raise ValueError(f"SPAN out of bounds: {(sr, sc, er, ec)} for {rows}x{cols}")
            style.append(("SPAN", (sc, sr), (ec, er)))

    # 2) Formatting — BOX + INNERGRID (avoid GRID with spans on 4.4.x)
    style.extend([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ])

    t = Table(data, colWidths=col_widths, rowHeights=row_heights, repeatRows=0)
    t.setStyle(TableStyle(style))

    # Force layout to compute span rects before drawing
    w, h = t.wrapOn(c, 0, 0)  # populates internal _spanRects
    t.drawOn(c, x, y - h)
    return w, h

# ---------- Scenarios ----------

def centered_table_page(path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Centered Table")
    data = [
        ["H1", "H2", "H3"],
        ["A1", "B1", "C1"],
        ["A2", "B2", "C2"],
        ["A3", "B3", "C3"],
    ]
    colw = [mm(30)] * 3
    total_w = sum(colw)
    x = (A4[0] - total_w) / 2.0
    y = A4[1] / 2.0
    draw_table(c, data, x, y, col_widths=colw, spans=None)
    c.showPage()
    c.save()

def full_width_table_page(path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Full Width Table")
    data = [["H1", "H2", "H3", "H4", "H5"]]
    data += [[f"R{r}C{c}" for c in range(1, 6)] for r in range(1, 8)]
    margin = mm(10)
    usable_w = A4[0] - 2 * margin
    colw = [usable_w / 5.0] * 5
    draw_table(c, data, margin, A4[1] - mm(60), col_widths=colw, spans=None)
    c.showPage()
    c.save()

def two_tables_same_cols(path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Two Tables Same Cols")
    data1 = [["H1", "H2", "H3"], ["A", "B", "C"], ["D", "E", "F"]]
    data2 = [["H1", "H2", "H3"], ["1", "2", "3"], ["4", "5", "6"]]
    margin = mm(15)
    gap = mm(6)
    colw = [mm(35)] * 3

    # Top table
    w1, h1 = draw_table(c, data1, margin, A4[1] - mm(40), col_widths=colw, spans=None)

    # Separator line just under the first table
    y_sep = A4[1] - mm(40) - h1 - mm(2)
    c.setLineWidth(0.5)
    c.line(margin, y_sep, margin + w1, y_sep)

    # Bottom table
    y2 = y_sep - gap
    draw_table(c, data2, margin, y2, col_widths=colw, spans=None)
    c.showPage()
    c.save()

def two_tables_diff_cols(path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Two Tables Diff Cols")
    data1 = [["H1", "H2"], ["A", "B"], ["C", "D"]]
    data2 = [["H1", "H2", "H3", "H4"], ["1", "2", "3", "4"], ["5", "6", "7", "8"]]
    margin = mm(15)
    gap = mm(8)
    colw1 = [mm(45)] * 2
    colw2 = [mm(25)] * 4

    w1, h1 = draw_table(c, data1, margin, A4[1] - mm(40), col_widths=colw1, spans=None)
    draw_table(c, data2, margin, A4[1] - mm(40) - h1 - gap, col_widths=colw2, spans=None)
    c.showPage()
    c.save()

def row_merges_splits(path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Row Merges/Splits (Manual)")
    data = [
        ["H1", "H2", "H3", "H4"],
        ["A",  "B",  "C",  "D"],
        ["E",  "F",  "G",  "H"],
        ["I",  "J",  "K",  "L"],
        ["M",  "N",  "O",  "P"],
    ]
    # Merge rows 2–3 in column 0 (E..I), anchor is (row=2,col=0)
    spans = [(2, 0, 3, 0)]
    margin = mm(15)
    colw = [mm(30)] * 4
    # uniform heights for simplicity
    rowh = [mm(10)] * len(data)

    x = margin
    y_top = A4[1] - mm(40)
    draw_table_manual_with_spans(c, x, y_top, colw, rowh, data, spans)
    c.showPage()
    c.save()

def col_merges_splits(path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Col Merges/Splits (Manual)")
    data = [
        ["H1", "H2", "H3", "H4"],
        ["A",  "B",  "C",  "D"],
        ["E",  "F",  "G",  "H"],
        ["I",  "J",  "K",  "L"],
    ]
    # Merge columns 1–2 in HEADER row => (row=0, col=1..2)
    spans = [(0, 1, 0, 2)]
    margin = mm(15)
    colw = [mm(30)] * 4
    rowh = [mm(10)] * len(data)

    x = margin
    y_top = A4[1] - mm(40)
    draw_table_manual_with_spans(c, x, y_top, colw, rowh, data, spans)
    c.showPage()
    c.save()


# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    #gens = [("05_row_merges_splits.pdf", row_merges_splits)]
    gens = [
        ("01_centered_table.pdf", centered_table_page),
        ("02_full_width_table.pdf", full_width_table_page),
        ("03_two_tables_same_cols.pdf", two_tables_same_cols),
        ("04_two_tables_diff_cols.pdf", two_tables_diff_cols),
        ("05_row_merges_splits.pdf", row_merges_splits),
        ("06_col_merges_splits.pdf", col_merges_splits),
    ]

    items = []
    for fname, fn in gens:
        path = os.path.join(args.out, fname)
        fn(path)
        items.append({"file": fname, "sha256": sha256_of_file(path)})

    manifest = {
        "page_size": "A4",
        "items": items,
    }
    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()

