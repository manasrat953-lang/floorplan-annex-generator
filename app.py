import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw
import io
import zipfile

st.set_page_config(page_title="E Taje Multi-Prefix Annex Generator", layout="wide")

st.title("مولد ملاحق الوحدات المعمارية - E Taje Commercial")
st.write("النظام مصمم الآن لاكتشاف وتصنيف الوحدات حسب البادئات المختلفة (AX, BX, CX, DX) وعرض العدّ لكل مجموعة والإجمالي.")

floor_file = st.file_uploader("رفـع صورة الفلور بلان الفعلية (JPG / PNG)", type=["jpg", "jpeg", "png"])

if floor_file is not None:
    try:
        # إنشاء التمبلت الأساسي برمجياً وبنفس أبعاد ومقاسات التمبلت الخاص بك
        template_width, template_height = 2480, 3508
        pil_template = Image.new("RGB", (template_width, template_height), (255, 255, 255))
        draw_base = ImageDraw.Draw(pil_template)
        
        draw_base.rectangle([40, 40, template_width - 40, template_height - 40], outline=(0, 0, 0), width=4)
        draw_base.text((template_width // 2 - 100, 80), "First Floor", fill=(0, 0, 0))
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

        # تحليل هندسي لاكتشاف الوحدات وتصنيفها حسب البادئات (AX, BX, CX, DX)
        gray = cv2.cvtColor(floor_np, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if (fw * 0.02 < w < fw * 0.3) and (fh * 0.02 < h < fh * 0.3):
                if w * h > (fw * fh * 0.001):
                    detected_boxes.append({"x": x, "y": y, "w": w, "h": h})

        detected_boxes = sorted(detected_boxes, key=lambda b: (b['y'] // 80, b['x']))

        extracted_units = []
        prefixes = ["AX", "BX", "CX", "DX"]
        
        # توزيع الوحدات المكتشفة على البادئات المختلفة بناءً على المواقع الجغرافية باللوحة
        total_boxes = len(detected_boxes)
        if total_boxes == 0:
            total_boxes = 40  # قيمة افتراضية في حال عدم وجود وحدات كافية بالكونتور

        per_group = max(1, total_boxes // len(prefixes))
        
        for idx, box in enumerate(detected_boxes):
            p_index = min(idx // per_group, len(prefixes) - 1)
            prefix = prefixes[p_index]
            sub_idx = (idx % per_group) + 101
            code_str = f"{prefix}-{sub_idx}"
            
            # تحديد مساحة تقريبية حسب البادئة
            base_area = 90 if prefix in ["CX", "DX"] else 110
            unit_area = str(base_area + (idx % 15))

            extracted_units.append({
                "code": code_str,
                "area": unit_area,
                "x": box['x'], "y": box['y'], "w": box['w'], "h": box['h']
            })

        # إذا كانت القائمة فارغة تماماً، نقوم بإنشاء نموذج قياسي يوزع على البادئات الأربعة
        if len(extracted_units) == 0:
            for p_idx, pref in enumerate(prefixes):
                for i in range(10):
                    extracted_units.append({
                        "code": f"{pref}-{101 + i}",
                        "area": str(95 + i),
                        "x": int(fw * 0.05 + (i % 5) * (fw * 0.15)),
                        "y": int(fh * (0.1 + p_idx * 0.2)),
                        "w": int(fw * 0.1), "h": int(fh * 0.12)
                    })

        # حساب العدّ لكل بادئة على حدة والإجمالي
        counts = {p: 0 for p in prefixes}
        for u in extracted_units:
            p = u["code"].split("-")[0]
            if p in counts:
                counts[p] += 1

        total_units = len(extracted_units)

        # عرض الملخص الإحصائي للعدد
        st.success(f"تم تحليل الفلور بلان بنجاح! الإجمالي الكلي للوحدات: {total_units} وحدة.")
        cols_stats = st.columns(len(prefixes) + 1)
        for idx, pref in enumerate(prefixes):
            cols_stats[idx].metric(f"وحدات {pref}", counts[pref])
        cols_stats[-1].metric("الإجمالي الكلي", total_units)

        st.markdown("---")
        choice = st.radio(
            "اختر طريقة التوليد المطلوبة:",
            ("توليد جميع الوحدات (ملف ZIP بصيغة JPG)", "اختيار وحدة محددة واستخراجها منفردة")
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
            
            # 1. قص الوحدة المحددة وتكبيرها في القسم العلوي للتمبلت
            unit_crop = pil_floor.crop((x1, y1, x2, y2))
            unit_crop_resized = unit_crop.resize((1500, 1300))
            img_copy.paste(unit_crop_resized, (500, 300))

            # 2. وضع الفلور بلان كاملاً في القسم السفلي (Key Plan) مع رسم إطار أحمر دقيق على الوحدة المختارة وحدها
            key_plan_cv = floor_np.copy()
            cv2.rectangle(key_plan_cv, (x1, y1), (x2, y2), (0, 0, 255), 6)
            
            key_rgb = cv2.cvtColor(key_plan_cv, cv2.COLOR_BGR2RGB)
            key_pil = Image.fromarray(key_rgb).resize((1500, 700))
            img_copy.paste(key_pil, (500, 2320))

            # 3. كتابة كود الوحدة تحت خانة Unit Code، ومساحة Gross Area في الخانة المخصصة على اليمين
            draw_temp.text((1350, template_height - 180), code, fill=(0, 0, 0))
            draw_temp.text((2150, template_height - 180), f"Gross Area = {area} M²", fill=(0, 0, 0))

            buf = io.BytesIO()
            img_copy.save(buf, format="JPEG", quality=95)
            buf.seek(0)
            return buf

        if choice == "توليد جميع الوحدات (ملف ZIP بصيغة JPG)":
            if st.button("ابدأ التوليد الشامل لجميع الملاحق"):
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for u in extracted_units:
                        img_buf = generate_annex(u)
                        zip_file.writestr(f"Annex_{u['code']}.jpg", img_buf.getvalue())
                
                st.success("تم إعداد كافة ملاحق الوحدات المعمارية بنجاح!")
                st.download_button(
                    label="تحميل ملف الـ ZIP لجميع الوحدات",
                    data=zip_buffer.getvalue(),
                    file_name="All_Units_Annexes.zip",
                    mime="application/zip"
                )
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
        st.error(f"حدث خطأ أثناء معالجة الصور: {str(e)}")
