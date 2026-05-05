# api-demo/ui/dashboard.py
import streamlit as st
from api_client import verify_face

def show_dashboard():
    user = st.session_state.current_user
    st.success(f"🔓 Authentication Successful. Welcome back, {user}!")
    
    # Mock FinTech Interface
    col1, col2, col3 = st.columns(3)
    col1.metric("Checking Account", "$12,450.00", "+$1,200.00")
    col2.metric("Savings Account", "$45,000.00", "+$300.00")
    col3.metric("Credit Card", "$1,250.00", "-$50.00")
    
    st.markdown("---")
    st.markdown("### Wire Transfer")
    
    amount = st.number_input("Amount to transfer ($)", min_value=1, value=100)
    recipient = st.text_input("Recipient Routing Number")
    
    # STEP-UP AUTHENTICATION LOGIC
    if amount >= 5000:
        st.warning("⚠️ High-value transfer detected. Step-up biometric authentication required.")
        picture = st.camera_input("Look at the camera to authorize transfer", key="step_up_cam")
        
        if picture and st.button("Authorize High-Value Transfer"):
            with st.spinner("Verifying identity for transaction..."):
                res, status = verify_face(user, picture.getvalue())
                
                if status == 200 and res.get('match'):
                    st.success(f"✅ Identity confirmed. ${amount} successfully wired to {recipient}.")
                    st.balloons()
                else:
                    st.error("🚨 Authentication failed. Transaction blocked and flagged.")
    else:
        # Standard transfer without face auth
        if st.button("Submit Transfer"):
            st.success(f"✅ ${amount} successfully transferred to {recipient}.")
            
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()