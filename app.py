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
GREEN_FILL = (238, 250, 230)
BLACK_LINE = (0, 0, 0)
WHITE_FILL = (255, 255, 255)

# -------------------------------------------------------------
# Database of All 54 First-Floor Units
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
    "BX-107": {"area": 74,  "spill": 20, "type": "blue",   "center": (259, 875), "terrace_center": (270, 956), "terrace_label": "BX-107 Terrace"},
    "BX-108": {"area": 71,  "spill": 24, "type": "blue",   "center": (363, 905), "terrace_center": (328, 959), "terrace_label": "BX-108 Terrace"},
    "BX-109": {"area": 54,  "spill": 0,  "type": "blue",   "center": (380, 852)},
    "BX-110": {"area": 55,  "spill": 0,  "type": "blue",   "center": (381, 798)},
}


# -------------------------------------------------------------
# Optimized Processing Helpers (Lightweight Memory Usage)
# -------------------------------------------------------------
def get_system_font(size):
    font_candidates = [
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arial.ttf"
    ]
    for path in font_candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


@st.cache_data
def segment_floor_layout(arr_layout: np.ndarray):
    arr = arr_layout.copy()
    h, w = arr.shape[:2]
    arr[0:int(h * 0.145), 0:int(w * 0.086), :] = 255

    purple_mask = (
        ((arr[:, :, 0].astype(int) - arr[:, :, 1].astype(int)) > 16)
        & ((arr[:, :, 2].astype(int) - arr[:, :, 1].astype(int)) > 16)
        & (arr[:, :, 0] > 185)
    )
    blue_mask = (
        ((arr[:, :, 2].astype(int) - arr[:, :, 0].astype(int)) > 25)
        & ((arr[:, :, 1].astype(int) - arr[:, :, 0].astype(int)) > 10)
        & (arr[:, :, 2] > 215)
    )
    green_mask = (
        ((arr[:, :, 1].astype(int) - arr[:, :, 2].astype(int)) > 12)
        & ((arr[:, :, 1].astype(int) - arr[:, :, 0].astype(int)) > 6)
        & (arr[:, :, 1] > 235)
    )

    _, labeled_p = cv2.connectedComponents(purple_mask.astype(np.uint8))
    _, labeled_b = cv2.connectedComponents(blue_mask.astype(np.uint8))
    _, labeled_g = cv2.connectedComponents(green_mask.astype(np.uint8))
    all_units_mask = purple_mask | blue_mask | green_mask

    return arr, labeled_p, labeled_b, labeled_g, all_units_mask


def find_component_at(lbl_arr: np.ndarray, cx: int, cy: int, scale_x: float = 1.0, scale_y: float = 1.0):
    sx, sy = int(cx * scale_x), int(cy * scale_y)
    r = max(10, int(10 * max(scale_x, scale_y)))
    win = lbl_arr[max(0, sy - r):min(lbl_arr.shape[0], sy + r + 1), max(0, sx - r):min(lbl_arr.shape[1], sx + r + 1)]
    vals = win[win > 0]
    if len(vals) == 0:
        return 0
    return int(np.bincount(vals).argmax())


def isolate_and_upscale_unit(
    arr_clean: np.ndarray,
    comp_mask: np.ndarray,
    all_units_mask: np.ndarray,
    fill_rgb: tuple,
    unit_code: str,
    clean_cad_mode: bool = True
) -> Image.Image:
    ys, xs = np.where(comp_mask)
    if len(ys) == 0:
        return Image.fromarray(np.full((300, 300, 3), 255, dtype=np.uint8))

    cx, cy = int(np.mean(xs)), int(np.mean(ys))
    margin = 8
    x1 = max(0, int(xs.min()) - margin)
    y1 = max(0, int(ys.min()) - margin)
    x2 = min(arr_clean.shape[1], int(xs.max()) + margin + 1)
    y2 = min(arr_clean.shape[0], int(ys.max()) + margin + 1)

    sub = arr_clean[y1:y2, x1:x2].copy()
    if not clean_cad_mode:
        return Image.fromarray(sub)

    sub_unit = comp_mask[y1:y2, x1:x2]
    sub_other = (all_units_mask[y1:y2, x1:x2]) & (~sub_unit)

    sub[sub_other] = [255, 255, 255]

    # Memory Safe Resizing (Max 2.5x instead of 8x)
    h_s, w_s = sub.shape[:2]
    scale = 2
    up = cv2.resize(sub, (w_s * scale, h_s * scale), interpolation=cv2.INTER_LINEAR)

    im_up = Image.fromarray(up)
    draw = ImageDraw.Draw(im_up)
    f_u = get_system_font(32)
    ub = f_u.getbbox(unit_code)
    tw, th = ub[2] - ub[0], ub[3] - ub[1]
    lcx, lcy = cx - x1, cy - y1
    draw.text((lcx * scale - tw // 2, lcy * scale - th // 2), unit_code, fill=BLACK_LINE, font=f_u)

    return im_up


def generate_sheet_for_unit(
    unit_code: str,
    template_img: Image.Image,
    arr_clean: np.ndarray,
    labeled_p: np.ndarray,
    labeled_b: np.ndarray,
    labeled_g: np.ndarray,
    all_units_mask: np.ndarray,
    floor_text: str = "First Floor",
    area_override: float = None,
    spill_override: float = None,
    clean_cad_mode: bool = True,
    custom_unit_img: Image.Image = None
) -> Image.Image:
    info = FIRST_FLOOR_UNITS[unit_code]
    area_val = float(area_override) if area_override is not None else float(info["area"])
    spill_val = float(spill_override) if spill_override is not None else float(info["spill"])

    h_lay, w_lay = arr_clean.shape[:2]
    sx, sy = w_lay / 998.0, h_lay / 1024.0

    lbl_arr = labeled_p if info["type"] == "purple" else labeled_b
    fill_rgb = PURPLE_FILL if info["type"] == "purple" else BLUE_FILL

    comp_id = find_component_at(lbl_arr, info["center"][0], info["center"][1], sx, sy)
    if comp_id == 0:
        raise ValueError(f"تعذر العثور على الوحدة {unit_code} في الرسمة. يرجى التأكد من رفع المخطط الصحيح.")
    comp_mask = (lbl_arr == comp_id)

    if custom_unit_img is not None:
        unit_img = custom_unit_img.convert("RGB")
    else:
        unit_img = isolate_and_upscale_unit(
            arr_clean=arr_clean,
            comp_mask=comp_mask,
            all_units_mask=all_units_mask,
            fill_rgb=fill_rgb,
            unit_code=unit_code,
            clean_cad_mode=clean_cad_mode
        )

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

    # Unit Paste
    uw, uh = unit_img.size
    max_w, max_h = 1223, 1213
    scale = min(max_w / uw, max_h / uh)
    new_w, new_h = int(uw * scale), int(uh * scale)
    u_resized = unit_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
    canvas.paste(u_resized, (1232 - new_w // 2, 1143 - new_h // 2))

    # Key Plan Highlight
    arr_k = arr_clean.copy()
    ys_h, xs_h = np.where(comp_mask)
    if len(ys_h) > 0:
        cv2.rectangle(arr_k, (xs_h.min() - 4, ys_h.min() - 4), (xs_h.max() + 4, ys_h.max() + 4), (217, 95, 108), 5)

    kp_crop = Image.fromarray(arr_k[int(100 * sy):int(1022 * sy), int(90 * sx):int(998 * sx)])
    kw, kh = kp_crop.size
    kp_scale = 931 / kh
    kp_w, kp_h = int(kw * kp_scale), int(kh * kp_scale)
    kp_resized = kp_crop.resize((kp_w, kp_h), Image.Resampling.BILINEAR)
    canvas.paste(kp_resized, (1244 - kp_w // 2, 2261))

    # Text & Footer Data
    draw.rectangle([1185, 3305, 1765, 3480], fill=WHITE_FILL)
    cb = font_main.getbbox(unit_code)
    cw = cb[2] - cb[0]
    draw.text((1474 - cw // 2, 3363), unit_code, fill=BLACK_LINE, font=font_main)

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


def load_default_or_uploaded(uploaded_file, default_filenames):
    if uploaded_file is not None:
        return Image.open(uploaded_file).convert("RGB")
    for fname in default_filenames:
        if os.path.exists(fname):
            return Image.open(fname).convert("RGB")
    return None


# -------------------------------------------------------------
# Streamlit Interface
# -------------------------------------------------------------
st.title("🏢 المولّد الأوتوماتيكي للوحات الوحدات التعاقدية (Auto Unit Sheet Generator)")

with st.sidebar:
    st.header("📂 1. ملفات المخطط والقالب")
    up_layout = st.file_uploader("ارفع مخطط الدور (Layout With Areas)", type=["jpg", "jpeg", "png"])
    up_template = st.file_uploader("اختياري: قالب اللوحة الفارغ (MAIN TEMPALTE)", type=["jpg", "jpeg", "png"])
    floor_name = st.text_input("اسم الدور (Floor Title)", value="First Floor")
    clean_cad_mode = st.toggle("تنظيف وتكبير رسمة الوحدة تلقائياً (Auto-Clean CAD)", value=True)

template_img = load_default_or_uploaded(up_template, ["MAIN TEMPALTE.jpg", "MAIN TEMPLATE.jpg", "template.jpg"])
layout_img = load_default_or_uploaded(up_layout, ["ETAJE-AX-BX-01-FIRST FLOOR - WITH AREA.jpg", "layout.jpg"])

if template_img is None or layout_img is None:
    st.info("👈 يرجى رفع ملف **مخطط الدور (Layout)** وملف **القالب (MAIN TEMPALTE)** من القائمة الجانبية للبدء.")
    st.stop()

# Auto-Scale uploaded Layout to prevent OOM
if layout_img.width > 1200:
    layout_img = layout_img.resize((1200, int(1200 * layout_img.height / layout_img.width)), Image.Resampling.BILINEAR)

arr_clean, labeled_p, labeled_b, labeled_g, all_units_mask = segment_floor_layout(np.array(layout_img))

tab_single, tab_batch = st.tabs([
    "🎯 توليد لوحة وحدة (باختيار الكود فقط)",
    "📦 توليد جميع وحدات الدور دفعة واحدة (Batch ZIP / PDF)"
])

with tab_single:
    col_ctrl, col_preview = st.columns([1, 2])
    with col_ctrl:
        all_codes = list(FIRST_FLOOR_UNITS.keys())
        selected_code = st.selectbox("كود الوحدة:", all_codes, index=all_codes.index("AX-120"))
        u_info = FIRST_FLOOR_UNITS[selected_code]

        with st.expander("تعديل يدوي اختياري"):
            area_ov = st.number_input("تعديل المساحة (m²)", value=float(u_info["area"]), step=1.0)
            spill_ov = st.number_input("تعديل مساحة التراس (m²)", value=float(u_info["spill"]), step=1.0)
            custom_u_file = st.file_uploader("رفع رسمة منفصلة للوحدة (اختياري)", type=["jpg", "jpeg", "png"])
            custom_u_img = Image.open(custom_u_file) if custom_u_file else None

        sheet_img = generate_sheet_for_unit(
            unit_code=selected_code,
            template_img=template_img,
            arr_clean=arr_clean,
            labeled_p=labeled_p,
            labeled_b=labeled_b,
            labeled_g=labeled_g,
            all_units_mask=all_units_mask,
            floor_text=floor_name,
            area_override=area_ov,
            spill_override=spill_ov,
            clean_cad_mode=clean_cad_mode,
            custom_unit_img=custom_u_img
        )

        buf_jpg = io.BytesIO()
        sheet_img.save(buf_jpg, format="JPEG", quality=85)
        st.download_button(
            label=f"📥 تحميل لوحة {selected_code} (JPG)",
            data=buf_jpg.getvalue(),
            file_name=f"{selected_code}.jpg",
            mime="image/jpeg",
            type="primary"
        )

    with col_preview:
        st.image(sheet_img, caption=f"معاينة - {selected_code}")

with tab_batch:
    selected_batch = st.multiselect(
        "اختر الوحدات المطلوب استخراج لوحاتها:",
        options=list(FIRST_FLOOR_UNITS.keys()),
        default=["AX-101", "AX-102", "AX-103"]
    )

    if st.button(f"🚀 توليد وحزم {len(selected_batch)} لوحة الآن", type="primary", disabled=(len(selected_batch) == 0)):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for idx, code in enumerate(selected_batch):
                s_im = generate_sheet_for_unit(
                    unit_code=code,
                    template_img=template_img,
                    arr_clean=arr_clean,
                    labeled_p=labeled_p,
                    labeled_b=labeled_b,
                    labeled_g=labeled_g,
                    all_units_mask=all_units_mask,
                    floor_text=floor_name,
                    clean_cad_mode=clean_cad_mode
                )
                img_bytes = io.BytesIO()
                s_im.save(img_bytes, format="JPEG", quality=80)
                zf.writestr(f"{code}.jpg", img_bytes.getvalue())
                del s_im  # Free RAM instantly

        st.success("تم توليد الحزمة بنجاح!")
        st.download_button(
            label="📦 تحميل ZIP لجميع اللوحات",
            data=zip_buf.getvalue(),
            file_name=f"{floor_name}_Units.zip",
            mime="application/zip",
            type="primary"
        )
