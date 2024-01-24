import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
from Homepage import get_session_state, set_session_state
from streamlit_extras.switch_page_button import switch_page
from PIL import Image, ImageDraw, ImageOps
import io
import requests
from uuid import uuid4
import plotly.graph_objs as go
import plotly.express as px




# Connect to MongoDB
client = MongoClient("mongodb+srv://odin:qsaw1234@odin.2symxyt.mongodb.net/test")
db = client.odin
users = db.users
data = db.data

def is_user_logged_in():
    return get_session_state().get("is_logged_in", False)

st.title("User Dashboard")

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

if not is_user_logged_in():
    add_logo()
    st.error("You need to log in to access this page.")
    st.stop()


# Define today's date
today = datetime.now().strftime("%Y-%m-%d")

def get_user_state():
    # Get the session state for the current session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid4())
    if st.session_state.session_id not in st.session_state:
        st.session_state[st.session_state.session_id] = {}
    return st.session_state[st.session_state.session_id]

# Add input field for subject name
subject_name = st.text_input("Enter subject name:")

# Add input field for teacher name
teacher_name = st.text_input("Enter your username:")

if st.button("Submit"):
    # Fetch the data for the current week for the entered subject name and teacher name
    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
    week_data = list(data.find({"date_verified": {"$gte": week_start}, "subject_name": subject_name, "teacher_name": teacher_name}))

    if len(week_data) > 0:
        # Create a DataFrame for the week's data
        df = pd.DataFrame(week_data)

        # Create a pie chart to show number of students present today
        total_students = 20
        present_today = df[df['date_verified'] == today]['Name'].nunique()
        absent_today = total_students - present_today

        chart_data = pd.DataFrame({
            'status': ['Present', 'Absent'],
            'students': [present_today, absent_today]
        })
        
        st.subheader('Attendance Today')
        st.write(chart_data.set_index('status'))
        st.plotly_chart(px.pie(chart_data, values='students', names='status'))

        # Create a bar chart to show number of students present each day this week
        attendance_by_day = df.groupby('date_verified')['Name'].nunique().reset_index()
        bar_chart = st.container()
        with bar_chart:
            st.subheader('Attendance This Week')
            st.bar_chart(attendance_by_day.set_index('date_verified'))

        # Create a table to show student names and attendance count for the week
        attendance_table = st.container()
        with attendance_table:
            st.subheader('Attendance Table')
            attendance_count = df.groupby('Name')['date_verified'].nunique().reset_index()
            attendance_count.columns = ['Name', 'Attendance Count']
            st.write(attendance_count)
    else:
        st.warning("No data available for the entered subject name.")




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