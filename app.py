import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw
import io
import zipfile

st.set_page_config(page_title="E Taje Strict Precision Engine", layout="wide")

st.title("مولد ملاحق الوحدات المعمارية - E Taje Commercial")
st.write("محرك الفلترة الدقيقة الصارم: استبعاد الشخابيط والأعمدة وعدّ الوحدات الرئيسية الحقيقية فقط.")

floor_file = st.file_uploader("رفـع صورة الفلور بلان (JPG / PNG)", type=["jpg", "jpeg", "png"])

if floor_file is not None:
    try:
        template_width, template_height = 2480, 3508
        pil_template = Image.new("RGB", (template_width, template_height), (255, 255, 255))
        draw_base = ImageDraw.Draw(pil_template)
        
        draw_base.rectangle([40, 40, template_width - 40, template_height - 40], outline=(0, 0, 0), width=4)
        draw_base.text((template_width // 2 - 100, 80), "Floor Plan Annex", fill=(0, 0, 0))
        draw_base.line([40, 2100, template_width - 40, 2100], fill=(0, 0, 0), width=3)
        draw_base.text((template_width // 2 - 400, 2150), "جميع الرسومات الهندسية الملحقة بهذا العقد ليست نهائية ويحتفظ المطور بحقها في ادخال التعديلات الملائمة عليها", fill=(0, 0, 0))
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

        # معالجة صارمة جداً لاستبعاد أي خطوط رفيعة أو تفاصيل داخلية
        gray = cv2.cvtColor(floor_np, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 210, 255, cv2.THRESH_BINARY_INV)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        valid_boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            
            min_w = fw * 0.035
            max_w = fw * 0.18
            min_h = fh * 0.035
            max_h = fh * 0.18
            
            if min_w < w < max_w and min_h < h < max_h:
                if (fw * fh * 0.0015) < area < (fw * fh * 0.03):
                    valid_boxes.append({"x": x, "y": y, "w": w, "h": h})

        filtered_boxes = []
        for b1 in valid_boxes:
            is_overlap = False
            for b2 in filtered_boxes:
                if abs(b1['x'] - b2['x']) < 40 and abs(b1['y'] - b2['y']) < 40:
                    is_overlap = True
                    break
            if not is_overlap:
                filtered_boxes.append(b1)

        filtered_boxes = sorted(filtered_boxes, key=lambda b: (b['y'] // 80, b['x']))

        extracted_units = []
        cx_count = 101
        dx_count = 101

        for idx, box in enumerate(filtered_boxes):
            if box['x'] < fw * 0.58:
                prefix = "CX"
                code_str = f"{prefix}-{cx_count}"
                cx_count += 1
                area_val = "92"
            else:
                prefix = "DX"
                code_str = f"{prefix}-{dx_count}"
                dx_count += 1
                area_val = "74"

            extracted_units.append({
                "code": code_str,
                "area": area_val,
                "x": box['x'], "y": box['y'], "w": box['w'], "h": box['h']
            })

        prefix_counts = {}
        for u in extracted_units:
            pref = u["code"].split("-")[0]
            prefix_counts[pref] = prefix_counts.get(pref, 0) + 1

        total_units = len(extracted_units)

        st.success(f"تمت الفلترة بنجاح! الإجمالي الحقيقي للوحدات المعمارية الصافية: {total_units} وحدة.")
        
        if total_units > 0:
            cols = st.columns(len(prefix_counts) + 1)
            for i, (p, cnt) in enumerate(prefix_counts.items()):
                cols[i].metric(f"وحدات {p}", cnt)
            cols[-1].metric("الإجمالي الكلي", total_units)
        else:
            st.warning("لم يتم رصد وحدات بعد الفلترة الصارمة. تأكد من وضوح الفلور بلان.")

        st.markdown("---")
        choice = st.radio("اختر طريقة التوليد المطلوبة:", ("توليد جميع الوحدات (ملف ZIP بصيغة JPG)", "اختيار وحدة محددة واستخراجها منفردة"))

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

        if choice == "توليد جميع الوحدات (ملف ZIP بصيغة JPG)":
            if st.button("ابدأ التوليد الشامل لجميع الملاحق"):
                if total_units == 0:
                    st.warning("لا توجد وحدات متاحة للتوليد.")
                else:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for u in extracted_units:
                            img_buf = generate_annex(u)
                            zip_file.writestr(f"Annex_{u['code']}.jpg", img_buf.getvalue())
                    
                    st.success("تم إعداد كافة ملاحق الوحدات المعمارية بنجاح!")
                    st.download_button(
                        label="تحميل ملف الـ ZIP لجميع الوحدات",
                        data=zip_buffer.getvalue(),
                        file_name="Strict_Units_Annexes.zip",
                        mime="application/zip"
                    )
        else:
            if total_units == 0:
                st.warning("لا توجد وحدات متاحة.")
            else:
                unit_codes = [u["code"] for u in extracted_units]
                selected_code = st.selectbox("اختر كود الوحدة المطلوبة:", unit_codes)
                selected_unit = next(u for u in extracted_units if u["code"] == selected_code)
                
                if st.button("توليد ملحق الوحدة المحددة"):
                    img_buf = generate_annex(selected_unit)
                    st.success(f"تم توليد ملحق الوحدة {selected_code} بنجاح!")
                    st.image(img_buf, caption=f"Annex {selected_code}", use_container_width=True)
                    st.download_button(
                        label=f"تحميل صورة Annex_{selected_code}.jpg",
                        data=img_buf.getvalue(),
                        file_name=f"Annex_{selected_code}.jpg",
                        mime="image/jpeg"
                    )
    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الفلور بلان: {str(e)}")
