import streamlit as st
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy.ndimage import label, binary_fill_holes, binary_dilation, binary_erosion
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
GRAY_WALL = (128, 128, 128)
BLACK_LINE = (0, 0, 0)
WHITE_FILL = (255, 255, 255)
RED_HIGHLIGHT = (217, 95, 108)

# -------------------------------------------------------------
# Complete Database of All 53 First-Floor Units (AX & BX)
# Automatically maps every unit code to its exact location,
# area, terrace/spill-out area, and category on the Floor Layout!
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


def get_system_font(size):
    """Loads a clean Sans-Serif font across Linux/Windows/macOS."""
    font_candidates = [
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arial.ttf",
        "Arial.ttf"
    ]
    for path in font_candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


@st.cache_data
def segment_floor_layout(arr_layout: np.ndarray):
    """
    Automatically segments the floor layout image into distinct unit polygons
    (Purple Clinics, Blue Offices, Green Terraces) using connected components.
    """
    arr = arr_layout.copy()
    # Mask out top-left Room Legend if present
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

    labeled_p, _ = label(purple_mask)
    labeled_b, _ = label(blue_mask)
    labeled_g, _ = label(green_mask)
    all_units_mask = purple_mask | blue_mask | green_mask

    return arr, labeled_p, labeled_b, labeled_g, all_units_mask


def find_component_at(lbl_arr: np.ndarray, cx: int, cy: int, scale_x: float = 1.0, scale_y: float = 1.0):
    """Finds the component ID around scaled coordinates (cx, cy)."""
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
    terrace_mask: np.ndarray = None,
    terrace_code: str = None,
    clean_cad_mode: bool = True
) -> Image.Image:
    """
    Automatically isolates a single unit (plus optional terrace) from the floor layout,
    removes neighboring units & corridor backgrounds, cleans interior text,
    and upscales to a crisp high-resolution CAD diagram.
    """
    filled = binary_fill_holes(comp_mask)
    ys, xs = np.where(filled)
    cx, cy = int(np.mean(xs)), int(np.mean(ys))

    total_mask = filled.copy()
    if terrace_mask is not None:
        t_filled = binary_fill_holes(terrace_mask)
        total_mask = total_mask | t_filled

    tys, txs = np.where(total_mask)
    margin = 8
    x1 = max(0, int(txs.min()) - margin)
    y1 = max(0, int(tys.min()) - margin)
    x2 = min(arr_clean.shape[1], int(txs.max()) + margin + 1)
    y2 = min(arr_clean.shape[0], int(tys.max()) + margin + 1)

    sub = arr_clean[y1:y2, x1:x2].copy()
    if not clean_cad_mode:
        return Image.fromarray(sub)

    sub_unit = filled[y1:y2, x1:x2]
    sub_total = total_mask[y1:y2, x1:x2]
    sub_other = (all_units_mask[y1:y2, x1:x2]) & (~sub_total)

    # Keep structural walls/columns/shafts belonging to this unit (within 6px)
    keep_zone = binary_dilation(sub_total, iterations=6)
    is_corridor = (sub[:, :, 0] > 228) & (sub[:, :, 1] > 228) & (sub[:, :, 2] > 225) & (~sub_total)

    sub[~keep_zone] = [255, 255, 255]
    sub[sub_other] = [255, 255, 255]
    sub[is_corridor] = [255, 255, 255]

    # Replace low-res text inside the unit interior while preserving door swing arcs near walls
    eroded_deep = binary_erosion(sub_unit, iterations=12)
    lcx, lcy = cx - x1, cy - y1
    text_box = np.zeros_like(sub_unit)
    text_box[max(0, lcy - 18):min(sub.shape[0], lcy + 18), max(0, lcx - 28):min(sub.shape[1], lcx + 28)] = True
    sub[(eroded_deep | text_box) & sub_unit] = fill_rgb

    if terrace_mask is not None:
        sub_terr = binary_fill_holes(terrace_mask)[y1:y2, x1:x2]
        ty_s, tx_s = np.where(sub_terr)
        tcx, tcy = int(np.mean(tx_s)), int(np.mean(ty_s))
        t_box = np.zeros_like(sub_terr)
        t_box[max(0, tcy - 15):min(sub.shape[0], tcy + 15), max(0, tcx - 26):min(sub.shape[1], tcx + 26)] = True
        sub[t_box & sub_terr] = GREEN_FILL

    # High-res 8x Lanczos upscaling + unsharp mask for crisp CAD lines
    scale = 8
    h_s, w_s = sub.shape[:2]
    up = cv2.resize(sub, (w_s * scale, h_s * scale), interpolation=cv2.INTER_LANCZOS4)
    blur = cv2.GaussianBlur(up, (0, 0), 2.0)
    up_sharp = cv2.addWeighted(up, 1.8, blur, -0.8, 0)

    im_up = Image.fromarray(up_sharp)
    draw = ImageDraw.Draw(im_up)
    f_u = get_system_font(38)
    ub = f_u.getbbox(unit_code)
    tw, th = ub[2] - ub[0], ub[3] - ub[1]
    draw.text((lcx * scale - tw // 2, lcy * scale - th // 2), unit_code, fill=BLACK_LINE, font=f_u)

    if terrace_mask is not None and terrace_code:
        f_t = get_system_font(24)
        tb = f_t.getbbox(terrace_code)
        ttw, tth = tb[2] - tb[0], tb[3] - tb[1]
        draw.text((tcx * scale - ttw // 2, tcy * scale - tth // 2), terrace_code, fill=BLACK_LINE, font=f_t)

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
    """Generates the complete 2480x3508 contract sheet for any selected unit code."""
    info = FIRST_FLOOR_UNITS[unit_code]
    area_val = float(area_override) if area_override is not None else float(info["area"])
    spill_val = float(spill_override) if spill_override is not None else float(info["spill"])

    h_lay, w_lay = arr_clean.shape[:2]
    sx, sy = w_lay / 998.0, h_lay / 1024.0

    lbl_arr = labeled_p if info["type"] == "purple" else labeled_b
    fill_rgb = PURPLE_FILL if info["type"] == "purple" else BLUE_FILL

    comp_id = find_component_at(lbl_arr, info["center"][0], info["center"][1], sx, sy)
    comp_mask = (lbl_arr == comp_id)

    terrace_mask = None
    terrace_label = info.get("terrace_label")
    if "terrace_center" in info and spill_val > 0:
        t_id = find_component_at(labeled_g, info["terrace_center"][0], info["terrace_center"][1], sx, sy)
        if t_id > 0:
            terrace_mask = (labeled_g == t_id)

    # 1. Get Top Unit Graphic
    if custom_unit_img is not None:
        unit_img = custom_unit_img.convert("RGB")
    else:
        unit_img = isolate_and_upscale_unit(
            arr_clean=arr_clean,
            comp_mask=comp_mask,
            all_units_mask=all_units_mask,
            fill_rgb=fill_rgb,
            unit_code=unit_code,
            terrace_mask=terrace_mask,
            terrace_code=terrace_label,
            clean_cad_mode=clean_cad_mode
        )

    # 2. Prepare Template Canvas
    canvas = template_img.copy().convert("RGB")
    draw = ImageDraw.Draw(canvas)
    font_main = get_system_font(52)
    font_sup = get_system_font(34)
    font_floor = get_system_font(58)

    # Update Floor Title if changed
    if floor_text.strip() != "First Floor":
        draw.rectangle([950, 35, 1550, 130], fill=WHITE_FILL)
        fb = font_floor.getbbox(floor_text)
        fw = fb[2] - fb[0]
        draw.text((1240 - fw // 2, 45), floor_text, fill=BLACK_LINE, font=font_floor)
        draw.line([(1240 - fw // 2, 105), (1240 + fw // 2, 105)], fill=BLACK_LINE, width=3)

    # Paste Top Unit Plan
    uw, uh = unit_img.size
    max_w, max_h = 1223, 1213
    scale = min(max_w / uw, max_h / uh)
    new_w, new_h = int(uw * scale), int(uh * scale)
    u_resized = unit_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    canvas.paste(u_resized, (1232 - new_w // 2, 1143 - new_h // 2))

    # 3. Highlight Exact Unit Polygon on Key Plan
    arr_k = arr_clean.copy()
    highlight_poly = binary_fill_holes(comp_mask)
    if terrace_mask is not None:
        highlight_poly = highlight_poly | binary_fill_holes(terrace_mask)
    # Dilate by 2px so surrounding wall borders of the selected unit also tint cleanly like reference AX-101
    highlight_poly = binary_dilation(highlight_poly, iterations=2)

    ys_h, xs_h = np.where(highlight_poly)
    hx1, hy1, hx2, hy2 = xs_h.min(), ys_h.min(), xs_h.max() + 1, ys_h.max() + 1
    region = arr_k[hy1:hy2, hx1:hx2].astype(float)
    sub_poly = highlight_poly[hy1:hy2, hx1:hx2]
    not_white = ~((region[:, :, 0] > 240) & (region[:, :, 1] > 240) & (region[:, :, 2] > 240))
    active = sub_poly & not_white

    lum = (0.299 * region[:, :, 0] + 0.587 * region[:, :, 1] + 0.114 * region[:, :, 2]) / 230.0
    lum = np.clip(lum, 0, 1.05)

    region[:, :, 0] = np.where(active, np.clip(217 * lum, 0, 255), region[:, :, 0])
    region[:, :, 1] = np.where(active, np.clip(95 * lum, 0, 255), region[:, :, 1])
    region[:, :, 2] = np.where(active, np.clip(108 * lum, 0, 255), region[:, :, 2])
    arr_k[hy1:hy2, hx1:hx2] = region.astype(np.uint8)

    kp_crop = Image.fromarray(arr_k[int(100 * sy):int(1022 * sy), int(90 * sx):int(998 * sx)])
    kw, kh = kp_crop.size
    kp_scale = 931 / kh
    kp_w, kp_h = int(kw * kp_scale), int(kh * kp_scale)
    kp_resized = kp_crop.resize((kp_w, kp_h), Image.Resampling.LANCZOS)
    canvas.paste(kp_resized, (1244 - kp_w // 2, 2261))

    # 4. Update Title Block: Unit Code & Area
    draw.rectangle([1185, 3305, 1765, 3480], fill=WHITE_FILL)
    cb = font_main.getbbox(unit_code)
    cw = cb[2] - cb[0]
    draw.text((1474 - cw // 2, 3363), unit_code, fill=BLACK_LINE, font=font_main)

    draw.rectangle([1775, 3230, 2450, 3480], fill=WHITE_FILL)
    a_str = f"{int(area_val)}" if area_val.is_integer() else f"{area_val}"
    s_str = f"{int(spill_val)}" if spill_val.is_integer() else f"{spill_val}"

    if spill_val > 0:
        l1 = f"Area = {a_str} m"
        tb1 = font_main.getbbox(l1)
        tw1 = tb1[2] - tb1[0]
        draw.text((1821, 3285), l1, fill=BLACK_LINE, font=font_main)
        draw.text((1821 + tw1 + 2, 3285 - 6), "2", fill=BLACK_LINE, font=font_sup)

        l2 = f"Spill Out Area = {s_str} m"
        tb2 = font_main.getbbox(l2)
        tw2 = tb2[2] - tb2[0]
        draw.text((1821, 3367), l2, fill=BLACK_LINE, font=font_main)
        draw.text((1821 + tw2 + 2, 3367 - 6), "2", fill=BLACK_LINE, font=font_sup)
    else:
        txt_main = f"Gross area = {a_str} m"
        tb = font_main.getbbox(txt_main)
        tw = tb[2] - tb[0]
        sb = font_sup.getbbox("2")
        sw = sb[2] - sb[0]
        start_x = 2114 - (tw + sw + 2) // 2
        y_pos = 3325
        draw.text((start_x, y_pos), txt_main, fill=BLACK_LINE, font=font_main)
        draw.text((start_x + tw + 2, y_pos - 6), "2", fill=BLACK_LINE, font=font_sup)

    return canvas


def load_default_or_uploaded(uploaded_file, default_filenames):
    """Loads an image from Streamlit uploader or falls back to repo files."""
    if uploaded_file is not None:
        return Image.open(uploaded_file).convert("RGB")
    for fname in default_filenames:
        if os.path.exists(fname):
            return Image.open(fname).convert("RGB")
    return None


# -------------------------------------------------------------
# Main Streamlit UI
# -------------------------------------------------------------
st.title("🏢 المولّد الأوتوماتيكي للوحات الوحدات التعاقدية (Auto Unit Sheet Generator)")
st.markdown(
    "ارفع **مخطط الدور (Layout)** فقط (أو استخدم المخطط المدمج)، وسيقوم البرنامج **أوتوماتيكياً** بقص الوحدة، تنظيفها، تظليل مكانها على الـ Key Plan، وكتابة الكود والمساحة بدون أي إدخال يدوي!"
)

with st.sidebar:
    st.header("📂 1. ملفات المخطط والقالب")
    up_layout = st.file_uploader("ارفع مخطط الدور (Layout With Areas)", type=["jpg", "jpeg", "png"])
    up_template = st.file_uploader("اختياري: قالب اللوحة الفارغ (MAIN TEMPALTE)", type=["jpg", "jpeg", "png"])
    floor_name = st.text_input("اسم الدور (Floor Title)", value="First Floor")
    clean_cad_mode = st.toggle("تنظيف وتكبير رسمة الوحدة تلقائياً (Auto-Clean CAD)", value=True)

template_img = load_default_or_uploaded(up_template, [
    "MAIN TEMPALTE.jpg",
    "user_uploaded_files/ttl=63d/user_uploaded/MAIN TEMPALTE.jpg"
])
layout_img = load_default_or_uploaded(up_layout, [
    "ETAJE-AX-BX-01-FIRST FLOOR - WITH AREA.jpg",
    "user_uploaded_files/ttl=63d/user_uploaded/ETAJE-AX-BX-01-FIRST FLOOR - WITH AREA.jpg"
])

if template_img is None or layout_img is None:
    st.info("👈 يرجى رفع ملف **مخطط الدور (Layout)** وملف **القالب (MAIN TEMPALTE)** من القائمة الجانبية للبدء (أو وضعهما في نفس مجلد `app.py` على GitHub ليعمل البرنامج بدون رفع في كل مرة).")
    st.stop()

# Automatically segment all 53 units from the layout image
arr_clean, labeled_p, labeled_b, labeled_g, all_units_mask = segment_floor_layout(np.array(layout_img))

tab_single, tab_batch = st.tabs([
    "🎯 توليد لوحة وحدة (باختيار الكود فقط)",
    "📦 توليد جميع وحدات الدور دفعة واحدة (Batch ZIP / PDF)"
])

with tab_single:
    col_ctrl, col_preview = st.columns([1, 2])
    with col_ctrl:
        st.subheader("اختر كود الوحدة")
        all_codes = list(FIRST_FLOOR_UNITS.keys())
        selected_code = st.selectbox("كود الوحدة (54 وحدة مسجلة تلقائياً):", all_codes, index=all_codes.index("AX-120"))

        u_info = FIRST_FLOOR_UNITS[selected_code]
        st.caption(f"**المساحة المسجلة تلقائياً:** `{u_info['area']} m²`" + (f" | **التراس:** `{u_info['spill']} m²`" if u_info['spill'] > 0 else ""))

        with st.expander("تعديل يدوي اختياري (في حال الرغبة بتغيير المساحة أو رفع صورة مخصصة)"):
            area_ov = st.number_input("تعديل المساحة (m²)", value=float(u_info["area"]), step=1.0)
            spill_ov = st.number_input("تعديل مساحة التراس / Spill Out (m²)", value=float(u_info["spill"]), step=1.0)
            custom_u_file = st.file_uploader("رفع رسمة منفصلة لهذه الوحدة (اختياري)", type=["jpg", "jpeg", "png"])
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
        sheet_img.save(buf_jpg, format="JPEG", quality=95)
        st.download_button(
            label=f"📥 تحميل لوحة {selected_code} (JPG)",
            data=buf_jpg.getvalue(),
            file_name=f"{selected_code}.jpg",
            mime="image/jpeg",
            use_container_width=True,
            type="primary"
        )

        buf_pdf = io.BytesIO()
        sheet_img.save(buf_pdf, format="PDF", resolution=300.0)
        st.download_button(
            label=f"📄 تحميل لوحة {selected_code} جاهزة للطباعة (PDF)",
            data=buf_pdf.getvalue(),
            file_name=f"{selected_code}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col_preview:
        st.image(sheet_img, caption=f"معاينة اللوحة التعاقدية - {selected_code}", use_container_width=True)

with tab_batch:
    st.subheader("توليد مجموعة وحدات أو الدور بالكامل بضغطة زر")
    selected_batch = st.multiselect(
        "اختر الوحدات المطلوب استخراج لوحاتها (أو اتركها كما هي لتوليد القائمة المختارة):",
        options=list(FIRST_FLOOR_UNITS.keys()),
        default=["AX-101", "AX-102", "AX-103", "AX-104", "AX-120", "BX-107"]
    )
    select_all = st.checkbox("تحديد كل وحدات الدور بالكامل (54 وحدة)")
    if select_all:
        selected_batch = list(FIRST_FLOOR_UNITS.keys())

    if st.button(f"🚀 توليد وحزم {len(selected_batch)} لوحة الآن", type="primary", disabled=(len(selected_batch) == 0)):
        progress = st.progress(0, text="جاري توليد اللوحات أوتوماتيكياً...")
        zip_buf = io.BytesIO()
        pdf_pages = []

        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for idx, code in enumerate(selected_batch):
                progress.progress((idx + 1) / len(selected_batch), text=f"جاري تجهيز لوحة {code} ({idx + 1}/{len(selected_batch)})...")
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
                s_im.save(img_bytes, format="JPEG", quality=95)
                zf.writestr(f"{code}.jpg", img_bytes.getvalue())
                pdf_pages.append(s_im)

        progress.empty()
        st.success(f"تم توليد {len(selected_batch)} لوحة بنجاح!")

        c1, c2 = st.columns(2)
        c1.download_button(
            label=f"📦 تحميل جميع اللوحات كملف مضغوط ({len(selected_batch)} صورة JPG في ZIP)",
            data=zip_buf.getvalue(),
            file_name=f"{floor_name.replace(' ', '_')}_Unit_Sheets.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary"
        )

        if pdf_pages:
            pdf_all_buf = io.BytesIO()
            pdf_pages[0].save(
                pdf_all_buf,
                format="PDF",
                resolution=300.0,
                save_all=True,
                append_images=pdf_pages[1:]
            )
            c2.download_button(
                label=f"📕 تحميل كتاب موحد بجميع اللوحات ({len(selected_batch)} صفحة PDF)",
                data=pdf_all_buf.getvalue(),
                file_name=f"{floor_name.replace(' ', '_')}_All_Units.pdf",
                mime="application/pdf",
                use_container_width=True
            )
