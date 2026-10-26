import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import zipfile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="Unit Annex Generator", layout="wide")

st.title("🏢 Floor Plan Unit Annex Generator")
st.write("Erfa3 el-Floor Plan w e'mel crop/coordinates le-kol unit 3ashan t-generate el-Annex PDFs.")

# 1. File Uploader
uploaded_file = st.file_uploader("Erfa3 el-Floor Plan (JPG / PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_height, img_width, _ = img.shape

    st.image(img_rgb, caption="Uploaded Floor Plan", use_column_width=True)

    st.subheader("📌 Input Unit Coordinates & Data")
    st.write("Dkhal el-units data (x, y, width, height percent 0-100% bta3et el-plan):")

    # Sample input form for units
    num_units = st.number_input("3adad el-units:", min_value=1, max_value=50, value=1)
    
    units_data = []
    for i in range(num_units):
        st.markdown(f"**Unit {i+1} Details:**")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            code = st.text_input(f"Code #{i+1}", value=f"CX-10{i+4}")
        with col2:
            area = st.text_input(f"Area (m²) #{i+1}", value="103")
        with col3:
            x_pct = st.slider(f"X % #{i+1}", 0, 100, 40)
        with col4:
            y_pct = st.slider(f"Y % #{i+1}", 0, 100, 75)
        with col5:
            w_pct = st.slider(f"W % #{i+1}", 1, 50, 10)
        with col6:
            h_pct = st.slider(f"H % #{i+1}", 1, 50, 12)
        
        units_data.append({
            "code": code,
            "area": area,
            "x": int((x_pct / 100.0) * img_width),
            "y": int((y_pct / 100.0) * img_height),
            "w": int((w_pct / 100.0) * img_width),
            "h": int((h_pct / 100.0) * img_height),
        })

    # Function to generate Key Plan with Red Highlight
    def generate_key_plan(base_img, unit_box):
        key_img = base_img.copy()
        x, y, w, h = unit_box["x"], unit_box["y"], unit_box["w"], unit_box["h"]
        # Draw red rectangle on key plan
        cv2.rectangle(key_img, (x, y), (x + w, y + h), (0, 0, 255), -1) # Red fill
        return key_img

    # Function to generate PDF Annex for a single unit
    def generate_pdf_annex(unit_info, base_img):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        a4_w, a4_h = A4

        # 1. Header Title
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(a4_w / 2, a4_h - 40, "First Floor")

        # 2. Main Crop Image (Top center)
        x, y, w, h = unit_info["x"], unit_info["y"], unit_info["w"], unit_info["h"]
        crop_img = base_img[y:y+h, x:x+w]
        
        # Convert crop to ReportLab Image
        _, crop_encoded = cv2.imencode('.png', crop_img)
        crop_bytes = io.BytesIO(crop_encoded.tobytes())
        crop_rl = ImageReader(crop_bytes)
        c.drawImage(crop_rl, 100, 380, width=400, height=350, preserveAspectRatio=True)

        # 3. Legal Disclaimer Text (Middle)
        c.setFont("Helvetica", 9)
        disclaimer = "جميع الرسومات الهندسية الملحقة بهذا العقد ليست نهائية ويحتفظ المطور بحقه في إدخال التعديلات الملاءمة عليها"
        c.drawCentredString(a4_w / 2, 350, disclaimer)

        # 4. Key Plan with Red Highlight (Bottom center)
        key_img = generate_key_plan(base_img, unit_info)
        _, key_encoded = cv2.imencode('.png', key_img)
        key_bytes = io.BytesIO(key_encoded.tobytes())
        key_rl = ImageReader(key_bytes)
        c.drawImage(key_rl, 150, 100, width=300, height=230, preserveAspectRatio=True)

        # 5. Footer Table Info
        c.setLineWidth(1)
        c.rect(40, 30, a4_w - 80, 50) # Outer table box
        c.line(180, 30, 180, 80)
        c.line(340, 30, 340, 80)
        c.line(440, 30, 440, 80)

        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, 65, "Project Name")
        c.drawString(60, 45, "E Taje Commercial")

        c.drawString(200, 65, "Unit Code")
        c.drawString(200, 45, unit_info["code"])

        c.drawString(360, 65, "Gross Area")
        c.drawString(360, 45, f"{unit_info['area']} M²")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    # Generate All Annexes Button
    if st.button("🚀 Generate All Annexes"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for u in units_data:
                pdf_out = generate_pdf_annex(u, img)
                zip_file.writestr(f"Annex_{u['code']}.pdf", pdf_out.getvalue())
        
        st.success("Tamm e'dad el-annexes be-naga7!")
        st.download_button(
            label="📥 Download All Annexes (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="Unit_Annexes.zip",
            mime="application/zip"
        )
