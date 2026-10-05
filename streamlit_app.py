import streamlit as st
import fitz
import numpy as np
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="Invoice Gen", layout="centered")
st.title("🏨 Hotel Invoice 1:1 Generator")

uploaded_file = st.file_uploader("1. Upload your base test.pdf", type=["pdf"])

st.subheader("2. Enter Details")
c1, c2 = st.columns(2)
name = c1.text_input("Guest Name", "Mr. Luke Moore")
a1 = c1.text_input("Address line 1", "438 Airpoint")
a2 = c1.text_input("Address line 2", "Skypark Road")
a3 = c1.text_input("Address line 3", "Bristol")
a4 = c1.text_input("Address line 4", "BS3 3NL")
ino = c2.text_input("Invoice No.", "26683")
inv = c2.text_input("Invoice Date", "02.09.2026")
arr = c2.text_input("Arrival", "28.08.2026")
dep = c2.text_input("Departure", "02.09.2026")
chg = c2.text_input("Nightly Charge", "104.05")

if st.button("Generate Invoice", type="primary"):
    if not uploaded_file:
        st.error("Please upload the base PDF first!")
        st.stop()
    try:
        CHARGE_F = float(chg)
        _a = datetime.strptime(arr, "%d.%m.%Y")
        _d = datetime.strptime(dep, "%d.%m.%Y")
        _nights = max((_d - _a).days, 1)
        ROW_DATES = [(_a + timedelta(days=i)).strftime("%d.%m.%y") for i in range(_nights)]
        CHARGE = "%.2f" % CHARGE_F
        CREDIT_TOTAL = "%.2f" % (CHARGE_F * _nights)
        NET_TOTAL = "%.2f" % round(CHARGE_F * _nights / 1.2, 2)
        VAT_20 = "%.2f" % round(CHARGE_F * _nights - CHARGE_F * _nights / 1.2, 2)

        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page = doc[0]
        SP = [s for b in page.get_text("dict")["blocks"] if b.get("type") == 0 for l in b["lines"] for s in l["spans"]]
        RED = []

        def kill(rect):
            RED.append(fitz.Rect(rect))

        def draw(text, y, bold=False, x=None, right=None, size=9):
            fname = "hebo" if bold else "helv"
            f = fitz.Font(fname)
            w = f.text_length(text, fontsize=size)
            xx = (right - w) if right is not None else x
            page.insert_text((xx, y), text, fontname=fname, fontsize=size, color=(0, 0, 0))

        def find(old, x_min=None, x_max=None):
            c = [s for s in SP if s["text"].strip() == old]
            if not c: c = [s for s in SP if s["text"].strip().startswith(old)]
            if not c: c = [s for s in SP if old.lower() in s["text"].lower()]
            if x_min is not None: c = [s for s in c if s["bbox"][0] >= x_min]
            if x_max is not None: c = [s for s in c if s["bbox"][0] <= x_max]
            return c[0] if c else None

        def span_near(text, y, dx=4):
            c = [s for s in SP if s["text"].strip() == text and abs(s["origin"][1] - y) < dx]
            if not c: c = [s for s in SP if s["text"].strip().startswith(text) and abs(s["origin"][1] - y) < dx]
            return c[0] if c else None

        def split_row(y):
            rs = [s for s in SP if abs(s["origin"][1] - y) < 3 and s["bbox"][0] > 250]
            val = None; lab = []
            for s in rs:
                t = s["text"].strip()
                if val is None and t and all(c in "0123456789.," for c in t):
                    val = s
                else:
                    lab.append(s)
            lr = max([s["bbox"][2] for s in lab], default=None)
            vr = val["bbox"][2] if val else None
            ref = lab[0] if lab else val
            sz = ref["size"] if ref else 9
            bd = ("Bold" in ref["font"]) if ref else False
            return lr, vr, sz, bd

        def grey_extent(y0, y1):
            pix = page.get_pixmap(dpi=72, clip=fitz.Rect(0, y0, page.rect.width, y1))
            a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].mean(axis=2)
            m = (a > 150) & (a < 235)
            cols = np.nonzero(m.any(axis=0))[0]
            if len(cols) == 0: return None, None
            return float(cols.min()), float(cols.max() + 1)

        def replace_exact(old, new):
            s = find(old)
            if not s: return
            kill(fitz.Rect(s["bbox"]) + (-1.5, -1.5, 1.5, 1.5))
            draw(new, s["origin"][1], bold=("Bold" in s["font"]), x=s["origin"][0], size=s["size"])

        for s in list(SP):
            if "Luke Moore" in s["text"] and "Guest" not in s["text"]:
                kill(fitz.Rect(s["bbox"]) + (-1.5, -1.5, 1.5, 1.5))
                draw(name, s["origin"][1], bold=("Bold" in s["font"]), x=s["origin"][0], size=s["size"])

        addr = find("airpoint") or find("skypark") or find("733")
        brl = find("Bristol")
        gb = find("Great Britain")
        if addr:
            g = (brl["origin"][1] - addr["origin"][1]) if brl else 11.0
            x0 = addr["bbox"][0]
            x1 = max(addr["bbox"][2], brl["bbox"][2] if brl else 0, gb["bbox"][2] if gb else 0) + 2
            kill(fitz.Rect(x0 - 2, addr["origin"][1] - 10, x1, addr["origin"][1] + 3 * g + 4))
            draw(a1, addr["origin"][1], x=x0, size=addr["size"])
            draw(a2, addr["origin"][1] + g, x=x0, size=addr["size"])
            draw(a3, addr["origin"][1] + 2 * g, x=x0, size=addr["size"])
            draw(a4, addr["origin"][1] + 3 * g, x=x0, size=addr["size"])

        s_d = find("27.03.2026", x_min=300)
        if s_d: kill(fitz.Rect(s_d["bbox"]) + (-1.5, -1.5, 1.5, 1.5)); draw(inv, s_d["origin"][1], x=s_d["origin"][0], size=s_d["size"])
        s_dp = find("27.03.2026", x_max=300)
        if s_dp: kill(fitz.Rect(s_dp["bbox"]) + (-1.5, -1.5, 1.5, 1.5)); draw(dep, s_dp["origin"][1], x=s_dp["origin"][0], size=s_dp["size"])
        s_ar = find("26.03.2026")
        if s_ar: kill(fitz.Rect(s_ar["bbox"]) + (-1.5, -1.5, 1.5, 1.5)); draw(arr, s_ar["origin"][1], x=s_ar["origin"][0], size=s_ar["size"])
        s_in = find("26683")
        if s_in and ino != "26683": kill(fitz.Rect(s_in["bbox"]) + (-1.5, -1.5, 1.5, 1.5)); draw(ino, s_in["origin"][1], x=s_in["origin"][0], size=s_in["size"])

        row1 = find("26.03.26")
        y_row1 = row1["origin"][1]; x_date = row1["origin"][0]; sz_row = row1["size"]
        x_desc = find("Accommodation")["origin"][0]
        mc = find("Mastercard"); y_mc = mc["origin"][1]
        row_h = y_mc - y_row1
        hdr = {l: find(l) for l in ("Description", "Qty.", "Charges", "Credit")}
        hdr["Date"] = min([s for s in SP if s["text"].strip() == "Date"], key=lambda s: abs(s["origin"][1] - (y_row1 - 10)))
        y_hdr = hdr["Date"]["origin"][1]; sz_hdr = hdr["Date"]["size"]; bd_hdr = "Bold" in hdr["Date"]["font"]

        def span_at(text, y, dx=6):
            c = [s for s in SP if s["text"].strip() == text and abs(s["origin"][1] - y) < dx]
            return c[0] if c else None

        qty_right = span_at("1", y_row1)["bbox"][2]
        charges_right = span_at("53.10", y_row1)["bbox"][2]
        credit_right = span_at("53.10", y_mc)["bbox"][2]
        RE = charges_right
        bal = find("Balance"); y_bal = bal["origin"][1]
        vb = find("VAT Breakdown"); y_vb = vb["origin"][1]; x_vb = vb["origin"][0]
        sz_mini = vb["size"]; bd_mini = "Bold" in vb["font"]
        na_s = span_near("Net Amount", y_vb) or vb
        vat_s = span_near("VAT", y_vb) or vb
        x_na = na_s["origin"][0]; x_vat = vat_s["origin"][0]
        y_v20 = find("VAT 20%")["origin"][1]
        y_v4 = find("VAT 4%")["origin"][1]
        vtot = find("TOTAL GBP"); y_vtot = vtot["origin"][1]
        na_right = span_at("44.25", y_v20)["bbox"][2]
        vat_right = span_at("8.85", y_v20)["bbox"][2]
        tot = find("Total"); sz_tot = tot["size"]; bd_tot = "Bold" in tot["font"]

        lr_bal, vr_bal, sz_b, bd_b = split_row(y_bal)
        ys_sub = [s["origin"][1] for s in SP if s["bbox"][0] > 250 and y_bal +
