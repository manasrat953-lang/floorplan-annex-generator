import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import math

st.set_page_config(
    page_title="Contract Unit Sheet Generator | مولّد لوحات التعاقد",
    page_icon="📐",
    layout="wide"
)

# -------------------------------------------------------------
# Constant Layout & Styling Parameters
# -------------------------------------------------------------
PURPLE_FILL = (216, 190, 215)
BLUE_FILL = (203, 230, 251)
GREEN_FILL = (238, 250, 230)
GRAY_WALL = (128, 128, 128)
BLACK_LINE = (0, 0, 0)
WHITE_FILL = (255, 255, 255)
RED_HIGHLIGHT = (217, 95, 108)

# Preset Unit Configurations
UNIT_PRESETS = {
    "AX-101": {
        "floor": "First Floor",
        "area": 103,
        "spill_out": 0,
        "has_spill_out": False,
        "keyplan_box": (850, 875, 962, 983),
        "type": "preset_img",
        "reference_crop": (850, 875, 962, 983)
    },
    "AX-102": {
        "floor": "First Floor",
        "area": 52,
        "spill_out": 0,
        "has_spill_out": False,
        "keyplan_box": (799, 875, 853, 983),
        "type": "preset_img",
        "reference_crop": (799, 875, 853, 983)
    },
    "AX-103": {
        "floor": "First Floor",
        "area": 52,
        "spill_out": 0,
        "has_spill_out": False,
        "keyplan_box": (745, 875, 800, 983),
        "type": "preset_img",
        "reference_crop": (745, 875, 800, 983)
    },
    "AX-104": {
        "floor": "First Floor",
        "area": 103,
        "spill_out": 0,
        "has_spill_out": False,
        "keyplan_box": (638, 875, 748, 983),
        "type": "mirror_101",
        "reference_crop": (638, 875, 748, 983)
    },
    "AX-120": {
        "floor": "First Floor",
        "area": 39,
        "spill_out": 0,
        "has_spill_out": False,
        "keyplan_box": (213, 377, 273, 461),
        "type": "cad_ax120",
        "reference_crop": (211, 367, 275, 462)
    },
    "BX-107": {
        "floor": "First Floor",
        "area": 74,
        "spill_out": 20,
        "has_spill_out": True,
        "keyplan_box": (212, 824, 297, 986),
        "type": "cad_bx107",
        "reference_crop": (208, 820, 302, 990)
    }
}


def get_system_font(size):
    """Fallback font loader for Linux/Windows/Mac."""
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


def render_ax120_cad():
    """Generates a crisp high-res CAD graphic for unit AX-120."""
    S = 12
    W, H = 64 * S, 96 * S
    im = Image.new("RGB", (W, H), WHITE_FILL)
    d = ImageDraw.Draw(im)
    LW = 4

    def rx(c): return int((c - 212) * S)
    def ry(r): return int((r - 367) * S)

    # 1. Fill interior
    d.rectangle([rx(220), ry(379), rx(270), ry(457)], fill=PURPLE_FILL)

    # 2. Bottom wall
    d.rectangle([rx(220), ry(457) - LW, rx(272), ry(457) + LW], fill=BLACK_LINE)

    # 3. L-shaped Top & Left Wall
    tl_poly = [
        (rx(217), ry(368)), (rx(220), ry(368)), (rx(220), ry(377)),
        (rx(256.5), ry(377)), (rx(256.5), ry(380)), (rx(220), ry(380)),
        (rx(220), ry(439)), (rx(217), ry(439))
    ]
    d.polygon(tl_poly, fill=GRAY_WALL)
    d.line(tl_poly + [tl_poly[0]], fill=BLACK_LINE, width=LW, joint="curve")

    # 4. Shaft & Column
    d.rectangle([rx(213), ry(439), rx(220), ry(448)], fill=GRAY_WALL, outline=BLACK_LINE, width=LW)
    d.rectangle([rx(214.3), ry(440.3), rx(218.7), ry(446.7)], fill=WHITE_FILL, outline=BLACK_LINE, width=LW)
    d.rectangle([rx(213), ry(448), rx(220), ry(461)], fill=GRAY_WALL, outline=BLACK_LINE, width=LW)

    # 5. Right Wall
    r_poly = [
        (rx(268.5), ry(377)), (rx(273), ry(377)), (rx(273), ry(457)),
        (rx(270), ry(457)), (rx(270), ry(380)), (rx(268.5), ry(380))
    ]
    d.polygon(r_poly, fill=GRAY_WALL)
    d.line(r_poly + [r_poly[0]], fill=BLACK_LINE, width=LW, joint="curve")

    # 6. Top Entrance Door
    door_r = rx(268.5) - rx(256.5)
    d.rectangle([rx(268.5) - 10, ry(380), rx(268.5), ry(380) + door_r], fill=WHITE_FILL, outline=BLACK_LINE, width=2)
    d.arc([rx(268.5) - door_r, ry(380) - door_r, rx(268.5) + door_r, ry(380) + door_r], start=90, end=180, fill=BLACK_LINE, width=2)

    # 7. Code text
    f_unit = get_system_font(44)
    bbox = f_unit.getbbox("AX-120")
    w_t, h_t = bbox[2] - bbox[0], bbox[3] - bbox[1]
    cx = (rx(220) + rx(270)) // 2
    cy = (ry(380) + ry(457)) // 2
    d.text((cx - w_t // 2, cy - h_t // 2), "AX-120", fill=BLACK_LINE, font=f_unit)

    return im


def render_bx107_cad():
    """Generates a crisp high-res CAD graphic for unit BX-107 + Terrace."""
    S = 10
    W, H = 94 * S, 172 * S
    im = Image.new("RGB", (W, H), WHITE_FILL)
    d = ImageDraw.Draw(im)
    LW = 4

    def rx(c): return int((c - 208) * S)
    def ry(r): return int((r - 820) * S)

    cx_b, cy_b, R_b = 276.0, 874.5, 58.0

    # 1. Terrace polygon (Green)
    terrace_pts = [(rx(243), ry(969)), (rx(243), ry(922.5))]
    for c_val in np.linspace(243, 276, 30):
        dx_v = c_val - cx_b
        dy_v = math.sqrt(max(0, R_b**2 - dx_v**2))
        terrace_pts.append((rx(c_val), ry(cy_b + dy_v)))
    terrace_pts.extend([(rx(296), ry(932.5)), (rx(296), ry(985.5)), (rx(273), ry(985.5))])
    for t in np.linspace(0, 1, 25):
        c_val = (1 - t)**2 * 273 + 2 * (1 - t) * t * 255 + t**2 * 243
        r_val = (1 - t)**2 * 985.5 + 2 * (1 - t) * t * 983 + t**2 * 969
        terrace_pts.append((rx(c_val), ry(r_val)))

    d.polygon(terrace_pts, fill=GREEN_FILL)
    d.line(terrace_pts + [terrace_pts[0]], fill=BLACK_LINE, width=LW, joint="curve")

    # 2. BX-107 interior polygon (Blue)
    bx_pts = [
        (rx(217.5), ry(826.5)),
        (rx(294.5), ry(826.5)),
        (rx(294.5), ry(932.5)),
        (rx(276.0), ry(932.5))
    ]
    for c_val in np.linspace(276.0, 218.5, 50):
        dx_v = c_val - cx_b
        dy_v = math.sqrt(max(0, R_b**2 - dx_v**2))
        bx_pts.append((rx(c_val), ry(cy_b + dy_v)))
    bx_pts.append((rx(217.5), ry(882.0)))

    d.polygon(bx_pts, fill=BLUE_FILL)
    d.line(bx_pts + [bx_pts[0]], fill=BLACK_LINE, width=LW, joint="curve")

    # 3. Walls, columns, doors
    d.rectangle([rx(217.5), ry(824), rx(296.5), ry(826.5)], fill=GRAY_WALL, outline=BLACK_LINE, width=LW)
    d.rectangle([rx(294.5), ry(826.5), rx(297.5), ry(829)], fill=GRAY_WALL, outline=BLACK_LINE, width=LW)
    d.rectangle([rx(294.5), ry(840), rx(297.5), ry(932.5)], fill=GRAY_WALL, outline=BLACK_LINE, width=LW)

    door1_r = rx(294.5) - rx(283.5)
    d.rectangle([rx(283.5), ry(829), rx(294.5), ry(829) + 8], fill=WHITE_FILL, outline=BLACK_LINE, width=2)
    d.arc([rx(294.5) - door1_r, ry(829) - door1_r, rx(294.5) + door1_r, ry(829) + door1_r], start=90, end=180, fill=BLACK_LINE, width=2)

    col_left_poly = [
        (rx(214.5), ry(862)), (rx(217.5), ry(862)), (rx(217.5), ry(874)),
        (rx(238.0), ry(874)), (rx(238.0), ry(882)), (rx(212.0), ry(882)),
        (rx(212.0), ry(870)), (rx(214.5), ry(870))
    ]
    d.polygon(col_left_poly, fill=GRAY_WALL)
    d.line(col_left_poly + [col_left_poly[0]], fill=BLACK_LINE, width=LW, joint="curve")
    d.rectangle([rx(230), ry(875.5), rx(236.5), ry(880.5)], fill=WHITE_FILL, outline=BLACK_LINE, width=LW)
    d.rectangle([rx(273), ry(985.5), rx(280), ry(990)], fill=GRAY_WALL, outline=BLACK_LINE, width=LW)

    door2_r = rx(292) - rx(282)
    d.line([(rx(282), ry(932.5)), (rx(292), ry(932.5))], fill=GREEN_FILL, width=LW + 2)
    d.rectangle([rx(292) - 8, ry(932.5), rx(292), ry(932.5) + door2_r], fill=WHITE_FILL, outline=BLACK_LINE, width=2)
    d.arc([rx(292) - door2_r, ry(932.5) - door2_r, rx(292) + door2_r, ry(932.5) + door2_r], start=90, end=180, fill=BLACK_LINE, width=2)

    f_u = get_system_font(42)
    f_t = get_system_font(28)
    ub = f_u.getbbox("BX-107")
    d.text((rx(258) - (ub[2] - ub[0]) // 2, ry(870)), "BX-107", fill=BLACK_LINE, font=f_u)
    tb = f_t.getbbox("BX-107 Terrace")
    d.text((rx(269) - (tb[2] - tb[0]) // 2, ry(956)), "BX-107 Terrace", fill=BLACK_LINE, font=f_t)

    return im


def generate_contract_sheet(
    template_img: Image.Image,
    layout_img: Image.Image,
    unit_img: Image.Image,
    unit_code: str,
    area_val: float,
    spill_out_val: float,
    has_spill_out: bool,
    keyplan_box: tuple,
    floor_text: str = "First Floor"
) -> Image.Image:
    """Builds the final composite high-res sheet matching company standards."""
    canvas = template_img.copy().convert("RGB")
    draw = ImageDraw.Draw(canvas)

    font_main = get_system_font(52)
    font_sup = get_system_font(34)
    font_floor = get_system_font(58)

    # 1. Update Floor Name Header if modified
    # Erase old floor title box (x: 950..1550, y: 35..130)
    draw.rectangle([950, 35, 1550, 130], fill=WHITE_FILL)
    fb = font_floor.getbbox(floor_text)
    fw = fb[2] - fb[0]
    draw.text((1240 - fw // 2, 45), floor_text, fill=BLACK_LINE, font=font_floor)
    draw.line([(1240 - fw // 2, 105), (1240 + fw // 2, 105)], fill=BLACK_LINE, width=3)

    # 2. Paste Unit Plan in Upper Center Section
    uw, uh = unit_img.size
    max_w, max_h = 1223, 1213
    scale = min(max_w / uw, max_h / uh)
    new_w, new_h = int(uw * scale), int(uh * scale)
    u_resized = unit_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    canvas.paste(u_resized, (1232 - new_w // 2, 1143 - new_h // 2))

    # 3. Process Key Plan with Red Highlight
    arr_lay = np.array(layout_img.convert("RGB"))
    # Mask out Room Legend top-left corner
    arr_lay[0:145, 0:85, :] = 255

    x1, y1, x2, y2 = keyplan_box
    # Constrain highlight within layout bounds
    x1, x2 = max(0, x1), min(arr_lay.shape[1], x2)
    y1, y2 = max(0, y1), min(arr_lay.shape[0], y2)

    region = arr_lay[y1:y2, x1:x2].astype(float)
    not_white = ~((region[:, :, 0] > 240) & (region[:, :, 1] > 240) & (region[:, :, 2] > 240))

    lum = (0.299 * region[:, :, 0] + 0.587 * region[:, :, 1] + 0.114 * region[:, :, 2]) / 230.0
    lum = np.clip(lum, 0, 1.05)

    region[:, :, 0] = np.where(not_white, np.clip(217 * lum, 0, 255), region[:, :, 0])
    region[:, :, 1] = np.where(not_white, np.clip(95 * lum, 0, 255), region[:, :, 1])
    region[:, :, 2] = np.where(not_white, np.clip(108 * lum, 0, 255), region[:, :, 2])
    arr_lay[y1:y2, x1:x2] = region.astype(np.uint8)

    # Crop building footprint from layout
    kp_crop = Image.fromarray(arr_lay[100:1022, 90:998])
    kw, kh = kp_crop.size
    kp_scale = 931 / kh
    kp_w, kp_h = int(kw * kp_scale), int(kh * kp_scale)
    kp_resized = kp_crop.resize((kp_w, kp_h), Image.Resampling.LANCZOS)
    canvas.paste(kp_resized, (1244 - kp_w // 2, 2261))

    # 4. Title Block: Unit Code
    draw.rectangle([1185, 3305, 1765, 3480], fill=WHITE_FILL)
    code_bbox = font_main.getbbox(unit_code)
    cw = code_bbox[2] - code_bbox[0]
    draw.text((1474 - cw // 2, 3363), unit_code, fill=BLACK_LINE, font=font_main)

    # 5. Title Block: Area Values
    draw.rectangle([1775, 3230, 2450, 3480], fill=WHITE_FILL)
    if has_spill_out and spill_out_val > 0:
        # Two-line format (Area + Spill Out Area)
        l1 = f"Area = {int(area_val) if area_val.is_integer() else area_val} m"
        tb1 = font_main.getbbox(l1)
        tw1 = tb1[2] - tb1[0]
        draw.text((1821, 3285), l1, fill=BLACK_LINE, font=font_main)
        draw.text((1821 + tw1 + 2, 3285 - 6), "2", fill=BLACK_LINE, font=font_sup)

        l2 = f"Spill Out Area = {int(spill_out_val) if spill_out_val.is_integer() else spill_out_val} m"
        tb2 = font_main.getbbox(l2)
        tw2 = tb2[2] - tb2[0]
        draw.text((1821, 3367), l2, fill=BLACK_LINE, font=font_main)
        draw.text((1821 + tw2 + 2, 3367 - 6), "2", fill=BLACK_LINE, font=font_sup)
    else:
        # Single-line format (Gross area = XX m²)
        txt_main = f"Gross area = {int(area_val) if area_val.is_integer() else area_val} m"
        tb = font_main.getbbox(txt_main)
        tw = tb[2] - tb[0]
        sb = font_sup.getbbox("2")
        sw = sb[2] - sb[0]
        start_x = 2114 - (tw + sw + 2) // 2
        y_pos = 3325
        draw.text((start_x, y_pos), txt_main, fill=BLACK_LINE, font=font_main)
        draw.text((start_x + tw + 2, y_pos - 6), "2", fill=BLACK_LINE, font=font_sup)

    return canvas


# -------------------------------------------------------------
# Streamlit Web App Interface
# -------------------------------------------------------------
st.title("📐 نظام توليد لوحات التعاقد الهندسية (Unit Sheet Generator)")
st.caption("أداة متكاملة لتركيب لوحات الوحدات العقارية وتظليل الـ Key Plan تلقائياً بدقة الطباعة الرسمية")

# Sidebar: Template and Floor Layout Setup
st.sidebar.header("⚙️ إعدادات النموذج والمخطط العام")
uploaded_template = st.sidebar.file_uploader("1. قالب اللوحة الأساسي (MAIN TEMPALTE)", type=["jpg", "png", "jpeg"])
uploaded_layout = st.sidebar.file_uploader("2. مخطط الدور الإجمالي (Layout With Areas)", type=["jpg", "png", "jpeg"])

floor_name = st.sidebar.text_input("اسم الدور (Floor Name)", value="First Floor")

st.sidebar.markdown("---")
st.sidebar.header("🏢 إعدادات الوحدة المطلوب توليدها")

selected_preset = st.sidebar.selectbox(
    "اختر وحدة جاهزة من القائمة أو حدد تخصيص يدوي:",
    ["تخصيص يدوي (Custom)"] + list(UNIT_PRESETS.keys())
)

if selected_preset != "تخصيص يدوي (Custom)":
    preset_data = UNIT_PRESETS[selected_preset]
    unit_code = st.sidebar.text_input("كود الوحدة (Unit Code)", value=selected_preset)
    unit_area = st.sidebar.number_input("المساحة الإجمالية (Gross Area m²)", value=float(preset_data["area"]), step=1.0)
    has_spill_out = st.sidebar.checkbox("تحتوي على تراس / Spill Out Area؟", value=preset_data["has_spill_out"])
    spill_out_area = 0.0
    if has_spill_out:
        spill_out_area = st.sidebar.number_input("مساحة التراس (Spill Out Area m²)", value=float(preset_data["spill_out"]), step=1.0)
    keyplan_box = preset_data["keyplan_box"]
    render_type = preset_data["type"]
else:
    unit_code = st.sidebar.text_input("كود الوحدة (Unit Code)", value="AX-105")
    unit_area = st.sidebar.number_input("المساحة الإجمالية (Gross Area m²)", value=92.0, step=1.0)
    has_spill_out = st.sidebar.checkbox("تحتوي على تراس / Spill Out Area؟", value=False)
    spill_out_area = 0.0
    if has_spill_out:
        spill_out_area = st.sidebar.number_input("مساحة التراس (Spill Out Area m²)", value=0.0, step=1.0)
    render_type = "upload_or_crop"

    st.sidebar.subheader("إحداثيات تظليل الوحدة في المخطط (Key Plan Box)")
    col_k1, col_k2 = st.sidebar.columns(2)
    kp_x1 = col_k1.number_input("X1 (يسار)", value=800, step=5)
    kp_y1 = col_k2.number_input("Y1 (أعلى)", value=850, step=5)
    kp_x2 = col_k1.number_input("X2 (يمين)", value=900, step=5)
    kp_y2 = col_k2.number_input("Y2 (أسفل)", value=980, step=5)
    keyplan_box = (int(kp_x1), int(kp_y1), int(kp_x2), int(kp_y2))

uploaded_unit_img = st.file_uploader("📂 اختياري: رفع صورة المسقط المنفصل للوحدة (Unit Plan Image)", type=["jpg", "png", "jpeg"])

# Action Button
if st.button("🚀 توليد اللوحة الهندسية الآن (Generate Sheet)", type="primary"):
    # Load Template
    if uploaded_template is not None:
        template_img = Image.open(uploaded_template)
    else:
        # Fallback to local default if running in repo with local assets
        try:
            template_img = Image.open("MAIN TEMPALTE.jpg")
        except Exception:
            st.error("يرجى رفع صورة القالب الأساسي MAIN TEMPALTE.jpg من الشريط الجانبي.")
            st.stop()

    # Load Floor Layout
    if uploaded_layout is not None:
        layout_img = Image.open(uploaded_layout)
    else:
        try:
            layout_img = Image.open("ETAJE-AX-BX-01-FIRST FLOOR - WITH AREA.jpg")
        except Exception:
            st.error("يرجى رفع صورة مخطط الدور الإجمالي Layout With Areas من الشريط الجانبي.")
            st.stop()

    # Determine Unit Plan Image
    if uploaded_unit_img is not None:
        unit_img = Image.open(uploaded_unit_img)
    elif selected_preset != "تخصيص يدوي (Custom)":
        if render_type == "cad_ax120":
            unit_img = render_ax120_cad()
        elif render_type == "cad_bx107":
            unit_img = render_bx107_cad()
        elif render_type == "mirror_101":
            try:
                u101 = Image.open("101.jpg").convert("RGB")
                draw_101 = ImageDraw.Draw(u101)
                draw_101.rectangle([380, 460, 560, 515], fill=PURPLE_FILL)
                unit_img = ImageOps.mirror(u101)
                d104 = ImageDraw.Draw(unit_img)
                f_u = get_system_font(45)
                ub = f_u.getbbox("AX-104")
                d104.text((512 - (ub[2] - ub[0]) // 2, 462), "AX-104", fill=BLACK_LINE, font=f_u)
            except Exception:
                unit_img = layout_img.crop(UNIT_PRESETS["AX-104"]["reference_crop"])
        else:
            # Check local file or crop from layout
            unit_file = f"{selected_preset.split('-')[-1]}.jpg"
            try:
                unit_img = Image.open(unit_file)
            except Exception:
                unit_img = layout_img.crop(preset_data["reference_crop"])
    else:
        # Crop directly from layout using provided box
        unit_img = layout_img.crop(keyplan_box)

    with st.spinner("جاري معالجة وتركيب اللوحة الهندسية عالية الدقة..."):
        result_sheet = generate_contract_sheet(
            template_img=template_img,
            layout_img=layout_img,
            unit_img=unit_img,
            unit_code=unit_code,
            area_val=unit_area,
            spill_out_val=spill_out_area,
            has_spill_out=has_spill_out,
            keyplan_box=keyplan_box,
            floor_text=floor_name
        )

        st.success(f"تم إنشاء لوحة الوحدة {unit_code} بنجاح!")
        st.image(result_sheet, caption=f"لوحة تعاقدية - {unit_code} ({floor_name})", use_container_width=True)

        # Download Buttons
        buf_jpg = io.BytesIO()
        result_sheet.save(buf_jpg, format="JPEG", quality=95)
        byte_data = buf_jpg.getvalue()

        col_d1, col_d2 = st.columns(2)
        col_d1.download_button(
            label="📥 تحميل اللوحة كصورة بجودة عالية (JPG)",
            data=byte_data,
            file_name=f"{unit_code}-Contract-Sheet.jpg",
            mime="image/jpeg"
        )

        # PDF Download
        buf_pdf = io.BytesIO()
        result_sheet.save(buf_pdf, format="PDF", resolution=300.0)
        col_d2.download_button(
            label="📄 تحميل اللوحة كملف جاهز للطباعة (PDF)",
            data=buf_pdf.getvalue(),
            file_name=f"{unit_code}-Contract-Sheet.pdf",
            mime="application/pdf"
        )
