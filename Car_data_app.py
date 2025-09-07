import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------
# LOGIN SYSTEM
# --------------------------
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid username or password")

# --------------------------
# LOAD DATA
# --------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("RETAIL_SALES_DATA.csv")   # <- Replace with your dataset file
    return df

# --------------------------
# PLOT FUNCTIONS
# --------------------------
def plot_bar_by_category(df: pd.DataFrame, category: str):
    counts = df[category].value_counts()
    fig, ax = plt.subplots()
    counts.plot(kind="bar", ax=ax)
    ax.set_title(f"Bar Chart by {category}")
    st.pyplot(fig)

def plot_pie_by_category(df: pd.DataFrame, category: str):
    counts = df[category].value_counts()
    fig, ax = plt.subplots()
    counts.plot(kind="pie", autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")
    ax.set_title(f"Pie Chart by {category}")
    st.pyplot(fig)

def plot_sales_trend(df: pd.DataFrame, date_col: str, sales_col: str):
    df[date_col] = pd.to_datetime(df[date_col])
    sales_trend = df.groupby(df[date_col].dt.to_period("M"))[sales_col].sum()
    fig, ax = plt.subplots()
    sales_trend.plot(ax=ax, marker="o")
    ax.set_title("📈 Monthly Sales Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Sales")
    st.pyplot(fig)

# --------------------------
# MAIN APP
# --------------------------
def main():
    st.title("🛒 Retail Sales Analysis Dashboard")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login()
        return

    # Load data
    df = load_data()

    st.subheader("📊 Dataset Preview")
    st.dataframe(df.head())

    # --------------------------
    # Data Filtering
    # --------------------------
    st.subheader("🔎 Data Filtering")
    category = st.selectbox("Select column to filter:", df.columns)
    unique_values = df[category].unique()
    selected_values = st.multiselect(f"Filter {category}", unique_values)

    if selected_values:
        df = df[df[category].isin(selected_values)]
        st.write(f"Filtered dataset ({len(df)} rows):")
        st.dataframe(df)

    # --------------------------
    # Charts
    # --------------------------
    st.subheader("📈 Visualizations")
    chart_type = st.radio("Choose chart type:", ["Bar Chart", "Pie Chart", "Sales Trend"])
    chart_category = st.selectbox("Select column for chart:", df.columns)

    if chart_type == "Bar Chart":
        plot_bar_by_category(df, chart_category)
    elif chart_type == "Pie Chart":
        plot_pie_by_category(df, chart_category)
    elif chart_type == "Sales Trend":
        # You need to tell which column is "Date" and which is "Sales"
        date_col = st.selectbox("Select Date column:", df.columns)
        sales_col = st.selectbox("Select Sales column:", df.columns)
        plot_sales_trend(df, date_col, sales_col)

    # --------------------------
    # Download Option
    # --------------------------
    st.subheader("⬇ Download Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="filtered_sales_data.csv",
        mime="text/csv"
    )

# --------------------------
# RUN APP
# --------------------------
if __name__ == "__main__":
    main()
