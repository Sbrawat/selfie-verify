import streamlit as st
import numpy as np
from ui import auth_views, dashboard

# --- INITIALIZATION & UI LOCKDOWN ---
st.set_page_config(page_title="FaceAuth", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; padding-bottom: 0rem !important; max-height: 100vh; overflow: hidden; }
    div[data-testid="stImage"] { height: 70vh !important; display: flex !important; justify-content: center !important; align-items: center !important; background-color: #000000 !important; border: 2px solid #333 !important; border-radius: 10px !important; padding: 1rem !important; box-sizing: border-box !important; overflow: hidden !important; }
    div[data-testid="stImage"] > div { display: flex !important; justify-content: center !important; align-items: center !important; width: 100% !important; height: 100% !important; }
    div[data-testid="stImage"] img { width: auto !important; height: auto !important; max-width: 100% !important; max-height: 100% !important; object-fit: contain !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🔐 FaceAuth: Secure Account Verification")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""

# --- ROUTER LOGIC ---
if not st.session_state.logged_in:
    
    menu = ["Register New Account", "Login (Verify)"]
    choice = st.sidebar.selectbox("Select Action", menu)
    
    # Placeholder for video UI to maintain strict CSS layout
    FRAME_WINDOW = st.empty()
    standby_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    FRAME_WINDOW.image(standby_frame, channels="RGB", use_container_width=True)

    if choice == "Register New Account":
        auth_views.show_registration(FRAME_WINDOW)
    elif choice == "Login (Verify)":
        auth_views.show_login(FRAME_WINDOW)

else:
    # User is logged in, show the secure dashboard
    dashboard.show_dashboard()