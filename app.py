import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(
    page_title="Auto Contract Sheet Generator",
    page_icon="🏢",
    layout="wide"
)

BLACK_LINE = (0, 0, 0)
WHITE_FILL = (255, 255, 255)

# قاعدة بيانات الوحدات بإحداثيات قص هندسي مباشر خفيف جداً على الـ RAM
FIRST_FLOOR_UNITS = {
    "AX-101": {"area": 103, "box": (860, 880, 950, 980)},
    "AX-102": {"area": 52,  "box": (790, 880, 860, 980)},
    "AX-103": {"area": 52,  "box": (730, 880, 800, 980)},
    "AX-104": {"area": 103, "box": (650, 880, 730, 980)},
    "AX-105": {"area": 38,  "box": (630, 810, 720, 890)},
    "AX-106": {"area": 38,  "box": (630, 760, 720, 835)},
    "AX-107": {"area": 38,  "box": (630, 700, 720, 780)},
    "AX-108": {"area": 38,  "box": (630, 650, 720, 725)},
    "AX-109": {"area": 39,  "box": (630, 595, 720, 670)},
    "AX-110": {"area": 52,  "box": (620, 545, 710, 620)},
    "AX-111": {"area": 102, "box": (660, 480, 755, 565)},
    "AX-112": {"area": 103, "box": (635, 415, 730, 500)},
    "AX-113": {"area": 103, "box": (585, 365, 680, 455)},
    "AX-114": {"area": 104, "box": (520, 335, 620, 425)},
    "AX-115": {"area": 51,  "box": (465, 385, 545, 470)},
    "AX-116": {"area": 39,  "box": (410, 375, 495, 455)},
    "AX-117": {"area": 39,  "box": (360, 375, 445, 440)},
    "AX-118": {"area": 39,  "box": (310, 375, 395, 435)},
    "AX-119": {"area": 39,  "box": (260, 375, 345, 435)},
    "AX-120": {"area": 39,  "box": (210, 375, 290, 435)},
    "AX-121": {"area": 121, "box": (115, 355, 205, 445)},
    "AX-122": {"area": 61,  "box": (115, 280, 205, 360)},
    "AX-123": {"area": 61,  "box": (115, 230, 205, 305)},
    "AX-124": {"area": 121, "box": (115, 145, 205, 235)},
    "AX-125": {"area": 38,  "box": (210, 130, 285, 200)},
    "AX-126": {"area": 38,  "box": (260, 130, 340, 200)},
    "AX-127": {"area": 38,  "box": (310, 130, 395, 200)},
    "AX-128": {"area": 38,  "box": (360, 130, 445, 200)},
    "AX-129": {"area": 38,  "box": (410, 130, 495, 200)},
    "AX-130": {"area": 38,  "box": (465, 130, 545, 200)},
    "AX-131": {"area": 91,  "box": (520, 160, 615, 250)},
    "AX-132": {"area": 92,  "box": (585, 175, 685, 270)},
    "AX-133": {"area": 92,  "box": (650, 200, 750, 295)},
    "AX-134": {"area": 92,  "box": (710, 240, 805, 330)},
    "AX-135": {"area": 92,  "box": (760, 290, 860, 380)},
    "AX-136": {"area": 92,  "box": (800, 345, 890, 435)},
    "AX-137": {"area": 92,  "box": (830, 410, 915, 500)},
    "AX-138": {"area": 91,  "box": (840, 475, 935, 565)},
    "AX-139": {"area": 38,  "box": (875, 540, 955, 615)},
    "AX-140": {"area": 38,  "box": (875, 595, 955, 670)},
    "AX-141": {"area": 38,  "box": (875, 650, 955, 725)},
    "AX-142": {"area": 38,  "box": (875, 700, 955, 780)},
    "AX-143": {"area": 38,  "box": (875, 760, 955, 835)},
    "AX-144": {"area": 38,  "box": (875, 810, 955, 890)},
    "BX-101": {"area": 74,  "box": (330, 555, 460, 630)},
    "BX-102": {"area": 83,  "box": (225, 540, 340, 620)},
    "BX-103": {"area": 42,  "box": (210, 595, 300, 675)},
    "BX-104": {"area": 42,  "box": (210, 650, 300, 725)},
    "BX-105": {"area": 42,  "box": (210, 700, 300, 780)},
    "BX-106": {"area": 42,  "box": (210, 755, 300, 835)},
    "BX-107": {"area": 74,  "box": (210, 835, 305, 985)},
    "BX-108": {"area": 71,  "box": (310, 860, 400, 985)},
    "BX-109": {"area": 54,  "box": (335, 800, 425, 885)},
    "BX-110": {"area": 55,  "box": (335, 750, 425, 830)},
}

def get_font(size):
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

def generate_sheet(unit_code, template_img, layout_pil):
    info = FIRST_FLOOR_UNITS[unit_code]
    lw, lh = layout_pil.size
    bx1, by1, bx2, by2 = info["box"]
    
    rx1, ry1 = int((bx1 / 1000.0) * lw), int((by1 / 1000.0) * lh)
    rx2, ry2 = int((bx2 / 1000.0) * lw), int((by2 / 1000.0) * lh)

    crop = layout_pil.crop((rx1, ry1, rx2, ry2))
    unit_img = crop.resize((crop.width * 2, crop.height * 2), Image.Resampling.BILINEAR)
    
    # مقاس آمن جداً ومناسب للطباعة والتعاقد (1240x1754) بدون أي استهلاك للرّامات
    canvas = template_img.resize((1240, 1754), Image.Resampling.BILINEAR).convert("RGB")
    draw = ImageDraw.Draw(canvas)
    
    uw, uh = unit_img.size
    scale = min(600 / uw, 600 / uh)
    new_w, new_h = int(uw * scale), int(uh * scale)
    canvas.paste(unit_img.resize((new_w, new_h), Image.Resampling.BILINEAR), (620 - new_w // 2, 570 - new_h // 2))

    kp_scale = 450 / layout_pil.height
    kp_resized = layout_pil.resize((int(layout_pil.width * kp_scale), int(layout_pil.height * kp_scale)), Image.Resampling.BILINEAR)
    ImageDraw.Draw(kp_resized).rectangle([int(rx1 * kp_scale), int(ry1 * kp_scale), int(rx2 * kp_scale), int(ry2 * kp_scale)], outline=(217, 95, 108), width=2)
    canvas.paste(kp_resized, (620 - kp_resized.width // 2, 1130))

    font_main = get_font(26)
    font_sup = get_font(18)
    
    draw.rectangle([590, 1650, 880, 1740], fill=WHITE_FILL)
    cb = font_main.getbbox(unit_code)
    draw.text((735 - (cb[2] - cb[0]) // 2, 1680), unit_code, fill=BLACK_LINE, font=font_main)

    draw.rectangle([890, 1610, 1220, 1740], fill=WHITE_FILL)
    a_str = f"{int(info['area'])}"
    txt_main = f"Gross area = {a_str} m"
    tb = font_main.getbbox(txt_main)
    draw.text((1055 - (tb[2] - tb[0] + 15) // 2, 1660), txt_main, fill=BLACK_LINE, font=font_main)
    draw.text((1055 + (tb[2] - tb[0]) // 2 - 10, 1655), "2", fill=BLACK_LINE, font=font_sup)

    return canvas

st.title("🏢 Auto Contract Sheet Generator (Zero-Crash Mode)")

with st.sidebar:
    up_layout = st.file_uploader("Layout Image", type=["jpg", "png", "jpeg"])
    up_template = st.file_uploader("Template Image", type=["jpg", "png", "jpeg"])

if not up_layout or not up_template:
    st.info("👈 أرجو رفع ملفات الـ Layout والـ Template من القائمة الجانبية للبدء.")
    st.stop()

# ضغط الصورة فور رفعها لحماية السيرفر من الكراش
template_img = Image.open(up_template).convert("RGB")
layout_pil = Image.open(up_layout).convert("RGB")
if layout_pil.width > 800:
    layout_pil = layout_pil.resize((800, int(800 * layout_pil.height / layout_pil.width)), Image.Resampling.BILINEAR)

selected_code = st.selectbox("اختر الكود:", list(FIRST_FLOOR_UNITS.keys()))

if st.button("توليد اللوحة برابط مباشر", type="primary"):
    sheet = generate_sheet(selected_code, template_img, layout_pil)
    
    st.success("تم توليد اللوحة بنجاح وبدون أي استهلاك للذاكرة!")

    buf = io.BytesIO()
    sheet.save(buf, format="JPEG", quality=85)
    st.download_button(
        label=f"📥 اضغط هنا لتحميل لوحة {selected_code} (JPG)",
        data=buf.getvalue(),
        file_name=f"{selected_code}.jpg",
        mime="image/jpeg",
        type="primary",
        use_container_width=True
    )
