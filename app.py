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
PURPLE_FILL = (216, 190, 215)
BLUE_FILL = (203, 230, 251)
BLACK_LINE = (0, 0, 0)
WHITE_FILL = (255, 255, 255)

# -------------------------------------------------------------
# Complete Database of First-Floor Units (Optimized Coordinates)
# -------------------------------------------------------------
FIRST_FLOOR_UNITS = {
    "AX-101": {"area": 103, "spill": 0,  "type": "purple", "center": (905, 931)},
    "AX-102": {"area": 52,  "spill": 0,  "type": "purple", "center": (825, 931)},
    "AX-103": {"area": 52,  "spill": 0,  "type": "purple", "center": (774, 931)},
    "AX-104": {"area": 103, "spill": 0,  "type": "purple", "center": (693, 931)},
    "AX-105": {"area": 38,  "spill": 0,  "type": "purple", "center": (679, 851)},
    "AX-106": {"area": 38,  "spill": 0,  "type": "purple", "center": (679, 799)},
    "AX-107": {"area": 38,  "spill": 0,  "type": "purple", "center": (679, 746)},
    "AX-108": {"area": 38,  "spill": 0,  "type": "purple", "center": (679, 693)},
    "AX-109": {"area": 39,  "spill": 0,  "type": "purple", "center": (679, 640)},
    "AX-110": {"area": 52,  "spill": 0,  "type": "purple", "center": (667, 588)},
    "AX-111": {"area": 102, "spill": 0,  "type": "purple", "center": (710, 525)},
    "AX-112": {"area": 103, "spill": 0,  "type": "purple", "center": (684, 462)},
    "AX-113": {"area": 103, "spill": 0,  "type": "purple", "center": (635, 412)},
    "AX-114": {"area": 104, "spill": 0,  "type": "purple", "center": (571, 386)},
    "AX-115": {"area": 51,  "spill": 0,  "type": "purple", "center": (509, 430)},
    "AX-116": {"area": 39,  "spill": 0,  "type": "purple", "center": (456, 418)},
    "AX-117": {"area": 39,  "spill": 0,  "type": "purple", "center": (403, 418)},
    "AX-118": {"area": 39,  "spill": 0,  "type": "purple", "center": (351, 418)},
    "AX-119": {"area": 39,  "spill": 0,  "type": "purple", "center": (298, 418)},
    "AX-120": {"area": 39,  "spill": 0,  "type": "purple", "center": (245, 418)},
    "AX-121": {"area": 121, "spill": 0,  "type": "purple", "center": (159, 404)},
    "AX-122": {"area": 61,  "spill": 0,  "type": "purple", "center": (159, 324)},
    "AX-123": {"area": 61,  "spill": 0,  "type": "purple", "center": (159, 272)},
    "AX-124": {"area": 121, "spill": 0,  "type": "purple", "center": (159, 191)},
    "AX-125": {"area": 38,  "spill": 0,  "type": "purple", "center": (245, 177)},
    "AX-126": {"area": 38,  "spill": 0,  "type": "purple", "center": (298, 178)},
    "AX-127": {"area": 38,  "spill": 0,  "type": "purple", "center": (351, 177)},
    "AX-128": {"area": 38,  "spill": 0,  "type": "purple", "center": (403, 178)},
    "AX-129": {"area": 38,  "spill": 0,  "type": "purple", "center": (456, 177)},
    "AX-130": {"area": 38,  "spill": 0,  "type": "purple", "center": (509, 177)},
    "AX-131": {"area": 91,  "spill": 0,  "type": "purple", "center": (571, 207)},
    "AX-132": {"area": 92,  "spill": 0,  "type": "purple", "center": (638, 221)},
    "AX-133": {"area": 92,  "spill": 0,  "type": "purple", "center": (703, 248)},
    "AX-134": {"area": 92,  "spill": 0,  "type": "purple", "center": (760, 287)},
    "AX-135": {"area": 92,  "spill": 0,  "type": "purple", "center": (810, 336)},
    "AX-136": {"area": 92,  "spill": 0,  "type": "purple", "center": (848, 394)},
    "AX-137": {"area": 92,  "spill": 0,  "type": "purple", "center": (875, 458)},
    "AX-138": {"area": 91,  "spill": 0,  "type": "purple", "center": (889, 525)},
    "AX-139": {"area": 38,  "spill": 0,  "type": "purple", "center": (920, 588)},
    "AX-140": {"area": 38,  "spill": 0,  "type": "purple", "center": (919, 640)},
    "AX-141": {"area": 38,  "spill": 0,  "type": "purple", "center": (919, 693)},
    "AX-142": {"area": 38,  "spill": 0,  "type": "purple", "center": (919, 746)},
    "AX-143": {"area": 38,  "spill": 0,  "type": "purple", "center": (919, 799)},
    "AX-144": {"area": 38,  "spill": 0,  "type": "purple", "center": (919, 851)},
    "BX-101": {"area": 74,  "spill": 0,  "type": "blue",   "center": (374, 599)},
    "BX-102": {"area": 83,  "spill": 0,  "type": "blue",   "center": (271, 586)},
    "BX-103": {"area": 42,  "spill": 0,  "type": "blue",   "center": (256, 640)},
    "BX-104": {"area": 42,  "spill": 0,  "type": "blue",   "center": (256, 693)},
    "BX-105": {"area": 42,  "spill": 0,  "type": "blue",   "center": (256, 746)},
    "BX-106": {"area": 42,  "spill": 0,  "type": "blue",   "center": (256, 799)},
    "BX-107": {"area": 74,  "spill": 20, "type": "blue",   "center": (259, 875)},
    "BX-108": {"area": 71,  "spill": 24, "type": "blue",   "center": (363, 905)},
    "BX-109": {"area": 54,  "spill": 0,  "type": "blue",   "center": (380, 852)},
    "BX-110": {"area": 55,  "spill": 0,  "type": "blue",   "center": (381, 798)},
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


@st.cache_data
def prepare_layout_arrays(layout_bytes):
    """تصغير وتجهيز مصفوفات الصورة بحجم خفيف جداً يمنع استهلاك الـ RAM ويقضي على الـ Oh No"""
    pil_img = Image.open(io.BytesIO(layout_bytes)).convert("RGB")
    # تصغير اللوحة مقدماً لحماية الذاكرة (Memory Safe)
    pil_img = pil_img.resize((1200, 1230), Image.Resampling.BILINEAR)
    arr = np.array(pil_img)

    purple_mask = (arr[:, :, 0] > 180) & (arr[:, :, 1] < 210) & (arr[:, :, 2] > 180)
    blue_mask = (arr[:, :, 0] < 220) & (arr[:, :, 1] > 200) & (arr[:, :, 2] > 230)

    _, labeled_p = cv2.connectedComponents(purple_mask.astype(np.uint8))
    _, labeled_b = cv2.connectedComponents(blue_mask.astype(np.uint8))

    return arr, labeled_p, labeled_b


def generate_sheet_for_unit(
    unit_code: str,
    template_img: Image.Image,
    arr_clean: np.ndarray,
    labeled_p: np.ndarray,
    labeled_b: np.ndarray,
    floor_text: str = "First Floor",
    area_override: float = None,
    spill_override: float = None,
    custom_unit_img: Image.Image = None
) -> Image.Image:
    info = FIRST_FLOOR_UNITS[unit_code]
    area_val = float(area_override) if area_override is not None else float(info["area"])
    spill_val = float(spill_override) if spill_override is not None else float(info["spill"])

    lbl_arr = labeled_p if info["type"] == "purple" else labeled_b
    cx, cy = info["center"]

    # البحث عن الكتل البيكسلية بدقة خفيفة
    r = 20
    win = lbl_arr[max(0, cy - r):min(lbl_arr.shape[0], cy + r + 1), max(0, cx - r):min(lbl_arr.shape[1], cx + r + 1)]
    vals = win[win > 0]
    comp_id = int(np.bincount(vals).argmax()) if len(vals) > 0 else 0
    comp_mask = (lbl_arr == comp_id) if comp_id > 0 else np.zeros_like(lbl_arr, dtype=bool)

    if custom_unit_img is not None:
        unit_img = custom_unit_img.convert("RGB")
    else:
        ys, xs = np.where(comp_mask)
        if len(ys) > 0:
            x1, y1 = max(0, xs.min() - 8), max(0, ys.min() - 8)
            x2, y2 = min(arr_clean.shape[1], xs.max() + 8), min(arr_clean.shape[0], ys.max() + 8)
            crop = arr_clean[y1:y2, x1:x2].copy()
            crop[~comp_mask[y1:y2, x1:x2]] = [255, 255, 255]
        else:
            crop = np.full((300, 300, 3), 255, dtype=np.uint8)

        # تكبير ناعم وسريع للوحة الوحدة
        h_s, w_s = crop.shape[:2]
        up = cv2.resize(crop, (int(w_s * 3), int(h_s * 3)), interpolation=cv2.INTER_LINEAR)
        unit_img = Image.fromarray(up)
        draw_u = ImageDraw.Draw(unit_img)
        f_u = get_system_font(30)
        ub = f_u.getbbox(unit_code)
        draw_u.text(((w_s * 3) // 2 - (ub[2] - ub[0]) // 2, (h_s * 3) // 2 - (ub[3] - ub[1]) // 2), unit_code, fill=BLACK_LINE, font=f_u)

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

    # لصق رسمة الوحدة
    uw, uh = unit_img.size
    scale = min(1223 / uw, 1213 / uh)
    new_w, new_h = int(uw * scale), int(uh * scale)
    u_resized = unit_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
    canvas.paste(u_resized, (1232 - new_w // 2, 1143 - new_h // 2))

    # لصق Key Plan مع تظليل أحمر خفيف
    arr_k = arr_clean.copy()
    ys_h, xs_h = np.where(comp_mask)
    if len(ys_h) > 0:
        cv2.rectangle(arr_k, (xs_h.min() - 2, ys_h.min() - 2), (xs_h.max() + 2, ys_h.max() + 2), (217, 95, 108), 4)

    kp_crop = Image.fromarray(arr_k)
    kw, kh = kp_crop.size
    kp_scale = 931 / kh
    kp_resized = kp_crop.resize((int(kw * kp_scale), int(kh * kp_scale)), Image.Resampling.BILINEAR)
    canvas.paste(kp_resized, (1244 - kp_resized.width // 2, 2261))

    # كتابة بيانات الكود والمساحة في الفوتر بدقة
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
arr_clean, labeled_p, labeled_b = prepare_layout_arrays(layout_bytes)

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
            arr_clean=arr_clean,
            labeled_p=labeled_p,
            labeled_b=labeled_b,
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
                    arr_clean=arr_clean,
                    labeled_p=labeled_p,
                    labeled_b=labeled_b,
                    floor_text=floor_name
                )
                img_bytes = io.BytesIO()
                s_im.save(img_bytes, format="JPEG", quality=85)
                zf.writestr(f"{code}.jpg", img_bytes.getvalue())

        st.success("تم التوليد بنجاح!")
        st.download_button("📦 تحميل ملف ZIP", data=zip_buf.getvalue(), file_name="Units_Annexes.zip", mime="application/zip", use_container_width=True)
