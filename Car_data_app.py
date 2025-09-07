import streamlit as st
import re

st.set_page_config(page_title="Retail Sales Dashboard", page_icon="🛒")

# Initialize session
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "login"

# -----------------------
# Login Page
# -----------------------
def login_page():
    st.title("🔐 Login to Retail Dashboard")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email == "test@gmail.com" and password == "1234":
            st.session_state["logged_in"] = True
            st.session_state["username"] = email
            st.session_state["page"] = "home"
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid email or password")

    st.markdown("---")
    if st.button("Register Here"):
        st.session_state["page"] = "register"

# -----------------------
# Registration Page
# -----------------------
def registration_page():
    st.title("📝 Register New Account")
    username = st.text_input("Enter Username")
    email = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")

    if st.button("Register"):
        # Email validation
        if not email.endswith("@gmail.com"):
            st.error("❌ Email must be a Gmail address (example: name@gmail.com).")
            return
        
        # Username validation (only letters and numbers allowed)
        if not re.match("^[A-Za-z0-9]+$", username):
            st.error("❌ Username should only contain letters and numbers (no special symbols).")
            return

        # Mock registration success
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["page"] = "home"
        st.success(f"✅ Welcome {username}! Your account has been created.")

# -----------------------
# Home Page
# -----------------------
def home_page():
    st.title("🏠 Welcome to Retail Sales Dashboard")
    st.write(f"Hello, {st.session_state.get('username', 'User')} 👋")
    st.write("This is a mock home page where we’ll later add charts, reports, and analytics.")

    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["page"] = "login"

# -----------------------
# Main App Logic
# -----------------------
if st.session_state["page"] == "login":
    login_page()
elif st.session_state["page"] == "register":
    registration_page()
elif st.session_state["page"] == "home":
    if st.session_state["logged_in"]:
        home_page()
    else:
        st.session_state["page"] = "login"
        login_page()
