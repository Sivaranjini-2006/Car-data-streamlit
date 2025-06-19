import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# -------------------
# Login Setup
# -------------------
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Incorrect username or password")

# -------------------
# Main Dashboard
# -------------------
def dashboard():
    st.title("🚗 Car Data Analysis Dashboard")

    # Load Data
    df = pd.read_csv("CAR DETAILS FROM CAR DEKHO.csv")
    df["name_2"] = df["name"].apply(lambda x: x.split(" ")[0])

    # Sidebar filters
    st.sidebar.header("📂 Filter Cars")
    year = st.sidebar.selectbox("Select Year", sorted(df["year"].unique(), reverse=True))
    fuel = st.sidebar.multiselect("Select Fuel Type", df["fuel"].unique())

    filtered_df = df[df["year"] == year]
    if fuel:
        filtered_df = filtered_df[filtered_df["fuel"].isin(fuel)]

    st.subheader(f"🔍 Filtered Results: {len(filtered_df)} Cars")
    st.dataframe(filtered_df)

    # Plot
    st.subheader("📊 Car Brands Count")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.countplot(data=filtered_df, x="name_2", order=filtered_df["name_2"].value_counts().index)
    plt.xticks(rotation=90)
    st.pyplot(fig)

    # Logout
    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# -------------------
# App Launcher
# -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    dashboard()
else:
    login_page()
