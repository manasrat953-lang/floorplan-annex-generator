import streamlit as st
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import os

st.set_page_config(
    page_title="Auto Contract Sheet Generator | مولّد اللوحات التعاقدية الأوتوماتيكي",
    page_icon="🏢",
    layout="wide"
)

# -------------------------------------------------------------
# Constant Colors & Styling
# -------------------------------------------------------------
BLACK_LINE = (0, 0, 0)
WHITE_FILL = (255, 255, 255)

# -------------------------------------------------------------
# Complete Database of First-Floor Units (Direct Coordinate Mapping)
# -------------------------------------------------------------
FIRST_FLOOR_UNITS = {
    "AX-101": {"area": 103, "spill": 0,  "type": "purple", "box": (860, 880, 950, 980)},
    "AX-102": {"area": 52,  "spill": 0,  "type": "purple", "box": (790, 880, 860, 980)},
    "AX-103": {"area": 52,  "spill": 0,  "type": "purple", "box": (730, 880, 800, 980)},
    "AX-104": {"area": 103, "spill": 0,  "type": "purple", "box": (650, 880, 730, 980)},
    "AX-105": {"area": 38,  "spill": 0,  "type": "purple", "box": (630, 810, 720, 890)},
    "AX-106": {"area": 38,  "spill": 0,  "type": "purple", "box": (630, 760, 720, 835)},
    "AX-107": {"area": 38,  "spill": 0,  "type": "purple", "box": (630, 700, 720, 780)},
    "AX-108": {"area": 38,  "spill": 0,  "type": "purple", "box": (630, 650, 720, 725)},
    "AX-109": {"area": 39,  "spill": 0,  "type": "purple", "box": (630, 595, 720, 670)},
    "AX-110": {"area": 52,  "spill": 0,  "type": "purple", "box": (620, 545, 710, 620)},
    "AX-111": {"area": 102, "spill": 0,  "type": "purple", "box": (660, 480, 755, 565)},
    "AX-112": {"area": 103, "spill": 0,  "type": "purple", "box": (635, 415, 730, 500)},
    "AX-113": {"area": 103, "spill": 0,  "type": "purple", "box": (585, 365, 680, 455)},
    "AX-114": {"area": 104, "spill": 0,  "type": "purple", "box": (520, 335, 620, 425)},
    "AX-115": {"area": 51,  "spill": 0,  "type": "purple", "box": (465, 385, 545, 470)},
    "AX-116": {"area": 39,  "spill": 0,  "type": "purple", "box": (410, 375, 495, 455)},
    "AX-117": {"area": 39,  "spill": 0,  "type": "purple", "box": (360, 375, 445, 440)},
    "AX-118": {"area": 39,  "spill": 0,  "type": "purple", "box": (310, 375, 395, 435)},
    "AX-119": {"area": 39,  "spill": 0,  "type": "purple", "box": (260, 375, 345, 435)},
    "AX-120": {"area": 39,  "spill": 0,  "type": "purple", "box": (210, 375, 290, 435)},
    "AX-121": {"area": 121, "spill": 0,  "type": "purple", "box": (115, 355, 205, 445)},
    "AX-122": {"area": 61,  "spill": 0,  "type": "purple", "box": (115, 280, 205, 360)},
    "AX-123": {"area": 61,  "spill": 0,  "type": "purple", "box": (115, 230, 205, 305)},
    "AX-124": {"area": 121, "spill": 0,  "type": "purple", "box": (115, 145, 205, 235)},
    "AX-125": {"area": 38,  "spill": 0,  "type": "purple", "box": (210, 130, 285, 200)},
    "AX-126": {"area": 38,  "spill": 0,  "type": "purple", "box": (260, 130, 340, 200)},
    "AX-127": {"area": 38,  "spill": 0,  "type": "purple", "box": (310, 130, 395, 200)},
    "AX-128": {"area": 38,  "spill": 0,  "type": "purple", "box": (360, 130, 445, 200)},
    "AX-129": {"area": 38,  "spill": 0,  "type": "purple", "box": (410, 130, 495, 200)},
    "AX-130": {"area": 38,  "spill": 0,  "type": "purple", "box": (465, 130, 545, 200)},
    "AX-131": {"area": 91,  "spill": 0,  "type": "purple", "box": (520, 160, 615, 250)},
    "AX-132": {"area": 92,  "spill": 0,  "type": "purple", "box": (585, 175, 685, 270)},
    "AX-133": {"area": 92,  "spill": 0,  "type": "purple", "box": (650, 200, 750, 295)},
    "AX-134": {"area": 92,  "spill": 0,  "type": "purple", "box": (710, 240, 805, 330)},
    "AX-135": {"area": 92,  "spill": 0,  "type": "purple", "box": (760, 290, 860, 380)},
    "AX-136": {"area": 92,  "spill": 0,  "type": "purple", "box": (800, 345, 890, 435)},
    "AX-137": {"area": 92,  "spill": 0,  "type": "purple", "box": (830, 410, 915, 500)},
    "AX-138": {"area": 91,  "spill": 0,  "type": "purple", "box": (840, 475, 935, 565)},
    "AX-139": {"area": 38,  "spill": 0,  "type": "purple", "box": (875, 540, 955, 615)},
    "AX-140": {"area": 38,  "spill": 0,  "type": "purple", "box": (875, 595, 955, 670)},
    "AX-141": {"area": 38,  "spill": 0,  "type": "purple", "box": (875, 650, 955, 725)},
    "AX-142": {"area": 38,  "spill": 0,  "type": "purple", "box": (875, 700, 955, 780)},
    "AX-143": {"area": 38,  "spill": 0,  "type": "purple", "box": (875, 760, 955, 835)},
    "AX-144": {"area": 38,  "spill": 0,  "type": "purple", "box": (875, 810, 955, 890)},
    "BX-101": {"area": 74,  "spill": 0,  "type": "blue",   "box": (330, 555, 460, 630)},
    "BX-102": {"area": 83,  "spill": 0,  "type": "blue",   "box": (225, 540, 340, 620)},
    "BX-103": {"area": 42,  "spill": 0,  "type": "blue",   "box": (210, 595, 300, 675)},
    "BX-104": {"area": 42,  "spill": 0,  "type": "blue",   "box": (210, 650, 300, 725)},
    "BX-105": {"area": 42,  "spill": 0,  "type": "blue",   "box": (210, 700, 300, 780)},
    "BX-106": {"area": 42,  "spill": 0,  "type": "blue",   "box": (210, 755, 300, 835)},
    "BX-107": {"area": 74,  "spill": 20, "type": "blue",   "box": (210, 835, 305, 985)},
    "BX-108": {"area": 71,  "spill": 24, "type": "blue",   "box": (310, 860, 400, 985)},
    "BX-109": {"area": 54,  "spill": 0,  "type": "blue",   "box": (335, 800, 425, 885)},
    "BX-110": {"area": 55,  "spill": 0,  "type": "blue",   "box": (335, 750, 425, 830)},
}


def get_system_font(size):
    for path in [
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arial.ttf"
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def generate_sheet_for_unit(
    unit_code: str,
    template_img: Image.Image,
    layout_pil: Image.Image,
    floor_text: str = "First Floor",
    area_override: float = None,
    spill_override: float = None,
    custom_unit_img: Image.Image = None
) -> Image.Image:
    info = FIRST_FLOOR_UNITS[unit_code]
    area_val = float(area_override) if area_override is not None else float(info["area"])
    spill_val = float(spill_override) if spill_override is not None else float(info["spill"])

    lw, lh = layout_pil.size
    bx1, by1, bx2, by2 = info["box"]
    # تحويل الإحداثيات النسبية (من 1000) إلى مقاس الصورة الفعلي بدقة خفيفة جداً
    rx1 = int((bx1 / 1000.0) * lw)
    ry1 = int((by1 / 1000.0) * lh)
    rx2 = int((bx2 / 1000.0) * lw)
    ry2 = int((by2 / 1000.0) * lh)

    if custom_unit_img is not None:
        unit_img = custom_unit_img.convert("RGB")
    else:
        # قص مباشر بدون عناء وتكبير ناعم وسريع
        crop = layout_pil.crop((rx1, ry1, rx2, ry2))
        unit_img = crop.resize((crop.width * 3, crop.height * 3), Image.Resampling.BILINEAR)
        draw_u = ImageDraw.Draw(unit_img)
        f_u = get_system_font(28)
        ub = f_u.getbbox(unit_code)
        draw_u.text((unit_img.width // 2 - (ub[2] - ub[0]) // 2, unit_img.height // 2 - (ub[3] - ub[1]) // 2), unit_code, fill=BLACK_LINE, font=f_u)

    canvas = template_img.copy().convert("RGB")
    draw = ImageDraw.Draw(canvas)
    font_main = get_system_font(52)
    font_sup = get_system_font(34)
    font_floor = get_system_font(58)

    if floor_text.strip() != "First Floor":
        draw.rectangle([950, 35, 1550, 130], fill=WHITE_FILL)
        fb = font_floor.getbbox(floor_text)
        fw = fb[2] - fb[0]
        draw.text((1240 - fw // 2, 45), floor_text, fill=BLACK_LINE, font=font_floor)

    # لصق رسمة الوحدة في المكان المخصص
    uw, uh = unit_img.size
    scale = min(1223 / uw, 1213 / uh)
    new_w, new_h = int(uw * scale), int(uh * scale)
    u_resized = unit_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
    canvas.paste(u_resized, (1232 - new_w // 2, 1143 - new_h // 2))

    # Key Plan خفيف جداً بدون مصفوفات معقدة
    kp_scale = 931 / layout_pil.height
    kp_w, kp_h = int(layout_pil.width * kp_scale), int(layout_pil.height * kp_scale)
    kp_resized = layout_pil.resize((kp_w, kp_h), Image.Resampling.BILINEAR)
    
    # رسم إطار أحمر خفيف مباشر على الـ Key Plan
    draw_kp = ImageDraw.Draw(kp_resized)
    draw_kp.rectangle(
        [int(rx1 * kp_scale), int(ry1 * kp_scale), int(rx2 * kp_scale), int(ry2 * kp_scale)],
        outline=(217, 95, 108), width=4
    )
    canvas.paste(kp_resized, (1244 - kp_w // 2, 2261))

    # كتابة الفوتر والمساحات
    draw.rectangle([1185, 3305, 1765, 3480], fill=WHITE_FILL)
    cb = font_main.getbbox(unit_code)
    draw.text((1474 - (cb[2] - cb[0]) // 2, 3363), unit_code, fill=BLACK_LINE, font=font_main)

    draw.rectangle([1775, 3230, 2450, 3480], fill=WHITE_FILL)
    a_str = f"{int(area_val)}" if area_val.is_integer() else f"{area_val}"
    txt_main = f"Gross area = {a_str} m"
    tb = font_main.getbbox(txt_main)
    tw = tb[2] - tb[0]
    sb = font_sup.getbbox("2")
    sw = sb[2] - sb[0]
    start_x = 2114 - (tw + sw + 2) // 2
    draw.text((start_x, 3325), txt_main, fill=BLACK_LINE, font=font_main)
    draw.text((start_x + tw + 2, 3325 - 6), "2", fill=BLACK_LINE, font=font_sup)

    return canvas


def load_default_bytes(uploaded_file, default_filenames):
    if uploaded_file is not None:
        return uploaded_file.read()
    for fname in default_filenames:
        if os.path.exists(fname):
            with open(fname, "rb") as f:
                return f.read()
    return None


# -------------------------------------------------------------
# Main Streamlit UI
# -------------------------------------------------------------
st.title("🏢 المولّد الأوتوماتيكي للوحات الوحدات التعاقدية (Auto Unit Sheet Generator)")

with st.sidebar:
    st.header("📂 ملفات المخطط والقالب")
    up_layout = st.file_uploader("ارفع مخطط الدور (Layout)", type=["jpg", "jpeg", "png"])
    up_template = st.file_uploader("ارفع القالب الفارغ (MAIN TEMPLATE)", type=["jpg", "jpeg", "png"])
    floor_name = st.text_input("اسم الدور", value="First Floor")

template_bytes = load_default_bytes(up_template, ["MAIN TEMPALTE.jpg", "MAIN TEMPLATE.jpg", "template.jpg"])
layout_bytes = load_default_bytes(up_layout, ["ETAJE-AX-BX-01-FIRST FLOOR - WITH AREA.jpg", "layout.jpg"])

if template_bytes is None or layout_bytes is None:
    st.info("👈 يرجى رفع ملف **مخطط الدور** وملف **القالب** من القائمة الجانبية للبدء.")
    st.stop()

template_img = Image.open(io.BytesIO(template_bytes)).convert("RGB")
# قراءة الصورة بمقاس متوازن تماماً يمنع الـ Crash نهائياً
layout_pil = Image.open(io.BytesIO(layout_bytes)).convert("RGB")
if layout_pil.width > 2000:
    layout_pil = layout_pil.resize((2000, int(2000 * layout_pil.height / layout_pil.width)), Image.Resampling.BILINEAR)

tab_single, tab_batch = st.tabs(["🎯 توليد وحدة منفردة", "📦 توليد دفعة واحدة (ZIP)"])

with tab_single:
    col_ctrl, col_preview = st.columns([1, 2])
    with col_ctrl:
        all_codes = list(FIRST_FLOOR_UNITS.keys())
        selected_code = st.selectbox("اختر كود الوحدة:", all_codes)
        u_info = FIRST_FLOOR_UNITS[selected_code]

        with st.expander("تعديل يدوي"):
            area_ov = st.number_input("المساحة (m²)", value=float(u_info["area"]), step=1.0)
            spill_ov = st.number_input("التراس (m²)", value=float(u_info["spill"]), step=1.0)

        sheet_img = generate_sheet_for_unit(
            unit_code=selected_code,
            template_img=template_img,
            layout_pil=layout_pil,
            floor_text=floor_name,
            area_override=area_ov,
            spill_override=spill_ov
        )

        buf_jpg = io.BytesIO()
        sheet_img.save(buf_jpg, format="JPEG", quality=90)
        st.download_button(
            label=f"📥 تحميل لوحة {selected_code} (JPG)",
            data=buf_jpg.getvalue(),
            file_name=f"{selected_code}.jpg",
            mime="image/jpeg",
            use_container_width=True,
            type="primary"
        )

    with col_preview:
        st.image(sheet_img, caption=f"معاينة - {selected_code}", use_container_width=True)

with tab_batch:
    selected_batch = st.multiselect("اختر الوحدات:", options=list(FIRST_FLOOR_UNITS.keys()), default=["AX-101", "AX-102", "AX-103"])
    if st.button("🚀 توليد وحزم الملفات", type="primary", disabled=(len(selected_batch) == 0)):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for code in selected_batch:
                s_im = generate_sheet_for_unit(
                    unit_code=code,
                    template_img=template_img,
                    layout_pil=layout_pil,
                    floor_text=floor_name
                )
                img_bytes = io.BytesIO()
                s_im.save(img_bytes, format="JPEG", quality=85)
                zf.writestr(f"{code}.jpg", img_bytes.getvalue())

        st.success("تم التوليد بنجاح!")
        st.download_button("📦 تحميل ملف ZIP", data=zip_buf.getvalue(), file_name="Units_Annexes.zip", mime="application/zip", use_container_width=True)
