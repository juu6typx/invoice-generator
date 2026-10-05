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
inv = c2.text_input("Invoice Date", "02.09.2026")
arr = c2.text_input("Arrival", "27.08.2026")
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
        ROW_DATES = [(_a + timedelta(days=i)).strftime("%d.%m.%y") for i in range(1, _nights + 1)]
        CHARGE = "%.2f" % CHARGE_F
        CREDIT_TOTAL = "%.2f" % (CHARGE_F * _nights)
        NET_TOTAL = "%.2f" % round(CHARGE_F * _nights / 1.2, 2)
        VAT_20 = "%.2f" % round(CHARGE_F * _nights - CHARGE_F * _nights / 1.2, 2)

        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page = doc[0]
        SP = [s for b in page.get_text("dict")["blocks"] if b.get("type") == 0 for l in b["lines"] for s in l["spans"]]

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

        def replace_exact(old, new, **kw):
            s = find(old, **kw)
            if not s: return
            r = fitz.Rect(s["bbox"])
            page.draw_rect(r + (-1.5, -1.5, 1.5, 1.5), color=None, fill=(1, 1, 1))
            draw(new, s["origin"][1], bold=("Bold" in s["font"]), x=s["origin"][0], size=s["size"])

        for s in list(SP):
            if "Luke Moore" in s["text"] and "Guest" not in s["text"]:
                r = fitz.Rect(s["bbox"])
                page.draw_rect(r + (-1.5, -1.5, 1.5, 1.5), color=None, fill=(1, 1, 1))
                draw(name, s["origin"][1], bold=("Bold" in s["font"]), x=s["origin"][0], size=s["size"])

        addr = find("airpoint") or find("skypark") or find("733")
        brl = find("Bristol")
        gb = find("Great Britain")
        if addr:
            g = (brl["origin"][1] - addr["origin"][1]) if brl else 11.0
            x0 = addr["bbox"][0]
            x1 = max(addr["bbox"][2], brl["bbox"][2] if brl else 0, gb["bbox"][2] if gb else 0) + 2
            page.draw_rect(fitz.Rect(x0 - 2, addr["origin"][1] - 10, x1, addr["origin"][1] + 3 * g + 4), color=None, fill=(1, 1, 1))
            draw(a1, addr["origin"][1], x=x0, size=addr["size"])
            draw(a2, addr["origin"][1] + g, x=x0, size=addr["size"])
            draw(a3, addr["origin"][1] + 2 * g, x=x0, size=addr["size"])
            draw(a4, addr["origin"][1] + 3 * g, x=x0, size=addr["size"])

        replace_exact("27.03.2026", inv, x_min=300)
        replace_exact("27.03.2026", dep, x_max=300)
        replace_exact("26.03.2026", arr)

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
        ys_sub = [s["origin"][1] for s in SP if s["bbox"][0] > 250 and y_bal + 4 < s["origin"][1] < y_vb]
        y_tiv = min(ys_sub); y_net = max(ys_sub)
        lr_tiv, vr_tiv, _, _ = split_row(y_tiv)
        lr_net, vr_net, _, _ = split_row(y_net)

        T_left, T_right = grey_extent(y_hdr - 1, y_hdr + 3)
        if T_left is None: T_left, T_right = x_date - 6, credit_right + 6
        M_left, M_right = grey_extent(y_vb - 7, y_vb - 4)
        if M_left is None: M_left, M_right = x_vb - 6, vat_right + 6

        dmini = RE - vat_right
        x_vb2 = x_vb + dmini
        x_na2 = x_na + dmini
        na_right2 = na_right + dmini
        vat_right2 = RE
        M_left2 = x_vb2 - (x_vb - M_left)
        M_right2 = RE + 15
        lb_bal = (lr_bal if lr_bal else RE - 46) + (RE - (vr_bal or RE))
        lb_tiv = (lr_tiv if lr_tiv else RE - 46) + (RE - (vr_tiv or RE))
        lb_net = (lr_net if lr_net else RE - 46) + (RE - (vr_net or RE))

        pix = page.get_pixmap(dpi=72, clip=fitz.Rect(x_vb, y_vb - 6, x_vb + 6, y_vb - 4))
        arrpx = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
        med = np.median(arrpx.reshape(-1, 3), axis=0) / 255.0
        grey = tuple(round(float(v), 3) for v in med)
        gsp = [s for s in SP if "The hotel," in s["text"]]
        gdpr_top = gsp[0]["bbox"][1] if gsp else 10 ** 4
        bottom = min(y_vtot + 8, gdpr_top - 4)

        page.draw_rect(fitz.Rect(0, y_hdr - 12, page.rect.width, bottom), color=None, fill=(1, 1, 1))

        y = y_hdr
        page.draw_rect(fitz.Rect(T_left, y - 8, T_right, y + 3), color=None, fill=grey)
        page.draw_line((T_left, y - 9), (T_right, y - 9), color=(0, 0, 0), width=0.7)
        page.draw_line((T_left, y + 4), (T_right, y + 4), color=(0, 0, 0), width=0.7)
        for label in ("Date", "Description", "Qty.", "Charges", "Credit"):
            draw(label, y, bold=bd_hdr, x=hdr[label]["origin"][0], size=sz_hdr)
        y += row_h
        for d in ROW_DATES:
            draw(d, y, x=x_date, size=sz_row)
            draw("Accommodation", y, x=x_desc, size=sz_row)
            draw("1", y, right=qty_right, size=sz_row)
            draw(CHARGE, y, right=charges_right, size=sz_row)
            y += row_h
        draw("Mastercard", y, x=x_desc, size=sz_row)
        draw("1", y, right=qty_right, size=sz_row)
        draw(CREDIT_TOTAL, y, right=credit_right, size=sz_row)
        y += row_h * 0.8
        draw("XXXXXXXXXXXX3724 XX/XX", y, x=x_desc, size=sz_row)
        y += row_h * 1.2
        y_totN = y
        page.draw_line((T_left, y_totN - 9), (T_right, y_totN - 9), color=(0, 0, 0), width=0.7)
        page.draw_rect(fitz.Rect(T_left, y_totN - 8, T_right, y_totN + 3), color=None, fill=grey)
        page.draw_line((T_left, y_totN + 4), (T_right, y_totN + 4), color=(0, 0, 0), width=0.7)
        draw("Total", y_totN, bold=bd_tot, x=x_date, size=sz_tot)
        draw(CREDIT_TOTAL, y_totN, bold=bd_tot, right=charges_right, size=sz_tot)
        draw(CREDIT_TOTAL, y_totN, bold=bd_tot, right=credit_right, size=sz_tot)
        y_totN += row_h
        draw("Balance GBP", y_totN, bold=bd_b, right=lb_bal, size=sz_b)
        draw("0.00", y_totN, bold=bd_b, right=RE, size=sz_b)
        delta = y_totN - y_bal

        draw("Total Including VAT GBP", y_tiv + delta, bold=bd_b, right=lb_tiv, size=sz_b)
        draw(CREDIT_TOTAL, y_tiv + delta, bold=bd_b, right=RE, size=sz_b)
        draw("Net Amount GBP", y_net + delta, bold=bd_b, right=lb_net, size=sz_b)
        draw(NET_TOTAL, y_net + delta, bold=bd_b, right=RE, size=sz_b)

        yv = y_vb + delta
        page.draw_rect(fitz.Rect(M_left2, yv - 7, M_right2, yv + 2), color=None, fill=grey)
        draw("VAT Breakdown", yv, bold=bd_mini, x=x_vb2, size=sz_mini)
        draw("Net Amount", yv, bold=bd_mini, x=x_na2, size=sz_mini)
        draw("VAT", yv, bold=bd_mini, x=x_vat + dmini, size=sz_mini)
        yv = y_v20 + delta
        draw("VAT 20%", yv, bold=bd_mini, x=x_vb2, size=sz_mini)
        draw(NET_TOTAL, yv, bold=bd_mini, right=na_right2, size=sz_mini)
        draw(VAT_20, yv, bold=bd_mini, right=vat_right2, size=sz_mini)
        yv = y_v4 + delta
        draw("VAT 4%", yv, bold=bd_mini, x=x_vb2, size=sz_mini)
        draw("0.00", yv, bold=bd_mini, right=na_right2, size=sz_mini)
        draw("0.00", yv, bold=bd_mini, right=vat_right2, size=sz_mini)
        yv = y_vtot + delta
        page.draw_line((M_left2, yv - sz_mini - 1), (M_right2, yv - sz_mini - 1), color=(0, 0, 0), width=0.7)
        draw("TOTAL GBP", yv, bold=bd_mini, x=x_vb2, size=sz_mini)
        draw(VAT_20, yv, bold=bd_mini, right=vat_right2, size=sz_mini)
        page.draw_line((M_left2, yv + 2), (M_right2, yv + 2), color=(0, 0, 0), width=0.7)

        out_bytes = io.BytesIO()
        doc.save(out_bytes)
        doc.close()
        st.success("Invoice Generated Successfully!")
        st.download_button("📥 Download Amended PDF", out_bytes.getvalue(),
                           file_name="Hotel_Invoice_amended.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Error: {e}")
