import streamlit as st
import fitz
import numpy as np
from datetime import datetime, timedelta
import io
import re

st.set_page_config(page_title="Invoice Gen", layout="centered")
st.title(" Hotel Invoice 1:1 Generator")

uploaded_file = st.file_uploader("1. Upload your base test.pdf", type=["pdf"])

st.subheader(" test.pdf", type=["pdf"])

st.subheader("2. Enter Details")
c1, c2 = st.columns(2)
name = c1.text_input("Guest Name", "Mr. Luke Moore")
c1, c2 =_input("Guest Name", "Mr. Luke Moore")
 st.columns(2)
name = c1.text_input("Guest Name", "Mr. Luke Moore")
a1 = c1.text_input("Address line 1", "438 Airpoint")
a2 = c1.text_input("Address line 2", "Skypark Road")
a3 = c1.text_input("Address line 3", "Bristol")
a4 = c1.text_input("Address line 4",a1 = c1.text_input("Address line 1", "438 Airpoint")
a2 = c1.text_input("Address line 2", "Skypark Road")
a3 = c1.text_input("Address line 3", "Bristol")
a4 = c1.text_input("Address line 4", "BS3 3NL")
ino = c2.text_input("Invoice No.", "26683 "BS3 3NL")
ino = c2.text_input("Invoice No.", "26683")
ref = c2.text_input("Reference No. (11 digits, blank = keep)", "")
")
ref = c2.text_input("Reference Noinv = c2.text_input("Invoice Date", "0. (11 digits, blank = keep)", "")
2.09.2026")
arrinv = c2.text_input("Invoice Date", "02.09.2026")
arr = c2.text_input("Arrival", "28 = c2.text_input("Arrival", "28.08.2026")
dep =.08.2026")
dep = c2.text_input("Departure", "02.09.2026")
chg = c c2.text_input("Departure", "02.09.2026")
chg = c2.text_input("Nightly Charge", "1342.text_input("Nightly Charge", "134.56")

if st.button("Generate Invoice",.56")

if st.button("Generate Invoice", type="primary"):
    if not uploaded_file:
 type="primary"):
    if not uploaded_file:
        st.error("Please upload the base PDF first!")
        st.error("Please upload the base PDF first!")
        st.stop()
    try:
        CHARGE        st.stop()
    try:
        CHARGE_F = float(chg)
        _a = datetime.strptime(arr, "%d.%m.%Y")
        _d = datetime.strptime(dep, "%d.%m.%Y")
        _nights = max((_d -_F = float(chg)
        _a = datetime _a).days, 1)
        ROW_D.strptime(arr, "%d.%m.%Y")
        _d = datetime.strptime(dep, "%d.%m.%Y")
        _nights = max((_d - _a).days, 1)
        ROW_DATES = [(_a + timedelta(days=i)).strftime("%ATES = [(_a + timedelta(days=i)).strftime("%d.%m.%y") for i in range(_nd.%m.%y") for i in range(_nights)]
        CHARGE = "%.2f" %ights)]
        CHARGE = "%.2f" % CHARGE_F
        CREDIT_TOTAL = "%.2f CHARGE_F
        CREDIT_TOTAL = "%.2f" % (CHARGE_F * _nights)
        NET_TOTAL = "%.2f" % round(CHARGE" % (CHARGE_F * _nights)
_F * _nights / 1.2,         NET_TOTAL = "%.2f" % round(CHARGE2)
        VAT_20 = "%.2f_F * _nights / 1.2, 2)
        VAT_20 = "%.2f" % round(CHARGE_F * _nights - CH" % round(CHARGE_F * _nights - CHARGE_F * _nights / 1.2, 2)

        doc = fitz.open(stream=ARGE_F * _nights / 1.2, 2)

        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page =uploaded_file.read(), filetype="pdf")
        page = doc[0]
        SP = [s for b doc[0]
        SP = [s for b in page.get_text("dict")["blocks"] if b in page.get_text("dict")["blocks"] if b.get("type") == 0 for l in b[".get("type") == 0 for l in b["lines"] for s in l["spans"]]

        def find(old, x_min=None, x_max=None):
            c = [s for s in SP if slines"] for s in l["spans"]]

        def find(old, x_min=None, x_max=None):
            c = [s for s in SP if s["text"].strip() == old]
            if["text"].strip() == old]
            if not c: c = [s for s in SP if not c: c = [s for s in SP if s["text"].strip().startswith(old)]
            if s["text"].strip().startswith(old)]
            if not c: c = [s for s in SP if not c: c = [s for s in SP if old.lower() in s["text"].lower()]
            old.lower() in s["text"].lower()]
            if x_min is not None: c = [s for if x_min is not None: c = [s for s in c if s["bbox"][0] >= x_min]
            if x_max is not None: c s in c if s["bbox"][0] >= x_min]
            if x_max is not None: c = [s for s in c if s["bbox"][ = [s for s in c if s["bbox"][0] <= x_max]
            return c[00] <= x_max]
            return c[0] if c else None

        def span_near(text,] if c else None

        def span_near(text, y, dx=4):
            c = [s y, dx=4):
            c = [s for s in SP if s["text"].strip() == for s in SP if s["text"].strip() == text and abs(s["origin"][1] - y) text and abs(s["origin"][1] - y) < dx]
            if not c: c = [s for s in SP if s["text"].strip(). < dx]
            if not c: c = [s for s in SP if s["text"].strip().startswith(text) and abs(s["origin"][1] -startswith(text) and abs(s["origin"][1] - y) < dx]
            return c[0] if c else None

        def span_at(text, y y) < dx]
            return c[0] if c else None

        def span_at(text, y, dx=6):
            c = [s for, dx=6):
            c = [s for s in SP if s["text"].strip() == text s in SP if s["text"].strip() == text and abs(s["origin"][1] - y)  and abs(s["origin"][1] - y) < dx]
            return c[0] if c else None

        def split_row(y):
            rs = [s for s in SP if abs(s["origin"][1] - y) < 3 and s["bbox"][0] > 250]
            val = None; lab = []
            for s in rs:
                t = s["text"].strip()
                if val is None and t and all(c in "< dx]
            return c[0] if c else None

        def split_row(y):
            rs = [s for s in SP if abs(s["origin"][1] - y) < 3 and s["bbox"][0] > 250]
            val = None; lab = []
            for s in rs:
                t = s["text"].strip()
                if val is None and t and all(c in "0123456789.," for c in t):
                    val = s
               0123456789.," for c in t):
                    val = s
                else:
                    lab.append(s)
            lr = else:
                    lab.append(s)
            lr = max([s["bbox"][2] for s in lab max([s["bbox"][2] for s in lab], default=None)
            vr = val["bbox"][2] if val else None
            ref = lab[], default=None)
            vr = val["bbox"][2] if val else None
            ref = lab[0] if lab else val
            return lr, vr, (ref["size"] if ref else 9),0] if lab else val
            return lr, vr, (ref["size"] if ref else 9), ("Bold" in ref["font"] if ref else False ("Bold" in ref["font"] if ref else False)

        def grey_extent(y0, y1):)

        def grey_extent(y0, y1):
            pix = page.get_pixmap(dpi=7
            pix = page.get_pixmap(dpi=72, clip=fitz.Rect(0, y02, clip=fitz.Rect(0, y0, page.rect.width, y1))
            a = np.frombuffer(pix.samples, np.uint8, page.rect.width, y1))
           ).reshape(pix.height, pix.width, pix.n) a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].mean(axis=2)
           [:, :, :3].mean(axis=2)
            m = (a > 150) & (a < 235)
            cols = np m = (a > 150) & (.nonzero(m.any(axis=0))[0]
            if len(cols) == 0: return None, Nonea < 235)
            cols = np
            return float(cols.min()), float(cols.max() + 1)

        NAMES = [(s["origin"][.nonzero(m.any(axis=0))[0]
            if len(cols) == 0: return None, None
            return float(cols.min()), float(cols.max() + 1)

        NAMES = [(s["origin"][0], s["origin"][1], s["size"],0], s["origin"][1], s["size"], "Bold" in s["font"]) for s in SP "Bold" in s["font"]) for s in SP if "Luke Moore" in s["text"] and " if "Luke Moore" in s["text"] and "Guest" not in s["text"]]
        addr =Guest" not in s["text"]]
        addr = find("airpoint") or find("skypark") or find("733")
        brl = find("airpoint") or find("skypark") or find("733")
        brl = find("Bristol"); gb = find("Great Britain") find("Bristol"); gb = find("Great Britain")
        s_d = find("27.03.2026", x_min=300
        s_d = find("27.03.2026", x_min=300); s_dp = find("27.03.); s_dp = find("27.03.2026", x_max=300);2026", x_max=300); s_ar = find("26.03.2 s_ar = find("26.03.2026")
        s_in = find("2026")
        s_in = find("26683")
        
        # Find 16683")
        
        # Find 11-digit reference number
        s_ref = None
1-digit reference number
        s_ref = None
        if ref:
            ref_candidates = [s for s in SP if re.match(r"^\d{1        if ref:
            ref_candidates = [s for s in SP if re.match(r"^\d{11}$", s["text"].strip())]
           1}$", s["text"].strip())]
            if ref_candidates:
                # Look for reference in if ref_candidates:
                # Look for reference in the header area (above the table)
                row the header area (above the table)
                row1 = find("26.03.26")
                if row1:
                    header1 = find("26.03.26")
                if row1:
                    header_y = row1["origin"][1]
                    top_y = row1["origin"][1]
                    top_refs = [s for s in ref_candidates_refs = [s for s in ref_candidates if s["origin"][1] < header_y]
                    if top_refs:
                        s_ref = sorted(top_refs, key=lambda s: s["origin"][1])[0]
        
        row1 = find("26.03.26")
        y_row1 = row1["origin"][1]; x_date = row if s["origin"][1] < header_y]
                    if top_refs:
                        s_ref = sorted(top_refs, key=lambda s: s["origin"][1])[0]
        
        row1 = find("26.03.26")
        y_row1 = row1["origin"][1]; x_date = row1["origin"][0]; sz_row = row1["1["origin"][0]; sz_row = row1["size"]
        x_desc = find("Accommodationsize"]
        x_desc = find("Accommodation")["origin"][0]
        mc = find("Mastercard"); y_mc = mc["origin"][1]")["origin"][0]
        mc = find("Mastercard"); y_mc = mc["origin"][1]
        row_h = y_mc - y_row1
        hdr = {l: find(l) for l in
        row_h = y_mc - y_row1
        hdr = {l: find(l) for l in ("Description", "Qty.", "Charges", "Credit ("Description", "Qty.", "Charges", "Credit")}
        hdr["Date"] = min([s for")}
        hdr["Date"] = min([s for s in SP if s["text"].strip() == " s in SP if s["text"].strip() == "Date"], key=lambda s: abs(s["origin"][Date"], key=lambda s: abs(s["origin"][1] - (y_row1 - 10)))
        y_hdr = hdr["Date"]["origin"][11] - (y_row1 - 10)))
        y_hdr = hdr["Date"]["origin"][1]; sz_hdr = hdr["Date"]["size"]; bd_hdr]; sz_hdr = hdr["Date"]["size"]; bd_hdr = "Bold" in hdr["Date"]["font"]
 = "Bold" in hdr["Date"]["font"]
        qty_right = span_at("1", y_row1        qty_right = span_at("1", y_row1)["bbox"][2]
        charges_right = span_at("53.10", y_row1)["bbox)["bbox"][2]
        charges_right = span_at("53.10", y_row1)["bbox"][2]
        credit_right = span_at("5"][2]
        credit_right = span_at("53.10", y_mc)["bbox"][2]3.10", y_mc)["bbox"][2]
        RE = charges_right
        bal = find("
        RE = charges_right
        bal = find("Balance"); y_bal = bal["origin"][1]
Balance"); y_bal = bal["origin"][1]
        vb = find("VAT Breakdown"); y_vb = vb["origin"][1]; x_vb =        vb = find("VAT Breakdown"); y_vb = vb["origin"][1]; x_vb = vb["origin"][0]
        sz_mini = vb["size"]; bd_mini = "Bold" in vb["font"]
        x_na = (span_near("Net Amount", y_vb) or vb)["origin"][0]
        x_vat = (span_near("VAT", y_vb) or vb)["origin"][0]
        y_v20 = find("VAT 20%")["origin"][1]
        y_v4 = find("VAT 4%")["origin"][1]
        y_vtot = find("TOTAL GBP")["origin"][1]
        na_right = span_at("44.25", y_v20)["bbox"][2]
        vat_right = span_at("8.85", y_v20)["bbox"][2]
        tot = find("Total"); sz_tot = tot["size"]; bd_tot = "Bold" in tot["font"]
        lr_bal, vr_bal, sz_b, bd_b = split_row(y_bal)
        ys_sub = [s["origin"][1] for s in SP if s["bbox"][0] > 250 and y_bal +  vb["origin"][0]
        sz_mini = vb["size"]; bd_mini = "Bold" in vb["font"]
        x_na = (span_near("Net Amount", y_vb) or vb)["origin"][0]
        x_vat = (span_near("VAT", y_vb) or vb)["origin"][0]
        y_v20 = find("VAT 20%")["origin"][1]
        y_v4 = find("VAT 4%")["origin"][1]
        y_vtot = find("TOTAL GBP")["origin"][1]
        na_right = span_at("44.25", y_v20)["bbox"][2]
        vat_right = span_at("8.85", y_v20)["bbox"][2]
        tot = find("Total"); sz_tot = tot["size"]; bd_tot = "Bold" in tot["font"]
        lr_bal4 < s["origin"][1] < y_vb, vr_bal, sz_b, bd_b = split_row(y_bal)
        ys_sub = [s["origin"][1] for s in SP if s["bbox"][0] > 250 and y_bal + 4 < s["origin"][1] < y_vb]
        if len(ys_sub) < 2]
        if len(ys_sub) < 2: ys_sub = [y_bal + 12,: ys_sub = [y_bal + 12, y_bal + 24]
        y_tiv y_bal + 24]
        y_tiv = min(ys_sub); y_net = max(ys = min(ys_sub); y_net = max(ys_sub)
        lr_tiv, vr_tiv,_sub)
        lr_tiv, vr_tiv, _, _ = split_row(y_tiv)
        lr _, _ = split_row(y_tiv)
        lr_net, vr_net, _, _ = split_row(y_net_net, vr_net, _, _ = split_row(y_net)
        T_left, T_right = grey_extent(y)
        T_left, T_right = grey_extent(y_hdr - 1, y_hdr + 3)_hdr - 1, y_hdr + 3)
        if T_left is None: T_left, T
        if T_left is None: T_left, T_right = x_date - 6, credit_right + _right = x_date - 6, credit_right + 6
        M_left, M_right = grey_extent(y6
        M_left, M_right = grey_extent(y_vb - 7, y_vb - 4_vb - 7, y_vb - 4)
        if M_left is None: M_left,)
        if M_left is None: M_left, M_right = x_vb - 6, vat_right M_right = x_vb - 6, vat_right + 6
        dmini = RE - vat_right + 6
        dmini = RE - vat_right
        x_vb2 = x_vb + d
        x_vb2 = x_vb + dmini; x_na2 = x_na + dmini;mini; x_na2 = x_na + dmini; x_vat2 = x_vat + dmini
        na_right2 = na_right + dmini; vat x_vat2 = x_vat + dmini
        na_right2 = na_right + dmini; vat_right2 = RE
        M_left2 = x_v_right2 = RE
        M_left2 = x_vb2 - (x_vb - M_left); Mb2 - (x_vb - M_left); M_right2 = RE + 15
        lb_bal_right2 = RE + 15
        lb_bal = (lr_bal or RE - 46) + (RE - (vr_bal or RE))
        lb = (lr_bal or RE - 46) + (RE - (vr_bal or RE))
        lb_tiv = (lr_tiv or RE - 46) + (RE - (vr_tiv or RE))
        lb_net = (lr_net or RE - 46) + (RE - (vr_net or RE))
        pix = page.get_pixmap(dpi=72, clip=fitz.Rect(x_vb, y_vb - 6, x_vb + 6, y_vb - 4))
        ap = np.frombuffer(pix.samples, np.uint8_tiv = (lr_tiv or RE - 4).reshape(pix.height, pix.width, pix.n)6) + (RE - (vr_tiv or RE))
        lb_net = (lr_net or RE - 46) + (RE - (vr_net or RE))
        pix = page.get_pixmap(dpi=72, clip=fitz.Rect(x_vb, y_vb - 6, x_vb + 6, y_vb - 4))
        ap = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
        grey = tuple(round(float[:, :, :3]
        grey = tuple(round(float(v), 3) for v in np.median(ap.reshape(-1, 3), axis=0) / (v), 3) for v in np.median(ap.reshape(-1, 3), axis=0) / 255.0)
        gsp = [255.0)
        gsp = [s for s in SP if "The hotel," in ss for s in SP if "The hotel," in s["text"]]
        gdpr_top = gsp[["text"]]
        gdpr_top = gsp[0]["bbox"][1] if gsp else 10]["bbox"][1] if gsp else 10 ** 4
        bottom = min(y_vtot0 ** 4
        bottom = min(y_vtot + 8, gdpr_top - 4)

 + 8, gdpr_top - 4)

        RED = []
        for (nx, ny,        RED = []
        for (nx, ny, ns, nb) in NAMES:
            RED.append(fitz.Rect(nx - 2, ny - ns, nx + 130, ny + 4))
 ns, nb) in NAMES:
            RED.append(fitz.Rect(nx - 2, ny - ns, nx + 130, ny + 4))
        if addr:
            g = (brl["        if addr:
            g = (brl["origin"][1] - addr["origin"][1]) iforigin"][1] - addr["origin"][1]) if brl else 11.0
            ax0 brl else 11.0
            ax0 = addr["bbox"][0]
            ax1 = = addr["bbox"][0]
            ax1 = max(addr["bbox"][2], brl["bbox"][ max(addr["bbox"][2], brl["bbox"][2] if brl else 0, gb["bbox2] if brl else 0, gb["bbox"][2] if gb else 0) + 2"][2] if gb else 0) + 2
            RED.append(fitz.Rect(ax0 - 2
            RED.append(fitz.Rect(ax0 - 2, addr["origin"][1] - 10,, addr["origin"][1] - 10, ax1, addr["origin"][1] + 3 ax1, addr["origin"][1] + 3 * g + 4))
        for s in ( * g + 4))
        for s in (s_d, s_dp, s_ar):
            if s: RED.append(fitz.Rect(s["bbox"]) +s_d, s_dp, s_ar):
            if s: RED.append(fitz.Rect(s["bbox"]) + (-1.5, -1.5, 1.5, 1.5))
        if s (-1.5, -1.5, 1.5, 1.5))
        if s_in and ino != "26683":_in and ino != "26683":
            RED.append(fitz.Rect(s_in["bbox"])
            RED.append(fitz.Rect(s_in["bbox"]) + (-1.5, -1.5,  + (-1.5, -1.5, 1.5, 1.5))
        if1.5, 1.5))
        if s_ref:
            RED.append(fitz.Rect(s_ref s_ref:
            RED.append(fitz.Rect(s_ref["bbox"]) + (-1.5, -1.["bbox"]) + (-1.5, -1.5, 1.5, 1.5))5, 1.5, 1.5))
        RED.append(fitz.Rect(0, y_hdr
        RED.append(fitz.Rect(0, y_hdr - 12, page.rect.width, bottom))
 - 12, page.rect.width, bottom))
        for r in RED:
            page.add_redact        for r in RED:
            page.add_redact_annot(r, fill=(1, 1, _annot(r, fill=(1, 1, 1))
        page.apply_redactions(images=fitz1))
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

        def draw.PDF_REDACT_IMAGE_NONE)

        def draw(text, y, bold=False, x=None, right=None, size=9):
            fname = "hebo" if bold else "helv"
            f = fitz.Font(fname)
            w = f.text_length(text, y, bold=False, x=None, right=None, size=9):
            fname = "hebo" if bold else "helv"
            f = fitz.Font(fname)
            w = f.text_length(text, fontsize=size)
            xx = (right -(text, fontsize=size)
            xx = (right - w) if right is not None else x
            page w) if right is not None else x
            page.insert_text((xx, y), text, fontname=f.insert_text((xx, y), text, fontname=fname, fontsize=size, color=(0, 0, 0))

        for (nx, ny, nsname, fontsize=size, color=(0, 0, 0))

        for (nx, ny, ns, nb) in NAMES:
            draw(name, ny, nb) in NAMES:
            draw(name, ny, bold=nb, x=nx, size=ns, bold=nb, x=nx, size=ns)
        if addr:
            draw(a1,)
        if addr:
            draw(a1, addr["origin"][1], x=ax0, addr["origin"][1], x=ax0, size=addr["size"])
            draw(a2, size=addr["size"])
            draw(a2, addr["origin"][1] + g, x=ax0, size=addr["size"])
            draw(a3, addr["origin"][1] + 2 * g addr["origin"][1] + g, x=ax0, size=addr["size"])
            draw(a3, addr["origin"][1] + 2 * g, x=ax0, size=addr["size"])
, x=ax0, size=addr["size"])
            draw(a4, addr["origin"][1] +            draw(a4, addr["origin"][1] + 3 * g, x=ax0, size=addr 3 * g, x=ax0, size=addr["size"])
        if s_d: draw(inv["size"])
        if s_d: draw(inv, s_d["origin"][1], x=s_d[", s_d["origin"][1], x=s_d["origin"][0], size=s_d["size"])
       origin"][0], size=s_d["size"])
        if s_dp: draw(dep, s_dp["origin"][ if s_dp: draw(dep, s_dp["origin"][1], x=s_dp["origin"][0], size=s1], x=s_dp["origin"][0], size=s_dp["size"])
        if s_ar: draw(arr_dp["size"])
        if s_ar: draw(arr, s_ar["origin"][1], x=s_ar["origin"][0], size=s_ar["size"])
        if s_in and ino != "26683": draw(ino, s_in["origin"][1], x=s_in["origin"][0], size=s, s_ar["origin"][1], x=s_ar["origin"][0], size=s_ar["size"])
        if s_in and ino != "26683": draw(ino, s_in["origin"][1], x=s_in["origin"][0], size=s_in["size"])
        if s_ref and ref:_in["size"])
        if s_ref and ref: draw(ref, s_ref["origin"][1], x=s draw(ref, s_ref["origin"][1], x=s_ref["origin"][0], size=s_ref["size"])_ref["origin"][0], size=s_ref["size"])

        y = y_hdr
        page.draw_rect(fitz.Rect(T_left, y - 8, T_right

        y = y_hdr
        page.draw_rect(fitz.Rect(T_left, y - 8, T_right, y + 3), color=None, fill, y + 3), color=None, fill=grey)
        page.draw_line((T_left,=grey)
        page.draw_line((T_left, y - 9), (T_right, y -  y - 9), (T_right, y - 9), color=(0, 0, 0),9), color=(0, 0, 0), width=0.7)
        page.draw_line(( width=0.7)
        page.draw_line((T_left, y + 4), (T_right,T_left, y + 4), (T_right, y + 4), color=(0, 0, y + 4), color=(0, 0, 0), width=0.7)
        for 0), width=0.7)
        for label in ("Date", "Description", "Qty.", " label in ("Date", "Description", "Qty.", "Charges", "Credit"):
            draw(label, yCharges", "Credit"):
            draw(label, y, bold=bd_hdr, x=hdr[label]["origin, bold=bd_hdr, x=hdr[label]["origin"][0], size=sz_hdr)
        y +="][0], size=sz_hdr)
        y += row_h
        for dte in ROW_DATES: row_h
        for dte in ROW_DATES:
            draw(dte, y, x=x_date,
            draw(dte, y, x=x_date, size=sz_row)
            draw("Accommodation size=sz_row)
            draw("Accommodation", y, x=x_desc, size=sz_row)", y, x=x_desc, size=sz_row)
            draw("1", y, right=qty_right
            draw("1", y, right=qty_right, size=sz_row)
            draw(CHARGE,, size=sz_row)
            draw(CHARGE, y, right=charges_right, size=sz_row) y, right=charges_right, size=sz_row)
            y += row_h
        draw("Mastercard
            y += row_h
        draw("Mastercard", y, x=x_desc, size=sz_row)", y, x=x_desc, size=sz_row)
        draw("1", y, right=qty_right
        draw("1", y, right=qty_right, size=sz_row)
        draw(CREDIT_TOTAL, size=sz_row)
        draw(CREDIT_TOTAL, y, right=credit_right, size=sz_row, y, right=credit_right, size=sz_row)
        y += row_h * 0.8)
        y += row_h * 0.8
        draw("XXXXXXXXXXXX3724 XX/
        draw("XXXXXXXXXXXX3724 XX/XX", y, x=x_desc, size=sz_rowXX", y, x=x_desc, size=sz_row)
        y += row_h * 1.2)
        y += row_h * 1.2
        yT = y
        page.draw_line((T_left, yT - 9), (T_right
        yT = y
        page.draw_line((T_left, yT - 9), (T_right, yT - 9), color=(0,, yT - 9), color=(0, 0, 0), width=0.7) 0, 0), width=0.7)
        page.draw_rect(fitz.Rect(T_left, y
        page.draw_rect(fitz.Rect(T_left, yT - 8, T_right, yT + T - 8, T_right, yT + 3), color=None, fill=grey)
        page.draw_line((T_left, yT + 4), (T_right, yT + 4), color=(3), color=None, fill=grey)
        page.draw_line((T_left, yT + 4), (T_right, yT + 4), color=(0, 0, 0), width=0.0, 0, 0), width=0.7)
        draw("Total", yT, bold7)
        draw("Total", yT, bold=bd_tot, x=x_date, size=sz_tot=bd_tot, x=x_date, size=sz_tot)
        draw(CREDIT_TOTAL, yT, bold)
        draw(CREDIT_TOTAL, yT, bold=bd_tot, right=charges_right, size=sz_tot)
        draw(CREDIT_TOTAL, yT, bold=bd_tot, right=credit_right, size=s=bd_tot, right=charges_right, size=sz_tot)
        draw(CREDIT_TOTAL, yT, bold=bd_tot, right=credit_right, size=sz_tot)
        yT += row_h
        draw("Balance GBP", yT, bold=bd_b, right=lb_bal, size=sz_b)
        draw("0.00", yT, bold=bd_b, right=RE, size=sz_b)
        delta = yT - y_bal
        draw("Total Including VAT GBP", y_tiv + delta, bold=bd_b, right=lb_tiv, size=sz_b)
        draw(CREDIT_TOTAL, y_tiv + delta, bold=bd_b, right=RE, size=sz_b)
        draw("Net Amount GBP", y_net + delta, bold=bdz_tot)
        yT += row_h
        draw("Balance GBP", yT, bold=bd_b, right=lb_bal, size=sz_b)
        draw("0.00", yT, bold=bd_b, right=RE, size=sz_b)
        delta = yT - y_bal
        draw("Total Including VAT GBP", y_tiv + delta, bold=bd_b, right=lb_tiv, size=sz_b)
        draw(CREDIT_TOTAL, y_tiv + delta, bold=bd_b, right=RE, size=sz_b)
        draw("Net Amount GBP", y_net + delta, bold=bd_b, right=lb_net, size=sz_b)_b, right=lb_net, size=sz_b)
        draw(NET_TOTAL, y_net + delta,
        draw(NET_TOTAL, y_net + delta, bold=bd_b, right=RE, size=sz bold=bd_b, right=RE, size=sz_b)
        yv = y_vb + delta_b)
        yv = y_vb + delta
        page.draw_rect(fitz.Rect(M_left2,
        page.draw_rect(fitz.Rect(M_left2, yv - 7, M_right2, yv yv - 7, M_right2, yv + 2), color=None, fill=grey)
 + 2), color=None, fill=grey)
        draw("VAT Breakdown", yv, bold        draw("VAT Breakdown", yv, bold=bd_mini, x=x_vb2, size=s=bd_mini, x=x_vb2, size=sz_mini)
        draw("Net Amount", yvz_mini)
        draw("Net Amount", yv, bold=bd_mini, x=x_na2, size, bold=bd_mini, x=x_na2, size=sz_mini)
        draw("VAT", yv, bold=bd_mini, x=x_vat2=sz_mini)
        draw("VAT", y, size=sz_mini)
        yv = yv, bold=bd_mini, x=x_vat2, size=sz_mini)
        yv = y_v20 + delta
        draw("VAT _v20 + delta
        draw("VAT 20%", yv, bold=bd_mini, x20%", yv, bold=bd_mini, x=x_vb2, size=sz_mini)
       =x_vb2, size=sz_mini)
        draw(NET_TOTAL, yv, bold=bd_mini draw(NET_TOTAL, yv, bold=bd_mini, right=na_right2, size=sz_mini), right=na_right2, size=sz_mini)
        draw(VAT_20, yv,
        draw(VAT_20, yv, bold=bd_mini, right=vat_right2, size bold=bd_mini, right=vat_right2, size=sz_mini)
        yv = y_v4 + delta
        draw("VAT 4%", y=sz_mini)
        yv = y_v4v, bold=bd_mini, x=x_vb2 + delta
        draw("VAT 4%", yv, bold=bd_mini, x=x_vb2, size=sz_mini)
        draw("0.00", yv, bold=bd_mini, right, size=sz_mini)
        draw("0.=na_right2, size=sz_mini)
       00", yv, bold=bd_mini, right=na_right2, size=sz_mini)
        draw("0.00", yv, bold= draw("0.00", yv, bold=bd_mini, right=vat_right2, size=szbd_mini, right=vat_right2, size=sz_mini)
        yv = y_vtot + delta_mini)
        yv = y_vtot + delta
        page.draw_line((M_left2, yv
        page.draw_line((M_left2, yv - sz_mini - 1), (M_right2, - sz_mini - 1), (M_right2, yv - sz_mini - 1), color=(0, 0, 0), width=0.7 yv - sz_mini - 1), color=(0, 0, 0), width=0.7)
        draw("TOTAL GBP", yv, bold)
        draw("TOTAL GBP", yv, bold=bd_mini, x=x_vb2, size=s=bd_mini, x=x_vb2, size=sz_mini)
        draw(VAT_20,z_mini)
        draw(VAT_20, yv, bold=bd_mini, right=vat_right yv, bold=bd_mini, right=vat_right2, size=sz_mini)
        page.draw_line2, size=sz_mini)
        page.draw_line((M_left2, yv + 2), (((M_left2, yv + 2), (M_right2, yv + 2), color=(M_right2, yv + 2), color=(0, 0, 0), width=0.7)

        out = io.BytesIO()
       0, 0, 0), width=0.7)

        out = io.BytesIO()
        doc.save(out)
        doc.close()
        st doc.save(out)
        doc.close()
        st.success("Invoice Generated Successfully!")
        st.download_button.success("Invoice Generated Successfully!")
        st.download_button("📥 Download Amended PDF", out.getvalue(),("📥 Download Amended PDF", out.getvalue(), file_name="Hotel_Invoice_amended.pdf", mime=" file_name="Hotel_Invoice_amended.pdf", mime="application/pdf")
    except Exception as e:
       application/pdf")
    except Exception as e:
        st.error(f"Error: {e}")
