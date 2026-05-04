import streamlit as st
import cv2
import time
from core.vision_engine import engine
from db.mongo_client import create_user_profile, get_user_embedding

def show_registration(FRAME_WINDOW):
    st.sidebar.subheader("Register Your Face")
    username = st.sidebar.text_input("Enter a Username:")
    run_cam = st.sidebar.checkbox("Start Camera")
    capture_button = st.sidebar.button("Capture & Register")

    if run_cam and username:
        cap = cv2.VideoCapture(0)
        st.sidebar.warning("Look directly at the camera and ensure good lighting.")
        
        while run_cam:
            ret, frame = cap.read()
            if not ret: break
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(rgb_frame, channels="RGB", use_container_width=True)

            if capture_button:
                st.sidebar.info("Extracting facial features...")
                encoding = engine.extract_embedding(rgb_frame)

                if encoding is not None:
                    # Save to MongoDB instead of pickle
                    create_user_profile(username, encoding)
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.rerun()
                else:
                    st.sidebar.error("No face detected. Please try again.")
                    break 
        cap.release()

def show_login(FRAME_WINDOW):
    st.sidebar.subheader("Identity Verification")
    login_user = st.sidebar.text_input("Enter your Username to login:")
    
    if login_user:
        saved_encoding = get_user_embedding(login_user)
        
        if saved_encoding is None:
            st.sidebar.error(f"Account '{login_user}' not found.")
        else:
            run_cam = st.sidebar.checkbox("Start Camera for Verification")
            
            if run_cam:
                cap = cv2.VideoCapture(0)
                st.sidebar.warning("Please BLINK to prove liveness.")
                
                blink_detected = False
                eye_closed = False
                
                while run_cam and not blink_detected:
                    ret, frame = cap.read()
                    if not ret: break
                    
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Call the core engine for liveness
                    is_closed = engine.check_liveness(rgb_frame)
                    if is_closed: 
                        eye_closed = True
                    elif not is_closed and eye_closed:
                        blink_detected = True
                        st.sidebar.success("Liveness Confirmed! Matching face...")
                    
                    FRAME_WINDOW.image(rgb_frame, channels="RGB", use_container_width=True)

                    if blink_detected:
                        time.sleep(0.5) 
                        ret, final_frame = cap.read()
                        final_rgb = cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB)
                        
                        live_encoding = engine.extract_embedding(final_rgb)

                        if live_encoding is not None:
                            is_match = engine.verify_match(live_encoding, saved_encoding)
                            
                            if is_match:
                                st.balloons()
                                st.session_state.logged_in = True
                                st.session_state.current_user = login_user
                                st.rerun()
                            else:
                                st.sidebar.error("Access Denied! Face does not match account.")
                        else:
                            st.sidebar.error("Face lost during capture. Try again.")
                        break 
                cap.release()