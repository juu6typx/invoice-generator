import streamlit as st
import fitz
import numpy as np
import io
import re
from datetime import datetime, timedelta

APP_PASSWORD = ""  # Optionally set a password here

st.set_page_config(page_title="Doc Amender", layout="centered")
if APP_PASSWORD:
    if st.text_input("Password", type="password") != APP_PASSWORD:
        st.stop()

st.title("📄 Document Amender — 1:1 Invoice Clone")
up = st.file_uploader("1. Upload base invoice PDF", type=["pdf"])

st.subheader("2. Invoice type & variables")
tpl = st.selectbox("Template", ["Ibis / Accor", "Custom labels"])

if tpl == "Ibis / Accor":
    L = dict(guest="Guest Name", ino="Invoice No.", idate="Date", arr="Arrival", dep="Departure",
             dhdr="Date", desch="Description", qtyh="Qty.", chgh="Charges", crh="Credit",
             total="Total", bal="Balance", vatb="VAT Breakdown", v20="VAT 20%", v4="VAT 4%",
             tvat="TOTAL GBP", pay="Mastercard")
else:
    c3, c4 = st.columns(2)
    L = dict(guest=c3.text_input("Guest label", "Guest Name"), ino=c4.text_input("Invoice No. label", "Invoice No."),
             idate=c3.text_input("Invoice date label", "Date"), arr=c4.text_input("Arrival label", "Arrival"),
             dep=c3.text_input("Departure label", "Departure"), dhdr=c4.text_input("Date header", "Date"),
             desch=c3.text_input("Description header", "Description"), qtyh=c4.text_input("Qty header", "Qty."),
             chgh=c3.text_input("Charges header", "Charges"), crh=c4.text_input("Credit header", "Credit"),
             total=c3.text_input("Total label", "Total"), bal=c4.text_input("Balance label", "Balance"),
             vatb=c3.text_input("VAT block header", "VAT Breakdown"), v20=c4.text_input("VAT main row", "VAT 20%"),
             v4=c3.text_input("VAT 2nd row", "VAT 4%"), tvat=c4.text_input("VAT total row", "TOTAL GBP"),
             pay=c4.text_input("Payment keyword", "Mastercard"))

c1, c2 = st.columns(2)
name = c1.text_input("Guest Name", "Mr. Luke Moore")
addr = c1.text_area("Address (one line per line)", "438 Airpoint\nSkypark Road\nBristol\nBS3 3NL")
ino = c2.text_input("Invoice No. (blank = keep)", "")
ref = c2.text_input("Reference No. (11 digits, blank = keep)", "")
inv = c2.text_input("Invoice Date", "02.09.2026")
arr = c2.text_input("Arrival", "28.08.2026")
dep = c2.text_input("Departure", "02.09.2026")
chg = c2.text_input("Nightly Charge", "134.56")
dsc = c2.text_input("Row description", "Accommodation")

c5, c6, c7 = st.columns(3)
fmt_meta = c5.selectbox("Meta date format", ["DD.MM.YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])
fmt_row = c6.selectbox("Row date format", ["DD.MM.YY", "DD/MM/YY", "YYYY-MM-DD"])
vat_rate = c7.number_input("VAT %", 0.0, 50.0, 20.0)

MF = {"DD.MM.YYYY": "%d.%m.%Y", "DD/MM/YYYY": "%d/%m/%Y", "YYYY-MM-DD": "%Y-%m-%d"}
RF = {"DD.MM.YY": "%d.%m.%y", "DD/MM/YY": "%d/%m/%y", "YYYY-MM-DD": "%Y-%m-%d"}
DR = {"DD.MM.YYYY": r"^\d{2}\.\d{2}\.\d{4}$", "DD/MM/YYYY": r"^\d{2}/\d{2}/\d{4}$", "YYYY-MM-DD": r"^\d{4}-\d{2}-\d{2}$"}[fmt_meta]
NR = r"^[\d.,]+$"

if st.button("Generate Invoice", type="primary"):
    if not up:
        st.error("Upload the base PDF first!"); st.stop()
    try:
        CF = float(chg)
        A = datetime.strptime(arr, MF[fmt_meta]); D = datetime.strptime(dep, MF[fmt_meta])
        N = max((D - A).days, 1)
        ROWS = [(A + timedelta(days=i)).strftime(RF[fmt_row]) for i in range(N)]
        CH = "%.2f" % CF; GROSS = CF * N
        TOTC = "%.2f" % GROSS
        NET = "%.2f" % round(GROSS / (1 + vat_rate / 100.0), 2)
        VAT = "%.2f" % round(GROSS - round(GROSS / (1 + vat_rate / 100.0), 2), 2)
        
        doc = fitz.open(stream=up.read(), filetype="pdf"); page = doc[0]
        SP = [s for b in page.get_text("dict")["blocks"] if b.get("type") == 0 for l in b["lines"] for s in l["spans"]]

        def find(t):
            c = [s for s in SP if s["text"].strip() == t]
            if not c: c = [s for s in SP if s["text"].strip().startswith(t)]
            if not c: c = [s for s in SP if t.lower() in s["text"].lower()]
            return c[0] if c else None

        def lab_val(label, pat=None):
            for lab in [s for s in SP if s["text"].strip() == label or s["text"].strip().startswith(label)]:
                vs = [s for s in SP if s is not lab and abs(s["origin"][1] - lab["origin"][1]) < 3 and s["bbox"][0] >= lab["bbox"][2] - 2]
                if vs:
                    v = sorted(vs, key=lambda s: s["bbox"][0])[0]
                    if pat is None or re.match(pat, v["text"].strip()): return lab, v
            return None, None

        def nums_at(y, dx=3):
            return sorted([s for s in SP if abs(s["origin"][1] - y) < dx and re.match(NR, s["text"].strip())], key=lambda s: s["bbox"][0])

        def labs_at(y, dx=3):
            return sorted([s for s in SP if abs(s["origin"][1] - y) < dx and not re.match(NR, s["text"].strip())], key=lambda s: s["bbox"][0])

        def grey_extent(y0, y1):
            pix = page.get_pixmap(dpi=72, clip=fitz.Rect(0, y0, page.rect.width, y1))
            a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].mean(axis=2)
            cols = np.nonzero(((a > 150) & (a < 235)).any(axis=0))[0]
            return (float(cols.min()), float(cols.max() + 1)) if len(cols) else (None, None)

        _, v_name = lab_val(L["guest"]); g_old = v_name["text"].strip() if v_name else name
        _, v_ino = lab_val(L["ino"], r"^[\w/-]+$")
        _, v_dat = lab_val(L["idate"], DR); _, v_arr = lab_val(L["arr"], DR); _, v_dep = lab_val(L["dep"], DR)
        
        # Find 11-digit reference number
        v_ref = None; ref_old = ""
        if ref:
            ref_candidates = [s for s in SP if re.match(r"^\d{11}$", s["text"].strip())]
            if ref_candidates:
                top_candidates = [s for s in ref_candidates if s["origin"][1] < (find(L["desch"])["origin"][1] if find(L["desch"]) else 300)]
                v_ref = sorted(top_candidates if top_candidates else ref_candidates, key=lambda s: s["origin"][1])[0]
                ref_old = v_ref["text"].strip()

        y_hdr = find(L["desch"])["origin"][1]
        hdr = {s["text"].strip(): s for s in SP if abs(s["origin"][1] - y_hdr) < 3 and s["text"].strip() in (L["dhdr"], L["desch"], L["qtyh"], L["chgh"], L["crh"])}
        sz_hdr = hdr[L["desch"]]["size"]; bd_hdr = "Bold" in hdr[L["desch"]]["font"]
        tot_s = min([s for s in SP if s["text"].strip() == L["total"] and s["origin"][1] > y_hdr], key=lambda s: s["origin"][1])
        y_tot = tot_s["origin"][1]; sz_tot = tot_s["size"]; bd_tot = "Bold" in tot_s["font"]
        
        gy = sorted(set(round(s["origin"][1]) for s in SP if y_hdr + 4 < s["origin"][1] < y_tot - 4))
        groups = []
        for y in gy:
            if groups and y - groups[-1][-1] <= 3: groups[-1].append(y)
            else: groups.append([y])
        row_ys = [sum(g) / len(g) for g in groups]
        r1 = row_ys[0]
        payy = next((y for y in row_ys if any((L["pay"].lower() in s["text"].lower() or "XXXX" in s["text"]) for s in SP if abs(s["origin"][1] - y) < 4)), None)
        row_h = (payy - r1) if payy else (row_ys[1] - r1 if len(row_ys) > 1 else 12.0)
        r1n = nums_at(r1)
        qn = [s for s in r1n if s["bbox"][0] < hdr[L["chgh"]]["bbox"][0]]
        qty_right = qn[-1]["bbox"][2] if qn else hdr[L["qtyh"]]["bbox"][2]
        charges_right = r1n[-1]["bbox"][2]
        sz_row = [s for s in SP if abs(s["origin"][1] - r1) < 3][0]["size"]
        x_date = min(s["bbox"][0] for s in SP if abs(s["origin"][1] - r1) < 3)
        x_desc = hdr[L["desch"]]["origin"][0]
        pay_txt = [s["text"] for s in labs_at(payy)] if payy else [L["pay"]]
        if payy and labs_at(payy + row_h * 0.8): pay_txt += [s["text"] for s in labs_at(payy + row_h * 0.8)]
        credit_right = nums_at(payy)[-1]["bbox"][2] if payy and nums_at(payy) else charges_right + 80
        
        bal_s = find(L["bal"]); y_bal = bal_s["origin"][1]
        band_s = find(L["vatb"]); y_vb = band_s["origin"][1]
        sz_mini = band_s["size"]; bd_mini = "Bold" in band_s["font"]
        x_vb = band_s["origin"][0]
        x_na = next((s["origin"][0] for s in SP if s["text"].strip() == "Net Amount" and abs(s["origin"][1] - y_vb) < 3), x_vb)
        x_vat = next((s["origin"][0] for s in SP if s["text"].strip() == "VAT" and abs(s["origin"][1] - y_vb) < 3), x_vb)
        sub_ys = sorted(set(round(s["origin"][1]) for s in SP if s["bbox"][0] > 250 and y_bal - 3 <= s["origin"][1] < y_vb - 4))
        y_tiv = sub_ys[1] if len(sub_ys) > 2 else y_bal + 12
        y_net = sub_ys[2] if len(sub_ys) > 2 else y_bal + 24
        y_v20 = find(L["v20"])["origin"][1]; y_v4 = find(L["v4"])["origin"][1]; y_vtot = find(L["tvat"])["origin"][1]
        n20 = nums_at(y_v20); na_right = n20[0]["bbox"][2]; vat_right = n20[-1]["bbox"][2]
        RE = charges_right
        
        T_left, T_right = grey_extent(y_hdr - 1, y_hdr + 3)
        if T_left is None: T_left, T_right = x_date - 6, credit_right + 6
        M_left, M_right = grey_extent(y_vb - 7, y_vb - 4)
        if M_left is None: M_left, M_right = x_vb - 6, vat_right + 6
        dmini = RE - vat_right
        x_vb2 = x_vb + dmini; x_na2 = x_na + dmini; x_vat2 = x_vat + dmini
        na_right2 = na_right + dmini; vat_right2 = RE
        M_left2 = x_vb2 - (x_vb - M_left); M_right2 = RE + 15
        
        def lr_vr(y):
            ls = labs_at(y); ns = nums_at(y)
            return (max(s["bbox"][2] for s in ls) if ls else RE - 46), (ns[-1]["bbox"][2] if ns else RE), (ls[0]["size"] if ls else 9), ("Bold" in ls[0]["font"] if ls else False)
        lb_bal, vr_bal, sz_b, bd_b = lr_vr(y_bal)
        lb_tiv, vr_tiv, _, _ = lr_vr(y_tiv)
        lb_net, vr_net, _, _ = lr_vr(y_net)
        
        RED = []
        for s in [q for q in SP if q["text"].strip() == g_old]:
            RED.append(fitz.Rect(s["bbox"]) + (-2, -2, 2, 2))
        
        blk = sorted([s for s in SP if s["bbox"][0] < 250 and s["origin"][1] < y_hdr - 30], key=lambda s: s["origin"][1])
        if blk:
            g = (blk[1]["origin"][1] - blk[0]["origin"][1]) if len(blk) > 1 else 11.0
            ax0 = blk[0]["bbox"][0]
            ax1 = max(s["bbox"][2] for s in blk) + 2
            RED.append(fitz.Rect(ax0 - 2, blk[0]["origin"][1] - 10, ax1, blk[0]["origin"][1] + (len(addr.split(chr(10))) + 1) * g + 4))
            
        for v in (v_ino, v_dat, v_arr, v_dep, v_ref):
            if v: RED.append(fitz.Rect(v["bbox"]) + (-1.5, -1.5, 1.5, 1.5))
            
        gdpr_top = next((s["bbox"][1] for s in SP if "The hotel," in s["text"]), 10**4)
        bottom = min(y_vtot + 8, gdpr_top - 4)
        RED.append(fitz.Rect(0, y_hdr - 12, page.rect.width, bottom))
        
        for r in RED:
            page.add_redact_annot(r, fill=(1, 1, 1))
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

        def draw(text, y, bold=False, x=None, right=None, size=9):
            fn = "hebo" if bold else "helv"
            w = fitz.Font(fn).text_length(text, fontsize=size)
            page.insert_text(((right - w) if right is not None else x, y), text, fontname=fn, fontsize=size, color=(0, 0, 0))

        for s in [q for q in SP if q["text"].strip() == g_old]:
            draw(name, s["origin"][1], bold=("Bold" in s["font"]), x=s["origin"][0], size=s["size"])
        if blk:
            lines = [name] + addr.split(chr(10))
            for i, ln in enumerate(lines):
                draw(ln, blk[0]["origin"][1] + i * g, x=ax0, size=blk[0]["size"])
        if v_ino and ino: draw(ino, v_ino["origin"][1], x=v_ino["origin"][0], size=v_ino["size"])
        if v_ref and ref: draw(ref, v_ref["origin"][1], x=v_ref["origin"][0], size=v_ref["size"])
        if v_dat: draw(inv, v_dat["origin"][1], x=v_dat["origin"][0], size=v_dat["size"])
        if v_arr: draw(arr, v_arr["origin"][1], x=v_arr["origin"][0], size=v_arr["size"])
        if v_dep: draw(dep, v_dep["origin"][1], x=v_dep["origin"][0], size=v_dep["size"])
        
        y = y_hdr
        page.draw_rect(fitz.Rect(T_left, y - 8, T_right, y + 3), color=None, fill=grey)
        page.draw_line((T_left, y - 9), (T_right, y - 9), color=(0, 0, 0), width=0.7)
        page.draw_line((T_left, y + 4), (T_right, y + 4), color=(0, 0, 0), width=0.7)
        for lb in (L["dhdr"], L["desch"], L["qtyh"], L["chgh"], L["crh"]):
            draw(lb, y, bold=bd_hdr, x=hdr[lb]["origin"][0], size=sz_hdr)
            
        y += row_h
        for dte in ROWS:
            draw(dte, y, x=x_date, size=sz_row)
            draw(dsc, y, x=x_desc, size=sz_row)
            draw("1", y, right=qty_right, size=sz_row)
            draw(CH, y, right=charges_right, size=sz_row)
            y += row_h
            
        for i, pt in enumerate(pay_txt):
            draw(pt, y + i * row_h * 0.8, x=x_desc, size=sz_row)
        draw("1", y, right=qty_right, size=sz_row)
        draw(TOTC, y, right=credit_right, size=sz_row)
        y += row_h * 0.8 * max(len(pay_txt), 1) + row_h * 0.4
        
        yT = y
        page.draw_line((T_left, yT - 9), (T_right, yT - 9), color=(0, 0, 0), width=0.7)
        page.draw_rect(fitz.Rect(T_left, yT - 8, T_right, yT + 3), color=None, fill=grey)
        page.draw_line((T_left, yT + 4), (T_right, yT + 4), color=(0, 0, 0), width=0.7)
        draw(tot_s["text"], yT, bold=bd_tot, x=tot_s["origin"][0], size=sz_tot)
        draw(TOTC, yT, bold=bd_tot, right=charges_right, size=sz_tot)
        draw(TOTC, yT, bold=bd_tot, right=credit_right, size=sz_tot)
        yT += row_h
        
        draw("".join(s["text"] for s in labs_at(y_bal)), yT, bold=bd_b, right=lb_bal, size=sz_b)
        draw("0.00", yT, bold=bd_b, right=RE, size=sz_b)
        delta = yT - y_bal
        draw("".join(s["text"] for s in labs_at(y_tiv)).replace("Includin g", "Including"), y_tiv + delta, bold=bd_b, right=lb_tiv, size=sz_b)
        draw(TOTC, y_tiv + delta, bold=bd_b, right=RE, size=sz_b)
        draw("".join(s["text"] for s in labs_at(y_net)), y_net + delta, bold=bd_b, right=lb_net, size=sz_b)
        draw(NET, y_net + delta, bold=bd_b, right=RE, size=sz_b)
        
        yv = y_vb + delta
        page.draw_rect(fitz.Rect(M_left2, yv - 7, M_right2, yv + 2), color=None, fill=grey)
        draw(L["vatb"], yv, bold=bd_mini, x=x_vb2, size=sz_mini)
        draw("Net Amount", yv, bold=bd_mini, x=x_na2, size=sz_mini)
        draw("VAT", yv, bold=bd_mini, x=x_vat2, size=sz_mini)
        
        yv = y_v20 + delta
        draw(L["v20"], yv, bold=bd_mini, x=x_vb2, size=sz_mini)
        draw(NET, yv, bold=bd_mini, right=na_right2, size=sz_mini)
        draw(VAT, yv, bold=bd_mini, right=vat_right2, size=sz_mini)
        
        yv = y_v4 + delta
        draw(L["v4"], yv, bold=bd_mini, x=x_vb2, size=sz_mini)
        draw("0.00", yv, bold=bd_mini, right=na_right2, size=sz_mini)
        draw("0.00", yv, bold=bd_mini, right=vat_right2, size=sz_mini)
        
        yv = y_vtot + delta
        page.draw_line((M_left2, yv - sz_mini - 1), (M_right2, yv - sz_mini - 1), color=(0, 0, 0), width=0.7)
        draw(L["tvat"], yv, bold=bd_mini, x=x_vb2, size=sz_mini)
        draw(VAT, yv, bold=bd_mini, right=vat_right2, size=sz_mini)
        page.draw_line((M_left2, yv + 2), (M_right2, yv + 2), color=(0, 0, 0), width=0.7)
        
        out = io.BytesIO(); doc.save(out)
        out.seek(0)
        chk = fitz.open(stream=out.read(), filetype="pdf")
        txt = chk[0].get_text(); chk.close(); doc.close()
        
        GHOSTS = [g_old, ref_old] + [v["text"].strip() for v in (v_ino, v_dat, v_arr, v_dep) if v] + [r1n[-1]["text"].strip()] + [s["text"].strip() for s in nums_at(y_tot)] + [s["text"].strip() for s in nums_at(y_bal)] + [s["text"].strip() for s in nums_at(y_tiv)] + [s["text"].strip() for s in nums_at(y_net)] + [s["text"].strip() for s in n20]
        NEWVALS = [name, inv, arr, dep, ino, ref, CH, TOTC, NET, VAT] + ROWS + addr.split(chr(10))
        ghosts = sorted(set(t for t in GHOSTS if t and len(t) > 1 and t in txt and t not in NEWVALS))
        
        if ghosts:
            st.warning("⚠️ Hidden-text leftovers: " + ", ".join(ghosts))
        else:
            st.success("✅ Hidden-text check passed: original values fully deleted.")
            
        st.success("Invoice Generated Successfully!")
        st.download_button("📥 Download Amended PDF", out.getvalue(), file_name="Invoice_amended.pdf", mime="application/pdf")
        
    except Exception as e:
        st.error(f"Error: {e}")
