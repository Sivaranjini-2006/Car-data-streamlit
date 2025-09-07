import streamlit as st

st.set_page_config(page_title="Retail Sales Dashboard", page_icon="🛒")

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# -----------------------
# Registration Page
# -----------------------
def registration_page():
    st.title("📝 User Registration")
    username = st.text_input("Enter Username")
    email = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")

    if st.button("Register"):
        st.success(f"✅ User {username} registered successfully! (Mock Only)")

    if st.button("Go to Login"):
        st.session_state["page"] = "login"

# -----------------------
# Login Page
# -----------------------
def login_page():
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Mock validation
        if email == "test@test.com" and password == "1234":
            st.session_state["logged_in"] = True
            st.session_state["username"] = "TestUser"
            st.success("✅ Login successful!")
            st.session_state["page"] = "home"
        else:
            st.error("❌ Invalid email or password (mock only)")

    if st.button("Go to Register"):
        st.session_state["page"] = "register"

# -----------------------
# Home Page
# -----------------------
def home_page():
    st.title("🏠 Welcome to Retail Sales Dashboard")
    st.write(f"Hello, {st.session_state.get('username', 'User')} 👋")
    st.write("This is just a mock showcase of how the project will look after login.")
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["page"] = "login"

# -----------------------
# Main App Logic
# -----------------------
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if st.session_state["page"] == "login":
    login_page()
elif st.session_state["page"] == "register":
    registration_page()
elif st.session_state["page"] == "home":
    home_page()
