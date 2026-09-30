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
address = c2.text_input("Address", "438 Airpoint, Skypark Road, BS3 3NL")
inv = c1.text_input("Invoice Date", "02.09.2026")
arr = c2.text_input("Arrival", "27.08.2026")
dep = c1.text_input("Departure", "02.09.2026")
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
            c = [s for s in SP if old.lower() in s["text"].lower()]
            if x_min is not None: c = [s for s in c if s["bbox"][0] >= x_min]
            if x_max is not None: c = [s for s in c if s["bbox"][0] <= x_max]
            return c[0] if c else None

        def replace_exact(old, new, **kw):
            s = find(old, **kw)
            if not s: return
            r = fitz.Rect(s["bbox"])
            page.draw_rect(r + (-1.5, -1.5, 1.5, 1.5), color=None, fill=(1, 1, 1))
            draw(new, s["origin"][1], bold=("Bold" in s["font"]), x=s["origin"][0], size=s["size"])

        for s in list(SP):
            if "Luke Moore" in s["text"]:
                r = fitz.Rect(s["bbox"])
                page.draw_rect(r + (-1.5, -1.5, 1.5, 1.5), color=None, fill=(1, 1, 1))
                draw(name, s["origin"][1], bold=("Bold" in s["font"]), x=s["origin"][0], size=s["size"])

        addr = find("airpoint") or find("skypark") or find("733")
        if addr:
            r = fitz.Rect(addr["bbox"])
            page.draw_rect(r + (-1.5, -1.5, 1.5, 1.5), color=None, fill=(1, 1, 1))
            draw(address, addr["origin"][1], x=addr["origin"][0], size=addr["size"])
            br = find("Bristol")
            if br: page.draw_rect(fitz.Rect(br["bbox"]) + (-1.5, -1.5, 1.5, 1.5), color=None, fill=(1, 1, 1))

        replace_exact("27.03.2026", inv, x_min=300)
        replace_exact("27.03.2026", dep, x_max=300)
        replace_exact("26.03.2026", arr)

        row1 = find("26.03.26")
        y_row1 = row1["origin"][1]; x_date = row1["origin"][0]
        x_desc = find("Accommodation")["origin"][0]
        mc = find("Mastercard"); y_mc = mc["origin"][1]
        row_h = y_mc - y_row1
        hdr = {l: find(l) for l in ("Description", "Qty.", "Charges", "Credit")}
        hdr["Date"] = min([s for s in SP if "Date" in s["text"]], key=lambda s: abs(s["origin"][1] - (y_row1 - 10)))
        y_hdr = hdr["Date"]["origin"][1]

        def span_at(text, y, dx=6):
            c = [s for s in SP if text in s["text"] and abs(s["origin"][1] - y) < dx]
            return c[0] if c else None

        qty_right = span_at("1", y_row1)["bbox"][2]
        charges_right = span_at("53.10", y_row1)["bbox"][2]
        credit_right = span_at("53.10", y_mc)["bbox"][2]
        bal = find("Balance"); y_bal = bal["origin"][1]; x_bal = bal["origin"][0]
        vb = find("VAT Breakdown"); y_vb = vb["origin"][1]; x_vb = vb["origin"][0]
        x_na = find("Net Amount")["origin"][0]
        x_vat = find("VAT")["origin"][0]
        y_v20 = find("VAT 20%")["origin"][1]
        y_v4 = find("VAT 4%")["origin"][1]
        vtot = find("TOTAL GBP")
        y_vtot = vtot["origin"][1]
        na_right = span_at("44.25", y_v20)["bbox"][2]
        vat_right = span_at("8.85", y_v20)["bbox"][2]
        right_spans = sorted([s for s in SP if s["bbox"][0] > 300 and y_bal < s["origin"][1] < y_vb], key=lambda s: s["origin"][1])
        y_tiv = right_spans[0]["origin"][1]
        y_net = right_spans[-1]["origin"][1]
        R = max(s["bbox"][2] for s in right_spans if abs(s["origin"][1] - y_tiv) < 3)
        
        pix = page.get_pixmap(dpi=72, clip=fitz.Rect(x_vb, y_vb - 6, x_vb + 6, y_vb - 4))
        arrpx = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
        med = np.median(arrpx.reshape(-1, 3), axis=0) / 255.0
        grey = tuple(round(float(v), 3) for v in med)
        g = [s for s in SP if "The hotel," in s["text"]]
        gdpr_top = g[0]["bbox"][1] if g else 10 ** 4
        bottom = min(y_vtot + 8, gdpr_top - 4)

        page.draw_rect(fitz.Rect(35, y_hdr - 12, page.rect.width - 35, bottom), color=None, fill=(1, 1, 1))
        y = y_hdr
        for label in ("Date", "Description", "Qty.", "Charges", "Credit"):
            draw(label, y, bold=True, x=hdr[label]["origin"][0], size=9)
        page.draw_line((x_date - 2, y + 3), (R, y + 3), color=(0, 0, 0), width=0.7)
        y += row_h
        for d in ROW_DATES:
            draw(d, y, x=x_date, size=9)
            draw("Accommodation", y, x=x_desc, size=9)
            draw("1", y, right=qty_right, size=9)
            draw(CHARGE, y, right=charges_right, size=9)
            y += row_h
        draw("Mastercard", y, x=x_desc, size=9)
        draw("1", y, right=qty_right, size=9)
        draw(CREDIT_TOTAL, y, right=credit_right, size=9)
        y += row_h * 0.8
        draw("XXXXXXXXXXXX3724 XX/XX", y, x=x_desc, size=9)
        y += row_h * 1.2
        page.draw_line((x_date - 2, y - row_h + 4), (R, y - row_h + 4), color=(0, 0, 0), width=0.7)
        draw("Total", y, bold=True, x=x_date, size=9)
        draw(CREDIT_TOTAL, y, bold=True, right=charges_right, size=9)
        draw(CREDIT_TOTAL, y, bold=True, right=credit_right, size=9)
        page.draw_line((x_date - 2, y + 3), (R, y + 3), color=(0, 0, 0), width=0.7)
        y += row_h
        draw("Balance GBP 0.00", y, x=x_bal, size=9)
        delta = y - y_bal
        draw("Total Includin g VAT GBP " + CREDIT_TOTAL, y_tiv + delta, bold=True, right=R, size=9)
        draw("Net Amount GBP " + NET_TOTAL, y_net + delta, bold=True, right=R, size=9)
        yv = y_vb + delta
        page.draw_rect(fitz.Rect(x_vb - 4, yv - 8, R, yv + 3), color=None, fill=grey)
        draw("VAT Breakdown", yv, bold=True, x=x_vb, size=9)
        draw("Net Amount", yv, bold=True, x=x_na, size=9)
        draw("VAT", yv, bold=True, x=x_vat, size=9)
        yv = y_v20 + delta
        draw("VAT 20%", yv, x=x_vb, size=9)
        draw(NET_TOTAL, yv, right=na_right, size=9)
        draw(VAT_20, yv, right=vat_right, size=9)
        yv = y_v4 + delta
        draw("VAT 4%", yv, x=x_vb, size=9)
        draw("0.00", yv, right=na_right, size=9)
        draw("0.00", yv, right=vat_right, size=9)
        yv = y_vtot + delta
        draw("TOTAL GBP " + VAT_20, yv, bold=True, x=x_vb, size=9)
        page.draw_line((x_vb - 4, yv + 3), (R, yv + 3), color=(0, 0, 0), width=0.7)
        
        out_bytes = io.BytesIO()
        doc.save(out_bytes)
        doc.close()
        
        st.success("Invoice Generated Successfully!")
        st.download_button(
            label="📥 Download Amended PDF",
            data=out_bytes.getvalue(),
            file_name="Hotel_Invoice_amended.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error: {e}")
