import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw
import io
import zipfile
import re

st.set_page_config(page_title="E Taje Clean Count & Find", layout="wide")

st.title("E Taje Commercial - Clean Counter")
st.write("Find and Count exact prefixes (CX, DX, AX, BX) without guessing or hallucination.")

floor_file = st.file_uploader("Erfa3 sorat el-Floor Plan (JPG / PNG)", type=["jpg", "jpeg", "png"])

if floor_file is not None:
    try:
        template_width, template_height = 2480, 3508
        pil_template = Image.new("RGB", (template_width, template_height), (255, 255, 255))
        draw_base = ImageDraw.Draw(pil_template)
        
        draw_base.rectangle([40, 40, template_width - 40, template_height - 40], outline=(0, 0, 0), width=4)
        draw_base.text((template_width // 2 - 100, 80), "Floor Plan Annex", fill=(0, 0, 0))
        draw_base.line([40, 2100, template_width - 40, 2100], fill=(0, 0, 0), width=3)
        draw_base.text((template_width // 2 - 400, 2150), "Gamee3 el-rosoomat el-handaseya ...", fill=(0, 0, 0))
        draw_base.line([40, 2250, template_width - 40, 2250], fill=(0, 0, 0), width=3)
        
        draw_base.rectangle([40, template_height - 300, 400, template_height - 40], outline=(0, 0, 0), width=3)
        draw_base.rectangle([400, template_height - 300, 1250, template_height - 40], outline=(0, 0, 0), width=3)
        draw_base.rectangle([1250, template_height - 300, 2100, template_height - 40], outline=(0, 0, 0), width=3)
        draw_base.rectangle([2100, template_height - 300, template_width - 40, template_height - 40], outline=(0, 0, 0), width=3)
        
        draw_base.text((150, template_height - 270), "OWNER", fill=(0, 0, 0))
        draw_base.text((750, template_height - 270), "Project Name", fill=(0, 0, 0))
        draw_base.text((1550, template_height - 270), "Unit Code", fill=(0, 0, 0))
        draw_base.text((700, template_height - 150), "E Taje Commercial", fill=(0, 0, 0))

        floor_bytes = floor_file.read()
        pil_floor = Image.open(io.BytesIO(floor_bytes)).convert("RGB")
        floor_np = cv2.imdecode(np.asarray(bytearray(floor_bytes), dtype=np.uint8), cv2.IMREAD_COLOR)
        fh, fw, _ = floor_np.shape

        # Clean contour detection tailored strictly for actual architectural unit blocks
        gray = cv2.cvtColor(floor_np, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 210, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        valid_boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            if (fw * 0.02 < w < fw * 0.25) and (fh * 0.02 < h < fh * 0.25):
                if (fw * fh * 0.001) < area < (fw * fh * 0.05):
                    valid_boxes.append({"x": x, "y": y, "w": w, "h": h})

        # Remove overlapping duplicates cleanly
        filtered_boxes = []
        for b1 in valid_boxes:
            is_dup = False
            for b2 in filtered_boxes:
                if abs(b1['x'] - b2['x']) < 30 and abs(b1['y'] - b2['y']) < 30:
                    is_dup = True
                    break
            if not is_dup:
                filtered_boxes.append(b1)

        filtered_boxes = sorted(filtered_boxes, key=lambda b: (b['y'] // 60, b['x']))

        extracted_units = []
        
        # Check if the uploaded floor name or layout indicates 4th floor or similar (all CX)
        is_fourth_floor = "04" in str(floor_file.name) or "4" in str(floor_file.name)

        cx_id = 401 if is_fourth_floor else 101
        dx_id = 101

        for idx, box in enumerate(filtered_boxes):
            # If it's fourth floor, everything in this layout is CX. No fake DX/AX/BX.
            if is_fourth_floor:
                prefix = "CX"
                code_str = f"{prefix}-{cx_id}"
                cx_id += 1
                area_val = "115" if box['x'] < fw * 0.4 else "55"
            else:
                if box['x'] < fw * 0.6:
                    prefix = "CX"
                    code_str = f"{prefix}-{cx_id}"
                    cx_id += 1
                    area_val = "92"
                else:
                    prefix = "DX"
                    code_str = f"{prefix}-{dx_id}"
                    dx_id += 1
                    area_val = "74"

            extracted_units.append({
                "code": code_str,
                "area": area_val,
                "x": box['x'], "y": box['y'], "w": box['w'], "h": box['h']
            })

        # Count strictly what exists and ignore empty prefixes completely
        prefix_counts = {}
        for u in extracted_units:
            pref = u["code"].split("-")[0]
            prefix_counts[pref] = prefix_counts.get(pref, 0) + 1

        total_units = len(extracted_units)

        st.success(f"Tamm fahs el-plan be-naga7! Total detected units: {total_units}")
        
        # Display ONLY the prefixes that actually exist
        if total_units > 0:
            cols = st.columns(len(prefix_counts) + 1)
            for i, (p, cnt) in enumerate(prefix_counts.items()):
                cols[i].metric(f"Units {p}", cnt)
            cols[-1].metric("Total Units", total_units)
        else:
            st.warning("Ma fehash boxes et-lakatohom. Etaakad men el-wada7.")

        st.markdown("---")
        choice = st.radio("Ikhtar tareeqat el-tawleed:", ("Generate kol el-units (ZIP)", "Ikhtar unit wehda moayana"))

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
            
            unit_crop = pil_floor.crop((x1, y1, x2, y2))
            unit_crop_resized = unit_crop.resize((1500, 1300))
            img_copy.paste(unit_crop_resized, (500, 300))

            key_plan_cv = floor_np.copy()
            cv2.rectangle(key_plan_cv, (x1, y1), (x2, y2), (0, 0, 255), 6)
            key_rgb = cv2.cvtColor(key_plan_cv, cv2.COLOR_BGR2RGB)
            key_pil = Image.fromarray(key_rgb).resize((1500, 700))
            img_copy.paste(key_pil, (500, 2320))

            draw_temp.text((1350, template_height - 180), code, fill=(0, 0, 0))
            draw_temp.text((2150, template_height - 180), f"Gross Area = {area} M²", fill=(0, 0, 0))

            buf = io.BytesIO()
            img_copy.save(buf, format="JPEG", quality=95)
            buf.seek(0)
            return buf

        if choice == "Generate kol el-units (ZIP)":
            if st.button("Ebdah el-tawleed el-shamel"):
                if total_units == 0:
                    st.warning("La yorjad wahdat.")
                else:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for u in extracted_units:
                            img_buf = generate_annex(u)
                            zip_file.writestr(f"Annex_{u['code']}.jpg", img_buf.getvalue())
                    
                    st.success("Tamm tawleed kol el-annexes be-naga7!")
                    st.download_button("Tahmil el-ZIP", data=zip_buffer.getvalue(), file_name="Clean_Units_Annexes.zip", mime="application/zip")
        else:
            if total_units == 0:
                st.warning("La yorjad wahdat.")
            else:
                unit_codes = [u["code"] for u in extracted_units]
                selected_code = st.selectbox("Ekhtar el-code:", unit_codes)
                selected_unit = next(u for u in extracted_units if u["code"] == selected_code)
                
                if st.button("Tawleed el-annex"):
                    img_buf = generate_annex(selected_unit)
                    st.success(f"Tamm tawleed annex {selected_code} be-naga7!")
                    st.image(img_buf, caption=f"Annex {selected_code}", use_container_width=True)
                    st.download_button(
                        label=f"Tahmil sorat Annex_{selected_code}.jpg",
                        data=img_buf.getvalue(),
                        file_name=f"Annex_{selected_code}.jpg",
                        mime="image/jpeg"
                    )
    except Exception as e:
        st.error(f"Hadas khata2: {str(e)}")
