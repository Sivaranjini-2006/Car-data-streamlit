import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------
# Logo + Heading
# -------------------
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
    # Load data
    df = pd.read_csv("CAR DETAILS FROM CAR DEKHO.csv")
    df["name_2"] = df["name"].apply(lambda x: x.split(" ")[0])

    # Optional search bar
    search_text = st.text_input("🔍 Search by car name or brand")
    if search_text:
        df = df[df["name"].str.contains(search_text, case=False)]

    # Sidebar filters
    st.sidebar.header("📂 Filter Cars")
    year = st.sidebar.selectbox("Select Year", sorted(df["year"].unique(), reverse=True))
    fuel = st.sidebar.multiselect("Select Fuel Type", df["fuel"].unique())

    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Apply filters
    filtered_df = df[df["year"] == year]
    if fuel:
        filtered_df = filtered_df[filtered_df["fuel"].isin(fuel)]

    # Show filtered results
    st.subheader(f"🔍 Filtered Results: {len(filtered_df)} Cars")
    st.dataframe(filtered_df)

    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button("📥 Download CSV", csv, "filtered_cars.csv", "text/csv")

    # Top brands chart
    st.subheader("🏆 Top 5 Car Brands")
    top_brands = df["name_2"].value_counts().head(5)
    st.bar_chart(top_brands)

    # Fuel type pie chart
    st.subheader("⛽ Fuel Type Distribution")
    fuel_counts = df["fuel"].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(fuel_counts, labels=fuel_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

# -------------------
# App Launcher
# -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    dashboard()
else:
    login_page()
