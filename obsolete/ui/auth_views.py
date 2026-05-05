import streamlit as st
import cv2
import time
import uuid # NEW IMPORT
import datetime # NEW IMPORT
from core.vision_engine import engine
from db.mongo_client import create_user_profile, get_user_embedding, save_session_token # IMPORT NEW FUNC

def show_registration(FRAME_WINDOW):
    st.sidebar.subheader("Register Your Face")
    username = st.sidebar.text_input("Enter a Username:")
    
    # 1. We removed the manual capture button
    run_cam = st.sidebar.checkbox("Start Camera")

    if run_cam and username:
        cap = cv2.VideoCapture(0)
        # 2. Updated instructions
        st.sidebar.warning("Please BLINK to capture and register your face.")
        
        blink_detected = False
        eye_closed = False
        
        while run_cam and not blink_detected:
            ret, frame = cap.read()
            if not ret: break
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 3. Inject the liveness check
            is_closed = engine.check_liveness(rgb_frame)
            if is_closed: 
                eye_closed = True
            elif not is_closed and eye_closed:
                blink_detected = True
                st.sidebar.success("Liveness Confirmed! Extracting features...")
            
            FRAME_WINDOW.image(rgb_frame, channels="RGB", width="strech")

            # 4. Process the registration once a blink happens
            if blink_detected:
                time.sleep(0.5) # Wait half a second so their eyes are open in the final picture
                ret, final_frame = cap.read()
                final_rgb = cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB)
                
                encoding = engine.extract_embedding(final_rgb)

                if encoding is not None:
                    create_user_profile(username, encoding)
                    
                    token = uuid.uuid4().hex
                    save_session_token(username, token)
                    st.session_state.session_token = token
                    
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
                    
                    FRAME_WINDOW.image(rgb_frame, channels="RGB", width="stretch")

                    if blink_detected:
                        time.sleep(0.5) 
                        ret, final_frame = cap.read()
                        final_rgb = cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB)
                        
                        live_encoding = engine.extract_embedding(final_rgb)

                        if live_encoding is not None:
                            is_match = engine.verify_match(live_encoding, saved_encoding)
                            
                            if is_match:
                                st.balloons()
                                
                                # --- NEW: GENERATE & SAVE SESSION TOKEN ---
                                token = uuid.uuid4().hex
                                save_session_token(login_user, token)
                                st.session_state.session_token = token
                                
                                st.session_state.logged_in = True
                                st.session_state.current_user = login_user
                                st.rerun()
                            else:
                                st.sidebar.error("Access Denied! Face does not match account.")
                        else:
                            st.sidebar.error("Face lost during capture. Try again.")
                        break 
                cap.release()