import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------
# App Header & Logo
# -------------------
def app_header():
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Car_icon_2.svg/1200px-Car_icon_2.svg.png", width=80)
    st.markdown("<h2 style='color:#e74c3c;'>🚗 Car Data Analysis Dashboard</h2>", unsafe_allow_html=True)

# -------------------
# Login Page
# -------------------
def login_page():
    st.subheader("🔐 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Incorrect username or password")

# -------------------
# Dashboard Page
# -------------------
def dashboard():
    app_header()

    # Load data
    df = pd.read_csv("CAR DETAILS FROM CAR DEKHO.csv")
    df["name_2"] = df["name"].apply(lambda x: x.split(" ")[0])

    # Form starts here
    with st.form("filter_form"):
        st.markdown("### 📋 Filter Car Data")

        search_text = st.text_input("🔍 Search by Car Name or Brand (optional)")
        year = st.selectbox("📅 Select Year", sorted(df["year"].unique(), reverse=True))
        fuel = st.multiselect("⛽ Select Fuel Type", df["fuel"].unique())

        submitted = st.form_submit_button("Apply Filters")

    # Show results after submit
    if submitted:
        filtered_df = df.copy()

        if search_text:
            filtered_df = filtered_df[filtered_df["name"].str.contains(search_text, case=False)]

        filtered_df = filtered_df[filtered_df["year"] == year]

        if fuel:
            filtered_df = filtered_df[filtered_df["fuel"].isin(fuel)]

        st.subheader(f"📊 {len(filtered_df)} Cars Found")
        st.dataframe(filtered_df)

        # Download CSV
        csv = filtered_df.to_csv(index=False)
        st.download_button("📥 Download Filtered Data", csv, "filtered_cars.csv", "text/csv")

        # Top 5 brands bar chart
        st.subheader("🏆 Top 5 Car Brands")
        top_brands = filtered_df["name_2"].value_counts().head(5)
        st.bar_chart(top_brands)

        # Fuel type pie chart
        st.subheader("⛽ Fuel Type Distribution")
        fuel_counts = filtered_df["fuel"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(fuel_counts, labels=fuel_counts.index, autopct='%1.1f%%', startangle=90)
        ax1.axis("equal")
        st.pyplot(fig1)

        # Logout button
        if st.button("🔓 Logout"):
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
