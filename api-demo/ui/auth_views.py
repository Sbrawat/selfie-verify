# api-demo/ui/auth_views.py
import streamlit as st
from api_client import register_face, verify_face

def show_registration():
    st.subheader("Open a SecureBank Account")
    username = st.text_input("Choose a Username:")
    
    # Streamlit's native camera widget returns an image file object
    picture = st.camera_input("Take a selfie to register")
    
    if picture and username:
        if st.button("Register via API"):
            with st.spinner("Talking to Identity Server..."):
                # .getvalue() extracts the raw bytes from the camera image
                res_data, status_code = register_face(username, picture.getvalue())
                
                if status_code == 200:
                    st.success(f"Welcome to SecureBank, {username}!")
                    # In a real app, you might auto-login here. 
                    # For demo purposes, we will ask them to log in to get a token.
                else:
                    st.error(f"Registration Failed: {res_data.get('detail')}")

def show_login():
    st.subheader("SecureBank Identity Verification")
    login_user = st.text_input("Enter your Username:")
    
    if login_user:
        picture = st.camera_input("Verify your identity")
        
        if picture and st.button("Login"):
            with st.spinner("Analyzing biometric data..."):
                res_data, status_code = verify_face(login_user, picture.getvalue())
                
                if status_code == 200 and res_data.get('match'):
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.session_state.session_token = res_data.get('session_token')
                    st.rerun()
                else:
                    error_msg = res_data.get('detail', 'Face does not match.')
                    st.error(f"Access Denied: {error_msg}")