# app.py
import streamlit as st
from image_describer import ProductImageDescriber
from video_describer import ProductVideoDescriber
import json
import os

st.set_page_config(page_title="AI Product Description Generator", layout="centered")

st.title("🧠 AI Product Description Generator")
st.markdown("Upload a product **image or video** (e.g., fashion or electronics), and get:")
st.markdown("- **Title** (1 line)\n- **Description** (2–3 lines)\n- **Bullet Features** (3–5 items)")

# API key input
openai_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

# File uploader
uploaded_file = st.file_uploader("📁 Upload product image/video", type=["jpg", "jpeg", "png", "mp4", "mov"])

# Display uploaded file preview
if uploaded_file is not None:
    file_type = uploaded_file.type
    st.subheader("📤 Uploaded File")

    if "image" in file_type:
        st.image(uploaded_file, use_container_width=True)
    elif "video" in file_type:
        st.video(uploaded_file)

# Submit button
if st.button("Generate Description"):
    if not openai_key:
        st.warning("Please enter your OpenAI API key.")
    elif not uploaded_file:
        st.warning("Please upload an image or video.")
    else:
        try:
            file_type = uploaded_file.type

            if "image" in file_type:
                image_bytes = uploaded_file.read()
                describer = ProductImageDescriber(image_bytes=image_bytes, openai_api_key=openai_key)
                result = describer.generate_product_description()

            elif "video" in file_type:
                video_path = f"temp_video.{uploaded_file.type.split('/')[-1]}"
                with open(video_path, "wb") as f:
                    f.write(uploaded_file.read())
                describer = ProductVideoDescriber(video_path=video_path, openai_api_key=openai_key)
                result = describer.generate_product_description()
                os.remove(video_path)

            else:
                st.error("Unsupported file format.")
                result = None

            if result:
                st.subheader("📝 Title")
                st.write(result.get("title", "N/A"))

                st.subheader("📃 Description")
                st.write(result.get("description", "N/A"))

                st.subheader("✅ Features")
                for feature in result.get("features", []):
                    st.markdown(f"- {feature}")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    pass
