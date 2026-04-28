import streamlit as st
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import face_recognition
import pickle
import os
import time
import numpy as np # NEW IMPORT

# --- INITIALIZATION & UI LOCKDOWN ---
st.set_page_config(page_title="FaceAuth", layout="wide")

# 1 & 3: Inject Custom CSS to freeze the layout and prevent scrolling
st.markdown("""
    <style>
    /* Lock the main container height and prevent scrolling */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        max-height: 100vh;
        overflow: hidden;
    }
    
    /* 1. The Main Outer Box */
    div[data-testid="stImage"] {
        height: 70vh !important; 
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        background-color: #000000 !important; /* Pitch black for seamless blend */
        border: 2px solid #333 !important;
        border-radius: 10px !important;
        padding: 1rem !important; 
        box-sizing: border-box !important;
        overflow: hidden !important; 
    }
    
    /* 2. The Hidden Streamlit Wrapper (This was causing the uneven padding!) */
    div[data-testid="stImage"] > div {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        height: 100% !important;
    }
    
    /* 3. The Image Itself (Stopping it from running out of bounds) */
    div[data-testid="stImage"] img {
        width: auto !important;     /* Overrides Streamlit's hardcoded inline width */
        height: auto !important;    /* Overrides Streamlit's hardcoded inline height */
        max-width: 100% !important; /* Respect the 1rem padding */
        max-height: 100% !important;/* Respect the 70vh limit */
        object-fit: contain !important; 
    }
    </style>
""", unsafe_allow_html=True)

st.title("Selfie Verify ")

# --- MEDIAPIPE TASKS API SETUP ---
try:
    base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_faces=1
    )
    face_landmarker = vision.FaceLandmarker.create_from_options(options)
except Exception as e:
    st.error("Error loading MediaPipe model. Please ensure 'face_landmarker.task' is downloaded and in the same folder.")
    st.stop()

LEFT_EYE_TOP, LEFT_EYE_BOTTOM = 159, 145

# Sidebar Navigation
menu = ["Register New Account", "Login (Verify)"]
choice = st.sidebar.selectbox("Select Action", menu)

# Create the main window placeholder
FRAME_WINDOW = st.empty()

# 2: Fixed Camera Box Standby Frame
# If the camera isn't running, show a black rectangle so the UI doesn't collapse
standby_frame = np.zeros((480, 640, 3), dtype=np.uint8)
FRAME_WINDOW.image(standby_frame, channels="RGB", width="stretch")

# --- HELPER FUNCTION: EAR CALCULATION ---
def calculate_ear(face_landmarks):
    top_point = face_landmarks[LEFT_EYE_TOP].y
    bottom_point = face_landmarks[LEFT_EYE_BOTTOM].y
    return bottom_point - top_point

# --- ROUTE 1: REGISTRATION ---
if choice == "Register New Account":
    st.sidebar.subheader("Register Your Face")
    username = st.sidebar.text_input("Enter a Username:")
    
    run_cam = st.sidebar.checkbox("Start Camera")
    capture_button = st.sidebar.button("Capture & Register")

    if run_cam and username:
        cap = cv2.VideoCapture(0)
        st.sidebar.warning("Look directly at the camera and ensure good lighting.")
        
        while run_cam:
            ret, frame = cap.read()
            if not ret:
                st.sidebar.error("Failed to access webcam.")
                break
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(rgb_frame, channels="RGB", width="stretch")

            if capture_button:
                st.sidebar.info("Extracting facial features...")
                face_locations = face_recognition.face_locations(rgb_frame)
                encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                if len(encodings) > 0:
                    user_encoding = encodings[0]
                    with open(f"{username}.pkl", "wb") as f:
                        pickle.dump(user_encoding, f)
                    st.sidebar.success(f"Successfully registered account for '{username}'!")
                    break
                else:
                    st.sidebar.error("No face detected. Please try again.")
                    break 
                    
        cap.release()

# --- ROUTE 2: LOGIN & VERIFICATION ---
elif choice == "Login (Verify)":
    st.sidebar.subheader("Identity Verification")
    login_user = st.sidebar.text_input("Enter your Username to login:")
    
    if login_user:
        if not os.path.exists(f"{login_user}.pkl"):
            st.sidebar.error(f"Account '{login_user}' not found. Please register first.")
        else:
            run_cam = st.sidebar.checkbox("Start Camera for Verification")
            
            if run_cam:
                with open(f"{login_user}.pkl", "rb") as f:
                    saved_encoding = pickle.load(f)

                cap = cv2.VideoCapture(0)
                st.sidebar.warning("Please BLINK to prove liveness.")
                
                blink_detected = False
                eye_closed = False
                
                while run_cam and not blink_detected:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                    results = face_landmarker.detect(mp_image)
                    
                    if results.face_landmarks:
                        face_landmarks = results.face_landmarks[0]
                        ear = calculate_ear(face_landmarks)
                        
                        if ear < 0.012: 
                            eye_closed = True
                        elif ear > 0.015 and eye_closed:
                            blink_detected = True
                            st.sidebar.success("Liveness Confirmed! Matching face...")
                    
                    FRAME_WINDOW.image(rgb_frame, channels="RGB", width="stretch")

                    if blink_detected:
                        time.sleep(0.5) 
                        ret, final_frame = cap.read()
                        final_rgb = cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB)
                        
                        face_locations = face_recognition.face_locations(final_rgb)
                        live_encodings = face_recognition.face_encodings(final_rgb, face_locations)

                        if len(live_encodings) > 0:
                            live_encoding = live_encodings[0]
                            matches = face_recognition.compare_faces([saved_encoding], live_encoding, tolerance=0.5)
                            
                            if matches[0]:
                                st.balloons()
                                st.sidebar.success("Access Granted! Identity Verified.")
                            else:
                                st.sidebar.error("Access Denied! Face does not match account.")
                        else:
                            st.sidebar.error("Face lost during capture. Try again.")
                        break 
                
                cap.release()