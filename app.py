import streamlit as st
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import face_recognition
import pickle
import os
import time

# --- INITIALIZATION ---
st.title("Selfie-Verify: Secure Account Verification")

# --- NEW MEDIAPIPE TASKS API SETUP ---
# Initialize the new FaceLandmarker
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

# Create an empty placeholder in the UI for the video feed
FRAME_WINDOW = st.empty()

# --- HELPER FUNCTION: EAR CALCULATION ---
def calculate_ear(face_landmarks):
    """Calculates the distance between the top and bottom eyelids."""
    # In the new API, landmarks are accessed as a direct list
    top_point = face_landmarks[LEFT_EYE_TOP].y
    bottom_point = face_landmarks[LEFT_EYE_BOTTOM].y
    return bottom_point - top_point

# --- ROUTE 1: REGISTRATION ---
if choice == "Register New Account":
    st.subheader("Register Your Face")
    username = st.text_input("Enter a Username:")
    
    # 1. Move the buttons OUTSIDE the while loop
    run_cam = st.checkbox("Start Camera")
    capture_button = st.button("Capture & Register")

    if run_cam and username:
        cap = cv2.VideoCapture(0)
        st.warning("Look directly at the camera and ensure good lighting.")
        
        while run_cam:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to access webcam.")
                break
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(rgb_frame)

            # 2. The logic remains inside, but checks the button state from outside
            if capture_button:
                st.info("Extracting facial features...")
                face_locations = face_recognition.face_locations(rgb_frame)
                encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                if len(encodings) > 0:
                    user_encoding = encodings[0]
                    with open(f"{username}.pkl", "wb") as f:
                        pickle.dump(user_encoding, f)
                    st.success(f"Successfully registered account for {username}!")
                    break
                else:
                    st.error("No face detected. Please try again.")
                    break # Break so it doesn't get stuck in an infinite error loop
                    
        cap.release()

# --- ROUTE 2: LOGIN & VERIFICATION ---
elif choice == "Login (Verify)":
    st.subheader("Identity Verification")
    login_user = st.text_input("Enter your Username to login:")
    
    if login_user:
        if not os.path.exists(f"{login_user}.pkl"):
            st.error(f"Account '{login_user}' not found. Please register first.")
        else:
            run_cam = st.checkbox("Start Camera for Verification")
            
            if run_cam:
                with open(f"{login_user}.pkl", "rb") as f:
                    saved_encoding = pickle.load(f)

                cap = cv2.VideoCapture(0)
                st.warning("Please BLINK to prove liveness.")
                
                blink_detected = False
                eye_closed = False
                
                while run_cam and not blink_detected:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # 1. NEW Liveness Check (MediaPipe Tasks API)
                    # Convert the numpy array into a MediaPipe Image object
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                    results = face_landmarker.detect(mp_image)
                    
                    if results.face_landmarks:
                        # Extract the first face detected
                        face_landmarks = results.face_landmarks[0]
                        ear = calculate_ear(face_landmarks)
                        
                        if ear < 0.012: # Threshold for closed eye
                            eye_closed = True
                        elif ear > 0.015 and eye_closed:
                            blink_detected = True
                            st.success("Liveness Confirmed! Matching face...")
                    
                    FRAME_WINDOW.image(rgb_frame)

                    # 2. Verification Check
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
                                st.success("Access Granted! Identity Verified.")
                            else:
                                st.error("Access Denied! Face does not match account.")
                        else:
                            st.error("Face lost during capture. Try again.")
                        break 
                
                cap.release()