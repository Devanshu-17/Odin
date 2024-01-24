import streamlit as st
from pymongo import MongoClient
from hashlib import sha256
from uuid import uuid4
from streamlit_extras.let_it_rain import rain
from streamlit_extras.switch_page_button import switch_page
import base64
from PIL import Image, ImageDraw, ImageOps
import io
import requests
from streamlit_extras.colored_header import colored_header

# Set page configuration
st.set_page_config(
    page_title="Odin: Revolutionising Attendance Management With Signature Recognition",
    page_icon="🔮")

# Connect to MongoDB
client = MongoClient("mongodb+srv://odin:qsaw1234@odin.2symxyt.mongodb.net/test")
db = client.odin
users = db.users

# Utility functions
def hash_password(password):
    # Hash a password string using SHA256
    return sha256(password.encode("utf-8")).hexdigest()

def get_session_state():
    # Get the session state for the current session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid4())
    if st.session_state.session_id not in st.session_state:
        st.session_state[st.session_state.session_id] = {}
    return st.session_state[st.session_state.session_id]

def set_session_state(state):
    # Set the session state for the current session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid4())
    if st.session_state.session_id not in st.session_state:
        st.session_state[st.session_state.session_id] = {}
    st.session_state[st.session_state.session_id] = state


# Registration function
def register():
    st.subheader("Create New Account")
    name = st.text_input("Enter Name", key="name")
    username = st.text_input("Username", key="reg_username")
    password = st.text_input("Password", type="password", key="reg_password")
    security_question = st.text_input("What is your darkest secret?", key="reg_security_question")

    if st.button("Register"):
        hashed_password = hash_password(password)
        if users.find_one({"username": username}):
            st.warning("An account with that username already exists")
        else:
            users.insert_one({"name": name, "username": username, "password": hashed_password, "security_question": security_question})
            st.success("Account created")
            st.balloons()

# Login function
def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        hashed_password = hash_password(password)
        user = users.find_one({"username": username, "password": hashed_password})
        if user:
            set_session_state({"is_logged_in": True, "username": username})
            st.success("Logged in as {}".format(username))
            switch_page("profile_page")
        else:
            st.error("Incorrect username or password")

# Forgot password function
def forgot_password():
    st.subheader("Forgot Password")
    username = st.text_input("Username", key="forgot_password_username")
    security_answer = st.text_input("What is your darkest secret?", key="forgot_password_security_answer")
    new_password = st.text_input("New Password", type="password", key="forgot_password_new_password")

    if st.button("Submit"):
        user = users.find_one({"username": username, "security_question": security_answer})
        if user:
            hashed_password = hash_password(new_password)
            users.update_one({"_id": user["_id"]}, {"$set": {"password": hashed_password}})
            st.success("Password updated successfully")
        else:
            st.error("Incorrect username or security answer")

# Forgot password function
def reset_password():
    st.subheader("Reset Password")
    username = st.text_input("Username", key="reset_password_username")
    security_answer = st.text_input("What is your darkest secret?", key="reset_password_security_answer")
    new_password = st.text_input("New Password", type="password", key="reset_password_new_password")

    if st.button("Submit"):
        user = users.find_one({"username": username, "security_question": security_answer})
        if user:
            hashed_password = hash_password(new_password)
            users.update_one({"_id": user["_id"]}, {"$set": {"password": hashed_password}})
            st.success("Password updated successfully")
            st.snow()
        else:
            st.error("Incorrect username or security answer")

def add_logo():
    image_url = "https://github.com/Devanshu-17/Odin/assets/93381397/bbfa6019-8b21-4ff7-b90d-f795464146df.jpg"
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

# Main function
def main():
    add_logo() # Call the function to add logo to sidebar
    colored_header(
    label="Odin",
    description=" ",
    color_name="violet-70",
    )
    

    menu = ["Home"]
    session_state = get_session_state()


    if not session_state.get("is_logged_in", False):
        menu.extend(["Login", "Register", "Forgot Password"])
    else:
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

        menu.append("Reset Password")
        
        # Create a logout button container
        logout_container = st.sidebar.container()
        with logout_container:
            st.button("Logout", on_click=logout)

    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Revolutionising Attendance Management With Signature Recognition")
    

    elif choice == "Login":
        login()

    elif choice == "Register":
        register()

    elif choice == "Forgot Password":
        forgot_password()

    elif choice == "Reset Password":
        reset_password()

def logout():
    set_session_state({"is_logged_in": False, "username": None})
    st._rerun()

if __name__ == "__main__":
    main()
