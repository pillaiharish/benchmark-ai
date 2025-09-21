import argparse, json
from pypdf import PdfReader

A4_MM = (210, 297)
POINTS_PER_MM = 72/25.4

def is_a4(w_pt, h_pt, tol_mm=1.0):
    w_mm = w_pt/POINTS_PER_MM
    h_mm = h_pt/POINTS_PER_MM
    return abs(w_mm-210)<=tol_mm and abs(h_mm-297)<=tol_mm or abs(w_mm-297)<=tol_mm and abs(h_mm-210)<=tol_mm

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    args = ap.parse_args()

    reader = PdfReader(args.file)
    page = reader.pages[0]
    w = float(page.mediabox.width)
    h = float(page.mediabox.height)

    out = {
        "page_points": {"width": w, "height": h},
        "page_mm": {"width": w/POINTS_PER_MM, "height": h/POINTS_PER_MM},
        "is_a4": is_a4(w, h),
        "dpi_note": "PDFs are vector; DPI only applies when rasterized. Log rasterizer DPI separately."
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
