
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os
from datetime import datetime

st.set_page_config(layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Set background and text color ---
st.markdown("""
    <style>
        header, .st-emotion-cache-18ni7ap { background-color: #d2b74e !important; }
        * {
            color: black !important;
        }
        body {
            background-color: #d2b74e !important;
        }
        .stApp {
            background-color: #d2b74e !important;
        }
        .stSelectbox div[data-baseweb="select"] {
            background-color: #F1DDB4 !important;
        }
        div[role="listbox"] {
            background-color: #F1DDB4 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Memory in a Frame")
st.caption("Turn today’s best memory into a keepsake! Create your own Polaroid-style card. Just upload a photo and pick a message.")

# --- CSS for polaroid style and responsiveness ---
st.markdown("""
    <style>
        .polaroid {
            background: white;
            padding: 10px;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            margin: 10px auto;
            width: 90%;
            max-width: 300px;
            text-align: center;
            border-radius: 10px;
        }
        .polaroid img {
            width: 100%;
            border-radius: 5px;
        }
        .category {
            font-weight: bold;
            margin-top: 15px;
        }
        .message-box {
            background-color: #f0f0f0;
            padding: 5px 10px;
            border-radius: 8px;
            margin: 5px 0;
            cursor: pointer;
        }
        .message-box:hover {
            background-color: #e0e0ff;
        }
    </style>
""", unsafe_allow_html=True)

def get_message_image_filename(msg):
    mapping = {
        "THANK YOU": "PIC_1_1",
        "NICE !": "PIC_1_2",
        "Good !": "PIC_1_3",
        "Delicious!": "PIC_2_1",
        "Super yummy!": "PIC_2_2",
        "So tasty!": "PIC_2_3",
        "BEST FRIENDLY!": "PIC_3_1",
        "Great staff": "PIC_3_2",
        "LOVED THE SERVICES": "PIC_3_3",
        "Cozy vibes!": "PIC_4_1",
        "So relaxing.": "PIC_4_2",
        "Cool spot.": "PIC_4_3"
    }
    return mapping.get(msg, "")

# --- Upload section ---
st.subheader("Upload a photo")
uploaded_image = st.file_uploader("Please select a photo of your dish or the restaurant", type=["jpg", "jpeg", "png"])

if uploaded_image:
    template_path = os.path.join(BASE_DIR, "assets", "polaframe.png")
    if not os.path.exists(template_path):
        st.error(f"Template image not found: {template_path}")
        st.stop()

    polaroid_template = Image.open(template_path).convert("RGBA")
    uploaded = Image.open(uploaded_image).convert("RGBA")

    uploaded_ratio = uploaded.width / uploaded.height
    if uploaded_ratio > 1:
        new_height = 346
        new_width = int(uploaded_ratio * new_height)
    else:
        new_width = 346
        new_height = int(new_width / uploaded_ratio)

    resized = uploaded.resize((new_width, new_height))
    left = (new_width - 346) // 2
    top = (new_height - 346) // 2
    uploaded_cropped = resized.crop((left, top, left + 346, top + 346))
    photo_area = (37, 37)

    combined = polaroid_template.copy()
    combined.paste(uploaded_cropped, box=photo_area, mask=uploaded_cropped)

    corner_path = os.path.join(BASE_DIR, "assets", "PIC_5_1.png")
    if os.path.exists(corner_path):
        corner_img = Image.open(corner_path).convert("RGBA")
        cw, ch = corner_img.size
        cx = (combined.width - cw) // 2
        cy = combined.height - ch - 15
        combined.paste(corner_img, (cx, cy), mask=corner_img)

    draw = ImageDraw.Draw(combined)
    try:
        msg_font = ImageFont.load_default()
    except:
        msg_font = ImageFont.load_default()

    msg_y = 10
    selected_msg = st.session_state.get("message_select")

    if selected_msg not in [None, "↓Message↓"]:
        msg = selected_msg
        image_path = os.path.join(BASE_DIR, "assets", f"{get_message_image_filename(msg)}.png")
        if os.path.exists(image_path):
            sticker = Image.open(image_path).convert("RGBA")
            sticker_width, sticker_height = sticker.size
            paste_x = 10
            paste_y = 80
            if paste_x + sticker_width > combined.width:
                sticker_width = combined.width - paste_x
            if paste_y + sticker_height > combined.height:
                sticker_height = combined.height - paste_y
            sticker = sticker.resize((sticker_width, sticker_height))
            combined.paste(sticker, (paste_x, paste_y), mask=sticker)
        else:
            draw.text((10, 80), msg, fill=(0, 0, 0), font=msg_font)

    today_str = datetime.now().strftime("on %b %d, %Y")
    bbox = draw.textbbox((0, 0), today_str, font=msg_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = combined.width - text_width - 30
    y = combined.height - text_height - 40
    draw.text((x, y), today_str, font=msg_font, fill=(0, 0, 0))

    st.subheader("Card Preview")
    st.image(combined, caption='Your Polaroid Card', use_container_width=False)

    buffer = io.BytesIO()
    combined.save(buffer, format="PNG")
    st.download_button(
        label="Download this card",
        data=buffer.getvalue(),
        file_name="polaroid_card.png",
        mime="image/png"
    )

st.subheader("Select a Message")
message_options = {
    "Feeling": ["THANK YOU", "NICE !", "Good !"],
    "Food": ["Delicious!", "Super yummy!", "So tasty!"],
    "Service": ["BEST FRIENDLY!", "Great staff", "LOVED THE SERVICES"],
    "Atmosphere": ["Cozy vibes!", "So relaxing.", "Cool spot."]
}
all_messages = [msg for msgs in message_options.values() for msg in msgs]
selected_msg = st.selectbox("Choose a message:", ["↓Message↓"] + all_messages, key="message_select")

if selected_msg != "↓Message↓":
    st.session_state["selected_messages"] = [selected_msg]
else:
    st.session_state["selected_messages"] = []
