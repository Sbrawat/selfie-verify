import streamlit as st
import numpy as np
import extra_streamlit_components as stx
import datetime
from ui import auth_views, dashboard
from db.mongo_client import get_user_by_session

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

# --- COOKIE MANAGER SETUP ---
# We initialize it directly with a unique key to prevent duplicate widget errors
cookie_manager = stx.CookieManager(key="cookie_manager")

# Initialize basic session states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""

# --- SILENT LOGIN LOGIC ---
# If not currently logged in, check if a valid cookie exists in the browser
if not st.session_state.logged_in:
    saved_token = cookie_manager.get(cookie="FaceAuthToken")
    if saved_token:
        # Check database to see if this token is valid
        valid_user = get_user_by_session(saved_token)
        if valid_user:
            st.session_state.logged_in = True
            st.session_state.current_user = valid_user
            st.rerun()

# --- LOGOUT COOKIE DELETION ---
if st.session_state.get('logout_triggered', False):
    cookie_manager.delete("FaceAuthToken")
    st.session_state.logout_triggered = False

# --- SETTING THE COOKIE AFTER NEW LOGIN ---
if st.session_state.logged_in and 'session_token' in st.session_state:
    # Set the cookie to expire in 1 day
    expire_date = datetime.datetime.now() + datetime.timedelta(days=1)
    cookie_manager.set("FaceAuthToken", st.session_state.session_token, expires_at=expire_date)
    # Remove the token from session state so we don't infinitely set it
    del st.session_state['session_token']

# --- ROUTER LOGIC ---
if not st.session_state.logged_in:
    
    menu = ["Register New Account", "Login (Verify)"]
    choice = st.sidebar.selectbox("Select Action", menu)
    
    FRAME_WINDOW = st.empty()
    standby_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    FRAME_WINDOW.image(standby_frame, channels="RGB", width="stretch")

    if choice == "Register New Account":
        auth_views.show_registration(FRAME_WINDOW)
    elif choice == "Login (Verify)":
        auth_views.show_login(FRAME_WINDOW)

else:
    dashboard.show_dashboard()