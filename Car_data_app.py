import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(page_title="Car Data Analysis", layout="wide")

# Title
st.title("🚗 Car Data Analysis Dashboard")

# Load the data
@st.cache_data
def load_data():
    return pd.read_csv("UPDATED_CAR_DATA.csv")

df = load_data()

# Show dataset
if st.checkbox("Show Raw Data"):
    st.write(df)

# Sidebar filters
st.sidebar.header("Filter Options")

# Brand filter
brands = df['Brand'].unique()
selected_brands = st.sidebar.multiselect("Select Brand(s)", brands, default=brands)

# Fuel Type filter
fuel_types = df['Fuel_Type'].unique()
selected_fuels = st.sidebar.multiselect("Select Fuel Type(s)", fuel_types, default=fuel_types)

# Price filter
min_price, max_price = int(df['Price'].min()), int(df['Price'].max())
price_range = st.sidebar.slider("Select Price Range", min_price, max_price, (min_price, max_price))

# Filter data
filtered_df = df[
    (df['Brand'].isin(selected_brands)) &
    (df['Fuel_Type'].isin(selected_fuels)) &
    (df['Price'] >= price_range[0]) &
    (df['Price'] <= price_range[1])
]

# Display summary
st.subheader("Filtered Dataset Summary")
st.write(f"Total Cars: {filtered_df.shape[0]}")
st.dataframe(filtered_df.head())

# Visualizations
st.subheader("📊 Visualizations")

# 1. Price distribution
fig1, ax1 = plt.subplots()
sns.histplot(filtered_df['Price'], kde=True, ax=ax1)
ax1.set_title("Price Distribution")
st.pyplot(fig1)

# 2. Fuel Type count
fig2, ax2 = plt.subplots()
sns.countplot(data=filtered_df, x='Fuel_Type', palette='Set2', ax=ax2)
ax2.set_title("Fuel Type Distribution")
st.pyplot(fig2)

# 3. Price by Brand
fig3, ax3 = plt.subplots(figsize=(12, 5))
sns.boxplot(data=filtered_df, x='Brand', y='Price', palette='Set3', ax=ax3)
ax3.set_title("Price by Brand")
ax3.tick_params(axis='x', rotation=45)
st.pyplot(fig3)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit | Dataset: `UPDATED_CAR_DATA.csv`")
