import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
-------------------

App Header & Logo

-------------------

def app_header(): st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Car_icon_2.svg/1200px-Car_icon_2.svg.png", width=80) st.markdown("<h2 style='color:#e74c3c;'>🚗 Advanced Car Data Analysis Dashboard</h2>", unsafe_allow_html=True)

-------------------

Login Page

-------------------

def login_page(): st.subheader("🔐 Login Required") username = st.text_input("Username") password = st.text_input("Password", type="password") if st.button("Login"): if username == "admin" and password == "1234": st.session_state.logged_in = True st.rerun() else: st.error("❌ Incorrect username or password")

-------------------

Dashboard Page

-------------------

def dashboard(): app_header()

# Load data
df = pd.read_csv("UPDATED_CAR_DATA.csv")
df["brand"] = df["name"].apply(lambda x: x.split(" ")[0])

# Sidebar filters
st.sidebar.header("🔧 Filter Options")
brands = st.sidebar.multiselect("Select Brand(s)", df["brand"].unique())
fuel = st.sidebar.multiselect("Select Fuel Type(s)", df["fuel"].unique())
transmission = st.sidebar.multiselect("Select Transmission", df["transmission"].unique())
owner = st.sidebar.multiselect("Select Owner Type", df["owner"].unique())
year_range = st.sidebar.slider("Select Year Range", int(df["year"].min()), int(df["year"].max()), (2018, 2024))

# Filter data
filtered_df = df[
    (df["year"] >= year_range[0]) & (df["year"] <= year_range[1])
]
if brands:
    filtered_df = filtered_df[filtered_df["brand"].isin(brands)]
if fuel:
    filtered_df = filtered_df[filtered_df["fuel"].isin(fuel)]
if transmission:
    filtered_df = filtered_df[filtered_df["transmission"].isin(transmission)]
if owner:
    filtered_df = filtered_df[filtered_df["owner"].isin(owner)]

st.subheader(f"📊 Showing {len(filtered_df)} Cars")
st.dataframe(filtered_df)

# Visualizations
if not filtered_df.empty:
    st.markdown("### 📈 Price vs. Year")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_df, x="year", y="selling_price", hue="fuel", ax=ax)
    st.pyplot(fig)

    st.markdown("### 🏆 Top 5 Brands by Listings (Pie Chart)")
    top_brands_pie = filtered_df["brand"].value_counts().head(5)
    fig_pie1, ax_pie1 = plt.subplots()
    ax_pie1.pie(top_brands_pie, labels=top_brands_pie.index, autopct='%1.1f%%', startangle=90)
    ax_pie1.axis("equal")
    st.pyplot(fig_pie1)

    st.markdown("### 🚘 Top 5 Car Models Overall (Pie Chart)")
    top_cars = filtered_df["name"].value_counts().head(5)
    fig2, ax2 = plt.subplots()
    ax2.pie(top_cars, labels=top_cars.index, autopct='%1.1f%%', startangle=90)
    ax2.axis("equal")
    st.pyplot(fig2)

    st.markdown("### ⚙️ Correlation Heatmap")
    numeric_df = filtered_df[["year", "selling_price", "km_driven", "mileage", "seats"]].dropna()
    corr = numeric_df.corr()
    fig3, ax3 = plt.subplots()
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax3)
    st.pyplot(fig3)

# Download CSV
csv = filtered_df.to_csv(index=False)
st.download_button("📥 Download Filtered Data", csv, "filtered_cars.csv", "text/csv")

# Logout
if st.button("🔓 Logout"):
    st.session_state.logged_in = False
    st.rerun()

-------------------

App Launcher

-------------------

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if st.session_state.logged_in: dashboard() else: login_page()

