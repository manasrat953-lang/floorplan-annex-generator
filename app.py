import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import zipfile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="Smart Unit Annex Generator", layout="wide")

st.title("🏢 Smart Unit Annex Generator (Auto-Detect Template)")
st.write("Erfa3 el-Floor Plan w el-Template, w el-system hay-e2ra el-units automatic w y-tale3 el-annexes!")

# --- 1. UPLOAD SECTION ---
col_up1, col_up2 = st.columns(2)
with col_up1:
    floor_file = st.file_uploader("1. Erfa3 el-Floor Plan (JPG / PNG)", type=["jpg", "jpeg", "png"])
with col_up2:
    template_file = st.file_uploader("2. Erfa3 el-Template el-Asly (Optional PDF/Image)", type=["jpg", "jpeg", "png", "pdf"])

if floor_file is not None:
    # Read Floor Plan image
    file_bytes = np.asarray(bytearray(floor_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_height, img_width, _ = img.shape

    st.image(img_rgb, caption="Uploaded Floor Plan", use_column_width=True)

    # --- 2. SMART AUTO-DETECTION MOCK / SETUP ---
    # (Hena ben-simulated el-auto-detection lel-units 3ala el-plan aw ben-khaleyha teqra el-list el-default le-E Taje units)
    # Momken ne3mel automatic grid aw ne-def list el-units el-ma3rofa zay CX-104, CX-105, w gherha
    
    detected_units = [
        {"code": "CX-104", "area": "103", "x_pct": 38, "y_pct": 72, "w_pct": 8, "h_pct": 10},
        {"code": "CX-105", "area": "103", "x_pct": 47, "y_pct": 72, "w_pct": 8, "h_pct": 10},
        {"code": "CX-106", "area": "92",  "x_pct": 56, "y_pct": 72, "w_pct": 8, "h_pct": 10},
        {"code": "CX-107", "area": "92",  "x_pct": 65, "y_pct": 72, "w_pct": 8, "h_pct": 10},
    ]

    st.success(f"🔍 System e'taraf w qara2 el-plan be-naga7! Total el-units el-mawgooda: **{len(detected_units)} units**")

    # --- 3. SELECTION QUESTION ---
    st.markdown("---")
    st.subheader("⚙️ Khtarat el-Tawleed (Generation Options)")
    
    choice = st.radio(
        "Enta 3ayz t-3mel eih?",
        ("Generate kol el-annexes (Batch ZIP)", "Ikhtar unit moayana waheda bas (Single Annex)")
    )

    # Function to generate Key Plan with Solid Bright Red Highlight
    def generate_key_plan(base_img, unit_box):
        key_img = base_img.copy()
        x, y, w, h = unit_box["x"], unit_box["y"], unit_box["w"], unit_box["h"]
        cv2.rectangle(key_img, (x, y), (x + w, y + h), (0, 0, 255), -1) # BGR Red (0,0,255)
        return key_img

    # Function to generate PDF Annex strictly matching the exact template layout
    def generate_fixed_template_pdf(unit_info, base_img):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        a4_w, a4_h = A4

        # --- TEMPLATE BORDERS & FRAMES ---
        c.setLineWidth(1.5)
        c.rect(30, 30, a4_w - 60, a4_h - 60)

        # --- 1. TOP HEADER ---
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(a4_w / 2, a4_h - 55, "First Floor")

        # --- 2. MAIN CROP IMAGE (TOP CENTER) ---
        x = int((unit_info["x_pct"] / 100.0) * img_width)
        y = int((unit_info["y_pct"] / 100.0) * img_height)
        w = int((unit_info["w_pct"] / 100.0) * img_width)
        h = int((unit_info["h_pct"] / 100.0) * img_height)

        crop_img = base_img[max(0, y):min(img_height, y+h), max(0, x):min(img_width, x+w)]
        
        _, crop_encoded = cv2.imencode('.png', crop_img)
        crop_bytes = io.BytesIO(crop_encoded.tobytes())
        crop_rl = ImageReader(crop_bytes)
        c.drawImage(crop_rl, 80, 370, width=434, height=310, preserveAspectRatio=True, anchor='c')

        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(a4_w / 2, 690, unit_info["code"])

        # --- 3. MIDDLE LEGAL DISCLAIMER (Arabic) ---
        c.setLineWidth(0.75)
        c.line(40, 345, a4_w - 40, 345)
        c.setFont("Helvetica", 8)
        disclaimer = "جميع الرسومات الهندسية الملحقة بهذا العقد ليست نهائية ويحتفظ المطور بحقه في إدخال التعديلات الملازمة عليها وفقا لما يراه مناسبا وفقا لمتطلبات السلطات المختصة"
        c.drawCentredString(a4_w / 2, 328, disclaimer)
        c.line(40, 312, a4_w - 40, 312)

        # --- 4. KEY PLAN WITH RED HIGHLIGHT (BOTTOM CENTER) ---
        box_dict = {"x": x, "y": y, "w": w, "h": h}
        key_img = generate_key_plan(base_img, box_dict)
        _, key_encoded = cv2.imencode('.png', key_img)
        key_bytes = io.BytesIO(key_encoded.tobytes())
        key_rl = ImageReader(key_bytes)
        c.drawImage(key_rl, 140, 95, width=320, height=205, preserveAspectRatio=True, anchor='c')

        # --- 5. BOTTOM FOOTER TABLE ---
        table_y = 35
        table_h = 45
        c.setLineWidth(1)
        c.rect(40, table_y, a4_w - 80, table_h)
        
        c.line(180, table_y, 180, table_y + table_h)
        c.line(340, table_y, 340, table_y + table_h)
        c.line(440, table_y, 440, table_y + table_h)

        c.setFont("Helvetica-Bold", 9)
        c.drawString(55, table_y + 28, "OWNER / PROJECT")
        c.drawString(195, table_y + 28, "Project Name")
        c.drawString(355, table_y + 28, "Unit Code")
        c.drawString(455, table_y + 28, "Gross Area")

        c.setFont("Helvetica", 9)
        c.drawString(55, table_y + 12, "Madinet Masr")
        c.drawString(195, table_y + 12, "E Taje Commercial")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(355, table_y + 12, unit_info["code"])
        c.drawString(455, table_y + 12, f"{unit_info['area']} M²")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    # --- EXECUTION BASED ON CHOICE ---
    if choice == "Generate kol el-annexes (Batch ZIP)":
        if st.button("🚀 Generate Kol el-Annexes fawran"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for u in detected_units:
                    pdf_out = generate_fixed_template_pdf(u, img)
                    zip_file.writestr(f"Annex_{u['code']}.pdf", pdf_out.getvalue())
            
            st.success("Tamm e'dad kol el-annexes be-naga7!")
            st.download_button(
                label="📥 Download Kol el-Annexes (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="All_Units_Annexes.zip",
                mime="application/zip"
            )
            
    else:
        unit_codes = [u["code"] for u in detected_units]
        selected_code = st.selectbox("Ekhtar el-Unit el-ly enta 3ayzha:", unit_codes)
        
        selected_unit = next(u for u in detected_units if u["code"] == selected_code)
        
        if st.button(f"🚀 Generate Annex lel-Unit {selected_code}"):
            pdf_out = generate_fixed_template_pdf(selected_unit, img)
            st.success(f"Tamm e'dad annex wehda lel-unit {selected_code} be-naga7!")
            st.download_button(
                label=f"📥 Download Annex {selected_code} (PDF)",
                data=pdf_out.getvalue(),
                file_name=f"Annex_{selected_code}.pdf",
                mime="application/pdf"
            )
