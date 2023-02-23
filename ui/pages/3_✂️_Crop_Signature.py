import streamlit as st
from pymongo import MongoClient
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import datetime
import os
import io
from Homepage import get_session_state, set_session_state
from streamlit_extras.switch_page_button import switch_page
import requests



# Connect to MongoDB
client = MongoClient("<database uri>")
db = client.odin
users = db.users


def is_user_logged_in():
    return get_session_state().get("is_logged_in", False)

def add_logo():
    owner = "Devanshu-17"
    repo = "odin_testing"
    path = "odin_logo.png"
    ref = "main"
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}"
    headers = {
        "Authorization": "token <Enter token here>"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    image_url = response.json()["download_url"]
    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url({image_url});
                background-repeat: no-repeat;
                padding-top: 80px;
                background-position: 20px 20px;
                background-size: 50%;
            }}
            [data-testid="stSidebarNav"]::before {{
                content: "ODIN";
                padding-top: 20px;
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 90px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

if not is_user_logged_in():
    add_logo()
    st.error("You need to log in to access this page.")
    st.stop()

def crop_signatures(image, bounding_boxes):
    cropped_signatures = []
    for i, box in enumerate(bounding_boxes):
        x, y, w, h = box
        signature = image[y:y+h, x:x+w]
        cropped_signatures.append(signature)
        st.image(signature, caption=f"Cropped signature {i+1}", use_column_width=True)
    return cropped_signatures

st.title("Signature Cropper")

st.sidebar.title("Signature Cropper")



uploaded_file = st.file_uploader("Upload Attendance Sheet", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
    st.image(image, caption="Original Image", use_column_width=True)

    bounding_boxes = [  (765, 321, 204, 76),
                        (1038, 326, 194, 80),
                        (1296, 332, 216, 74),
                        (1558, 332, 217, 76),
                        (1825, 337, 234, 73)
                      ]
    cropped_signatures = crop_signatures(image, bounding_boxes)

    if st.button("Save Signatures"):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M")
        folder_path = f"attendance/{current_time}"
        os.makedirs(folder_path)
        for i, signature in enumerate(cropped_signatures):
            cv2.imwrite(f"{folder_path}/{i}.png", signature)
        st.success("Signatures saved successfully!")

# Redirect to Homepage button
go_to_homepage = st.button("Homepage")
if go_to_homepage:
    switch_page("Homepage")



# Main function
def main():
    add_logo() # Call the function to add logo to sidebar
    # st.title("Odin App")

    session_state = get_session_state()


    if  session_state.get("is_logged_in", False):
        add_logo()
        # Create a sidebar container for logged in user info
        user_info_container = st.sidebar.container()
        with user_info_container:
            st.subheader(f"Logged in as {session_state['username']}")

            user = users.find_one({"username": get_session_state().get("username")})
            if user:
                # Show profile photo
                profile_photo = user.get("profile_photo")
                if profile_photo:
                    image = Image.open(io.BytesIO(profile_photo))
                    image = image.resize((100, 100))
                    image = image.convert("RGBA")

                    # Create circular mask
                    size = (100, 100)
                    mask = Image.new('L', size, 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0) + size, fill=255)

                    # Apply mask to image
                    output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
                    output.putalpha(mask)

                    output_bytes = io.BytesIO()
                    output.save(output_bytes, format='PNG')
                    output_bytes.seek(0)

                    # Show profile photo
                    st.image(output_bytes, width=100)

        
        # Create a logout button container
        logout_container = st.sidebar.container()
        with logout_container:
            st.button("Logout", on_click=logout, key="logout_button")

def logout():
    set_session_state({"is_logged_in": False, "username": None})
    st._rerun()

if __name__ == "__main__":
    main()