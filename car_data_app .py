
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------
# App Header
# -------------------
def app_header():
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Car_icon_2.svg/1200px-Car_icon_2.svg.png", width=80)
    st.markdown("<h2 style='color:#e74c3c;'>🚗 Advanced Car Data Analysis Dashboard</h2>", unsafe_allow_html=True)

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
    df = pd.read_csv("UPDATED_CAR_DATA.csv")
    df["brand"] = df["name"].apply(lambda x: x.split(" ")[0])

    st.markdown("### 📝 Enter Car Details to Filter")
    with st.form("filter_form"):
        name_input = st.text_input("Enter Car Name (optional)")
        year_input = st.number_input("Enter Year", min_value=int(df["year"].min()), max_value=int(df["year"].max()), step=1)
        fuel_input = st.selectbox("Select Fuel Type", options=["All"] + sorted(df["fuel"].unique().tolist()))
        transmission_input = st.selectbox("Select Transmission", options=["All"] + sorted(df["transmission"].unique().tolist()))
        price_min = int(df["selling_price"].min())
        price_max = int(df["selling_price"].max())
        price_range = st.slider("Select Price Range (₹)", min_value=price_min, max_value=price_max, value=(price_min, price_max), step=50000)
        submitted = st.form_submit_button("Apply Filters")

    # Initial filtered dataset
    filtered_df = df.copy()

    if submitted:
        if name_input:
            filtered_df = filtered_df[filtered_df["name"].str.contains(name_input, case=False)]
        if year_input:
            filtered_df = filtered_df[filtered_df["year"] == year_input]
        if fuel_input != "All":
            filtered_df = filtered_df[filtered_df["fuel"] == fuel_input]
        if transmission_input != "All":
            filtered_df = filtered_df[filtered_df["transmission"] == transmission_input]
        filtered_df = filtered_df[
            (filtered_df["selling_price"] >= price_range[0]) &
            (filtered_df["selling_price"] <= price_range[1])
        ]

    st.subheader(f"📊 Showing {len(filtered_df)} Matching Cars")
    st.dataframe(filtered_df)

    # Visualization: Bar chart of top 5 brands
    if not filtered_df.empty:
        st.markdown("### 🏆 Top 5 Brands by Listings (Bar Chart)")
        top_brands = filtered_df["brand"].value_counts().head(5)
        fig_bar, ax_bar = plt.subplots()
        sns.barplot(x=top_brands.index, y=top_brands.values, ax=ax_bar, palette="Set2")
        ax_bar.set_ylabel("Number of Listings")
        ax_bar.set_xlabel("Brand")
        st.pyplot(fig_bar)

        # Pie Chart: Top 5 car names
        st.markdown("### 🚘 Top 5 Car Models Overall (Pie Chart)")
        top_cars = filtered_df["name"].value_counts().head(5)
        fig_pie, ax_pie = plt.subplots()
        ax_pie.pie(top_cars, labels=top_cars.index, autopct='%1.1f%%', startangle=90)
        ax_pie.axis("equal")
        st.pyplot(fig_pie)

    # Download filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button("📥 Download Filtered Data", csv, "filtered_cars.csv", "text/csv")

    # Logout
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
