import streamlit as st
from db.mongo_client import fetch_user_notes, save_user_notes, save_session_token # IMPORT NEW FUNC

def show_dashboard():
    user = st.session_state.current_user
    st.success(f"🔓 Authentication Successful. Welcome to your secure vault, {user}!")
    
    # Fetch notes from MongoDB
    saved_notes = fetch_user_notes(user)

    st.markdown("### Your Personal Canvas")
    st.write("Write your private notes below. They will be saved securely to your account.")
    
    user_input = st.text_area("Canvas:", value=saved_notes, height=300, label_visibility="collapsed")
    
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("Save"):
            # Update notes in MongoDB
            save_user_notes(user, user_input)
            st.toast("Notes saved successfully!", icon="✅")
            
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        # Erase the token from the database for security
        save_session_token(st.session_state.current_user, "")
        
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.logout_triggered = True # Signal to app.py to delete the cookie
        st.rerun()