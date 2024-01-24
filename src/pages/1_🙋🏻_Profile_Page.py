import streamlit as st
from pymongo import MongoClient
from PIL import Image, ImageDraw, ImageOps
import io

from Homepage import get_session_state, set_session_state
from streamlit_extras.switch_page_button import switch_page
import base64
import requests


# Connect to MongoDB
client = MongoClient("mongodb+srv://odin:qsaw1234@odin.2symxyt.mongodb.net/test")
db = client.odin
users = db.users

def is_user_logged_in():
    return get_session_state().get("is_logged_in", False)

# Display different content based on whether the user is logged in or not
if get_session_state().get("is_logged_in", False):
    st.title("Profile Page")

    user = users.find_one({"username": get_session_state().get("username")})
    if user:
        # Show user name
        # st.subheader("Name: {}".format(user.get("name")))

        # Show profile photo
        profile_photo = user.get("profile_photo")
        if profile_photo:
            image = Image.open(io.BytesIO(profile_photo))
            image = image.resize((200, 200))
            image = image.convert("RGBA")

            # Create circular mask
            size = (200, 200)
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)

            # Apply mask to image
            output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)

            output_bytes = io.BytesIO()
            output.save(output_bytes, format='PNG')
            output_bytes.seek(0)
            st.write(f'<div><img src="data:image/png;base64,{base64.b64encode(output_bytes.getvalue()).decode()}" style="border-radius:50%;"></div>', unsafe_allow_html=True)


            
        
        # Upload profile photo
        st.subheader("Upload Profile Photo")
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            file_contents = uploaded_file.read()
            users.update_one({"username": get_session_state().get("username")}, {"$set": {"profile_photo": file_contents}})
            st.success("Profile photo uploaded successfully. Please refresh.")
        
        # About me
        st.subheader("About Me")
        about_me = user.get("about_me")
        st.write(about_me)
        if st.button("Edit About Me"):
            about_me_text = st.text_area("Enter some information about yourself", value=about_me)
            if about_me_text != about_me:
                users.update_one({"username": get_session_state().get("username")}, {"$set": {"about_me": about_me_text}})
                st.success("About me updated successfully.")
        if st.button("Save"):
            about_me_text = st.text_area("Enter some information about yourself", value=about_me)
            if about_me_text != about_me:
                users.update_one({"username": get_session_state().get("username")}, {"$set": {"about_me": about_me_text}})
                st.success("Information saved successfully. Please refresh.")
            about_me = about_me_text
            
        # Buttons
        col1, col2 = st.columns(2)
        with col1:
            # Redirect to Homepage button
            go_to_homepage = st.button("Homepage")
            if go_to_homepage:
                switch_page("Homepage")
        with col2:
            # Refresh button
            go_to_profile_page = st.button("Refresh")
            if go_to_profile_page:
                switch_page("profile page")

    else:
        st.error("User not found")
else:
    st.error("Please log in or create an account")


def add_logo():
    image_url = "https://github.com/Devanshu-17/Odin/assets/93381397/bbfa6019-8b21-4ff7-b90d-f795464146df.jpg"
    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url({image_url});
                max-width: 300px;
                min-height: 100vh;
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


# Main function
def main():
    add_logo() # Call the function to add logo to sidebar
    # st.title("Odin App")

    session_state = get_session_state()


    if  session_state.get("is_logged_in", False):
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