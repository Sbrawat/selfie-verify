# api-demo/app.py
import streamlit as st
from ui import auth_views, dashboard

st.set_page_config(page_title="SecureBank FaceAuth", layout="centered")
st.title("🏦 SecureBank App")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""

if not st.session_state.logged_in:
    menu = ["Login to Account", "Open New Account"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Open New Account":
        auth_views.show_registration()
    elif choice == "Login to Account":
        auth_views.show_login()
else:
    dashboard.show_dashboard()