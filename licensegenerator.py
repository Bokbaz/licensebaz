import streamlit as st
from PIL import Image
import io
import numpy as np
import cv2
import rembg

# Load the driver's license template
template_path = "image.png"
template = Image.open(template_path)
template_array = np.array(template)

# Define blue box coordinates (manually set from the template)
# These values may need fine-tuning depending on the exact template
blue_box_coords = {
    "x": 40,
    "y": 60,
    "width": 260,
    "height": 300
}

def remove_background(image: Image.Image) -> Image.Image:
    output = rembg.remove(image)
    return Image.open(io.BytesIO(output)).convert("RGBA")

def place_image_on_template(template, user_image):
    # Remove background from user image
    user_image_no_bg = remove_background(user_image)

    # Resize user image to fit into the blue box
    user_w, user_h = user_image_no_bg.size
    scale = blue_box_coords["width"] / user_w
    new_size = (int(user_w * scale), int(user_h * scale))
    resized_user_img = user_image_no_bg.resize(new_size, Image.ANTIALIAS)

    # Crop to match the height if needed
    if resized_user_img.size[1] > blue_box_coords["height"]:
        resized_user_img = resized_user_img.crop((
            0,
            0,
            resized_user_img.size[0],
            blue_box_coords["height"]
        ))

    # Paste the resized image into the template
    template_editable = template.convert("RGBA")
    template_editable.paste(resized_user_img, (blue_box_coords["x"], blue_box_coords["y"]), resized_user_img)

    return template_editable

st.title("Custom Driver License Profile Picture Generator")

uploaded_file = st.file_uploader("Upload a headshot photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Original Image", use_column_width=True)

    result = place_image_on_template(template, image)
    st.image(result, caption="Customized License", use_column_width=True)

    # Convert result to bytes for download
    img_byte_arr = io.BytesIO()
    result.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    st.download_button(
        label="Download Your Custom License",
        data=img_byte_arr,
        file_name="custom_license.png",
        mime="image/png"
    )
