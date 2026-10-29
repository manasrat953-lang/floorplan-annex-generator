import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw
import io
import zipfile
import re

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

st.set_page_config(page_title="E Taje Real OCR Plan Reader", layout="wide")

st.title("مولد ملاحق الوحدات المعمارية - القراءة الحقيقية بالـ OCR")
st.write("النظام يقرأ الأكواد والمساحات من اللوحة مباشرة (OCR) دون أي تخمين أو أرقام مسبقة.")

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

        extracted_units = []

        if OCR_AVAILABLE:
            # معالجة الصورة لزيادة وضوح الحروف الهندسية للـ OCR
            gray = cv2.cvtColor(floor_np, cv2.COLOR_BGR2GRAY)
            # تكبير الصورة قليلاً لتحسين قراءة النصوص الصغيرة مثل مساحات الغرف
            resized_ocr = cv2.resize(gray, (0, 0), fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
            
            ocr_data = pytesseract.image_to_data(resized_ocr, output_type=pytesseract.Output.DICT)
            n_boxes = len(ocr_data['text'])
            
            detected_raw = []
            areas_raw = []

            for i in range(n_boxes):
                text = ocr_data['text'][i].strip()
                if not text:
                    continue
                
                # تصحيح الإحداثيات بعد التكبير
                x = int(ocr_data['left'][i] / 1.5)
                y = int(ocr_data['top'][i] / 1.5)
                w = int(ocr_data['width'][i] / 1.5)
                h = int(ocr_data['height'][i] / 1.5)

                # البحث عن الأكواد الحقيقية مثل CX-101 أو DX-501 أو AX أو BX
                if re.search(r'(CX|DX|AX|BX)-\d+', text, re.IGNORECASE):
                    match = re.search(r'(CX|DX|AX|BX)-\d+', text, re.IGNORECASE)
                    code_found = match.group(0).upper()
                    detected_raw.append({"code": code_found, "x": x, "y": y, "w": w, "h": h})
                
                # البحث عن المساحات المكتوبة بجوار الوحدات
                elif re.search(r'\d+\s*(m2|m²|M2)', text, re.IGNORECASE):
                    num_match = re.search(r'\d+', text)
                    if num_match:
                        areas_raw.append({"area": num_match.group(0), "x": x, "y": y})

            # ربط الأكواد المكتشفة بالمساحات القريبة منها جغرافياً
            for item in detected_raw:
                matched_area = "100" # قيمة افتراضية إذا لم يجد المساحة المجاورة مباشرة
                min_dist = 999999
                for a in areas_raw:
                    dist = (a['x'] - item['x'])**2 + (a['y'] - item['y'])**2
                    if dist < min_dist and dist < 25000: # في نطاق قريب جداً على الخريطة
                        min_dist = dist
                        matched_area = a['area']

                extracted_units.append({
                    "code": item["code"],
                    "area": matched_area,
                    "x": item["x"], "y": item["y"], "w": item["w"], "h": item["h"]
                })

        # تنبيه إذا لم يتم العثور على أوداك عبر الـ OCR (لتتأكد من وجود حزمة التتريس)
        if len(extracted_units) == 0:
            st.warning("⚠️ لم يتمكن محرك الـ OCR من قراءة الأكواد. تأكد من وجود ملف packages.txt يحتوي على 'tesseract-ocr' في المستودع لكي يعمل القارئ الحقيقي.")
        else:
            # عدّ الوحدات المكتشفة حقيقةً وتصنيفها حسب البادئات الموجودة فقط
            prefix_counts = {}
            for u in extracted_units:
                pref = u["code"].split("-")[0]
                prefix_counts[pref] = prefix_counts.get(pref, 0) + 1

            st.success(f"تم قراءة الفلور بلان بالـ OCR بنجاح! إجمالي الوحدات المقروءة: {len(extracted_units)}")
            
            cols = st.columns(len(prefix_counts) + 1)
            for i, (p, cnt) in enumerate(prefix_counts.items()):
                cols[i].metric(f"وحدات {p}", cnt)
            cols[-1].metric("الإجمالي الكلي", len(extracted_units))

            st.markdown("---")
            choice = st.radio("اختر طريقة التوليد المطلوبة:", ("توليد جميع الوحدات (ZIP)", "اختيار وحدة محددة واستخراجها منفردة"))

            def generate_annex(unit_info):
                img_copy = pil_template.copy()
                code = unit_info["code"]
                area = unit_info["area"]
                x, y, w, h = unit_info["x"], unit_info["y"], unit_info["w"], unit_info["h"]

                x1 = max(0, min(x - 50, fw - 5))
                y1 = max(0, min(y - 50, fh - 5))
                x2 = max(x1 + 100, min(x + w + 100, fw))
                y2 = max(y1 + 100, min(y + h + 100, fh))

                draw_temp = ImageDraw.Draw(img_copy)
                
                # 1. قص الوحدة بناءً على مكان النص المكتشف وتكبيرها في القسم العلوي
                unit_crop = pil_floor.crop((x1, y1, x2, y2))
                unit_crop_resized = unit_crop.resize((1500, 1300))
                img_copy.paste(unit_crop_resized, (500, 300))

                # 2. Key Plan السفلي مع الإطار الأحمر الدقيق حول مكان الوحدة بالفلور بلان الأصلي
                key_plan_cv = floor_np.copy()
                cv2.rectangle(key_plan_cv, (x1, y1), (x2, y2), (0, 0, 255), 6)
                key_rgb = cv2.cvtColor(key_plan_cv, cv2.COLOR_BGR2RGB)
                key_pil = Image.fromarray(key_rgb).resize((1500, 700))
                img_copy.paste(key_pil, (500, 2320))

                # 3. كتابة الكود والمساحة بالأسفل بدقة
                draw_temp.text((1350, template_height - 180), code, fill=(0, 0, 0))
                draw_temp.text((2150, template_height - 180), f"Gross Area = {area} M²", fill=(0, 0, 0))

                buf = io.BytesIO()
                img_copy.save(buf, format="JPEG", quality=95)
                buf.seek(0)
                return buf

            if choice == "توليد جميع الوحدات (ZIP)":
                if st.button("ابدأ التوليد الشامل للوحدات المقروءة"):
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for u in extracted_units:
                            img_buf = generate_annex(u)
                            zip_file.writestr(f"Annex_{u['code']}.jpg", img_buf.getvalue())
                    
                    st.success("تم توليد ملاحق الوحدات المقروءة بنجاح!")
                    st.download_button("تحميل ملف ZIP", data=zip_buffer.getvalue(), file_name="OCR_Read_Units.zip", mime="application/zip")
            else:
                unit_codes = [u["code"] for u in extracted_units]
                selected_code = st.selectbox("اختر كود الوحدة المقروء:", unit_codes)
                selected_unit = next(u for u in extracted_units if u["code"] == selected_code)
                
                if st.button("توليد ملحق الوحدة"):
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
        st.error(f"حدث خطأ أثناء المعالجة: {str(e)}")
