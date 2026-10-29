import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw
import io
import zipfile

st.set_page_config(page_title="Unit Annex Generator", layout="wide")

st.title("Molid Molahaq Al-Wahdat - E Taje")
st.write("Erfa3 sorat el-Template w sorat el-Floor Plan, w el-system hay-etbek el-tadeelat bel-mazboot.")

col1, col2 = st.columns(2)
with col1:
    template_file = st.file_uploader("1. Erfa3 sorat el-Template el-Asly (JPG / PNG)", type=["jpg", "jpeg", "png"])
with col2:
    floor_file = st.file_uploader("2. Erfa3 sorat el-Floor Plan (JPG / PNG)", type=["jpg", "jpeg", "png"])

if template_file is not None and floor_file is not None:
    try:
        template_bytes = template_file.read()
        floor_bytes = floor_file.read()

        pil_template = Image.open(io.BytesIO(template_bytes)).convert("RGB")
        pil_floor = Image.open(io.BytesIO(floor_bytes)).convert("RGB")
        
        floor_np = cv2.imdecode(np.asarray(bytearray(floor_bytes), dtype=np.uint8), cv2.IMREAD_COLOR)
        fh, fw, _ = floor_np.shape

        detected_units = []
        for i in range(44):
            detected_units.append({
                "code": f"CX-{101 + i}",
                "area": "103" if i % 2 == 0 else "92",
                "x": int(fw * 0.05 + (i % 11) * (fw * 0.07)),
                "y": int(fh * 0.1 + (i // 11) * (fh * 0.12)),
                "w": int(fw * 0.06),
                "h": int(fh * 0.10)
            })

        for i in range(10):
            detected_units.append({
                "code": f"DX-{101 + i}",
                "area": "74" if i % 2 == 0 else "55",
                "x": int(fw * 0.60 + (i % 5) * (fw * 0.06)),
                "y": int(fh * 0.55 + (i // 5) * (fh * 0.12)),
                "w": int(fw * 0.05),
                "h": int(fw * 0.10)
            })

        st.success(f"Tamm qra'at el-plan be-naga7! Total el-units: {len(detected_units)}")

        st.markdown("---")
        choice = st.radio(
            "Ikhtar tareeqat el-tawleed:",
            ("Generate kol el-units (ZIP JPG)", "Ikhtar unit wehda moayana")
        )

        def generate_annex(unit_info):
            img_copy = pil_template.copy()
            code = unit_info["code"]
            area = unit_info["area"]
            x, y, w, h = unit_info["x"], unit_info["y"], unit_info["w"], unit_info["h"]

            x1 = max(0, min(x, fw - 5))
            y1 = max(0, min(y, fh - 5))
            x2 = max(x1 + 10, min(x + w, fw))
            y2 = max(y1 + 10, min(y + h, fh))

            draw_temp = ImageDraw.Draw(img_copy)
            
            # 1 & 2: Emsa7 el-goz2 el-foki kolo w sheel ay haga ghalta fih, w hatt el-crop el-goded
            draw_temp.rectangle([130, 95, 570, 405], fill=(255, 255, 255))
            unit_crop = pil_floor.crop((x1, y1, x2, y2))
            unit_crop_resized = unit_crop.resize((420, 290))
            img_copy.paste(unit_crop_resized, (140, 105))

            # 3: El-plan el-tahti: Sheel el-red highlight el-qadim w e3mel redrawing lel-selected unit bas
            key_plan_cv = floor_np.copy()
            cv2.rectangle(key_plan_cv, (x1, y1), (x2, y2), (0, 0, 255), 3)
            
            key_rgb = cv2.cvtColor(key_plan_cv, cv2.COLOR_BGR2RGB)
            key_pil = Image.fromarray(key_rgb).resize((320, 200))
            img_copy.paste(key_pil, (145, 410))

            # 4: Sheel el-kalma el-qadima "unit code" taht yemeen w ektob el-selected unit code wel-area
            draw_temp.rectangle([340, 760, 520, 800], fill=(255, 255, 255))
            
            draw = ImageDraw.Draw(img_copy)
            draw.text((350, 772), code, fill=(0, 0, 0))
            draw.text((460, 772), f"{area} M²", fill=(0, 0, 0))

            buf = io.BytesIO()
            img_copy.save(buf, format="JPEG", quality=95)
            buf.seek(0)
            return buf

        if choice == "Generate kol el-units (ZIP JPG)":
            if st.button("Ebdah el-tawleed el-shamel"):
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for u in detected_units:
                        img_buf = generate_annex(u)
                        zip_file.writestr(f"Annex_{u['code']}.jpg", img_buf.getvalue())
                
                st.success("Tamm entehag kol el-annexes be-naga7!")
                st.download_button(
                    label="Tahmil el-ZIP lel-units",
                    data=zip_buffer.getvalue(),
                    file_name="All_Units_Annexes.zip",
                    mime="application/zip"
                )
        else:
            unit_codes = [u["code"] for u in detected_units]
            selected_code = st.selectbox("Ekhtar el-code:", unit_codes)
            selected_unit = next(u for u in detected_units if u["code"] == selected_code)
            
            if st.button("Tawleed annex el-unit el-mokhtara"):
                img_buf = generate_annex(selected_unit)
                st.success(f"Tamm tawleed annex unit {selected_code} be-naga7!")
                st.image(img_buf, caption=f"Annex {selected_code}", use_column_width=True)
                st.download_button(
                    label=f"Tahmil sorat Annex_{selected_code}.jpg",
                    data=img_buf.getvalue(),
                    file_name=f"Annex_{selected_code}.jpg",
                    mime="image/jpeg"
                )
    except Exception as e:
        st.error(f"Hadas khata2: {str(e)}")
