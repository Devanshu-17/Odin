import streamlit as st

def set_theme(theme):
    if theme == 'light':
        primaryColor = "#6eb52f"
        backgroundColor = "#f0f0f5"
        secondaryBackgroundColor = "#e0e0ef"
        textColor = "#262730"
        font = "sans-serif"
    elif theme == 'dark':
        primaryColor = "#d33682"
        backgroundColor = "#002b36"
        secondaryBackgroundColor = "#586e75"
        textColor = "#fafafa"
        font = "sans-serif"
    else:
        raise ValueError(f"Invalid theme: {theme}")

    st.markdown(f"""
        <style>
            :root {{
                --primary-color: {primaryColor};
                --background-color: {backgroundColor};
                --secondary-background-color: {secondaryBackgroundColor};
                --text-color: {textColor};
                --font: {font};
            }}
            body {{
                color: var(--text-color);
                background-color: var(--background-color);
                font-family: var(--font);
            }}
            .stButton button {{
                background-color: var(--primary-color);
                color: var(--text-color);
            }}
            .stTextInput input {{
                background-color: var(--secondary-background-color);
            }}
        </style>
        """, unsafe_allow_html=True)

theme = st.radio("Select a theme", ["light", "dark"])
set_theme(theme)
