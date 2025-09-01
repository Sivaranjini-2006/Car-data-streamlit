import os
import io
import zipfile
import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import Optional, Tuple, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

DB_PATH = "sales_app.db"

# ----------------------------
# Utilities: Database & Auth
# ----------------------------

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                filename TEXT NOT NULL,
                uploaded_at TEXT NOT NULL,
                rows INTEGER,
                cols INTEGER
            )
            """
        )
        conn.commit()


# Simple salted SHA-256 (sufficient for demo). For production, use bcrypt/argon2.

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return h, salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    return hashlib.sha256((salt + password).encode()).hexdigest() == password_hash


def register_user(username: str, password: str) -> Tuple[bool, str]:
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            h, salt = hash_password(password)
            cur.execute(
                "INSERT INTO users (username, password_hash, salt, created_at) VALUES (?, ?, ?, ?)",
                (username, h, salt, datetime.utcnow().isoformat()),
            )
            conn.commit()
        return True, "Account created successfully. Please log in."
    except sqlite3.IntegrityError:
        return False, "Username already exists. Choose another."
    except Exception as e:
        return False, f"Error: {e}"


def authenticate(username: str, password: str) -> bool:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT password_hash, salt FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if not row:
            return False
        pw_hash, salt = row
        return verify_password(password, pw_hash, salt)


# ----------------------------
# App State & Navigation
# ----------------------------

def require_session():
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    if "nav" not in st.session_state:
        st.session_state.nav = "Login"


def navbar():
    with st.sidebar:
        st.title("🧭 Navigation")
        if st.session_state.auth_user:
            choice = st.radio(
                "Go to",
                ["Upload & Analyze", "EDA & Insights", "Downloads", "Account"],
                index=["Upload & Analyze", "EDA & Insights", "Downloads", "Account"].index(st.session_state.nav)
                if st.session_state.nav in ["Upload & Analyze", "EDA & Insights", "Downloads", "Account"]
                else 0,
            )
            st.session_state.nav = choice
            st.markdown("---")
            if st.button("🚪 Logout"):
                st.session_state.auth_user = None
                st.session_state.df = None
                st.session_state.nav = "Login"
                st.success("Logged out.")
        else:
            st.info("Please log in or register.")


# ----------------------------
# Auth Screens
# ----------------------------

def login_screen():
    st.title("🔐 Sales Analysis — Login")
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In")
        if submitted:
            if authenticate(username, password):
                st.session_state.auth_user = username
                st.session_state.nav = "Upload & Analyze"
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid username or password.")

    with tab_register:
        with st.form("register_form"):
            r_user = st.text_input("Create username")
            r_pass = st.text_input("Create password", type="password")
            r_pass2 = st.text_input("Confirm password", type="password")
            r_submit = st.form_submit_button("Create Account")
        if r_submit:
            if not r_user or not r_pass:
                st.warning("Username and password are required.")
            elif r_pass != r_pass2:
                st.warning("Passwords do not match.")
            else:
                ok, msg = register_user(r_user, r_pass)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


# ----------------------------
# Data Loading & Mapping
# ----------------------------

@st.cache_data(show_spinner=False)
def read_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    try:
        if filename.lower().endswith(".csv"):
            return pd.read_csv(io.BytesIO(file_bytes))
        elif filename.lower().endswith((".xls", ".xlsx")):
            return pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise ValueError("Unsupported file type. Upload CSV or Excel.")
    except Exception as e:
        raise e


def detect_date_column(df: pd.DataFrame) -> Optional[str]:
    for col in df.columns:
        try:
            parsed = pd.to_datetime(df[col], errors="raise", dayfirst=False)
            # Heuristic: at least 60% parse success or dtype already datetime
            if pd.api.types.is_datetime64_any_dtype(parsed) or parsed.notna().mean() > 0.6:
                return col
        except Exception:
            continue
    return None


# ----------------------------
# Analysis Helpers
# ----------------------------

def prepare_dataframe(df: pd.DataFrame, mappings: dict) -> pd.DataFrame:
    df = df.copy()
    # Ensure columns exist
    date_col = mappings.get("date")
    region_col = mappings.get("region")
    product_col = mappings.get("product")
    qty_col = mappings.get("quantity")
    price_col = mappings.get("unit_price")
    revenue_col = mappings.get("revenue")

    # Parse date
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])

    # Create revenue if missing
    if not revenue_col:
        if qty_col and price_col and qty_col in df.columns and price_col in df.columns:
            df["Revenue"] = pd.to_numeric(df[qty_col], errors="coerce").fillna(0) * \
                             pd.to_numeric(df[price_col], errors="coerce").fillna(0)
            revenue_col = "Revenue"
        else:
            # fallback: if a likely revenue column exists
            candidates = [c for c in df.columns if c.lower() in ("revenue", "sales", "amount", "total")]
            if candidates:
                revenue_col = candidates[0]
            else:
                df["Revenue"] = 0.0
                revenue_col = "Revenue"

    # Normalize text columns
    for c in [region_col, product_col]:
        if c and c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    # Attach canonical names for downstream
    df = df.rename(columns={
        date_col: "_Date",
        region_col: "_Region",
        product_col: "_Product",
        qty_col: "_Qty",
        price_col: "_UnitPrice",
        revenue_col: "_Revenue",
    })
    return df


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    f = df.copy()
    # Date filter
    date_min = f["_Date"].min() if "_Date" in f.columns else None
    date_max = f["_Date"].max() if "_Date" in f.columns else None

    st.subheader("🔎 Filters")
    if date_min is not None and date_max is not None:
        d1, d2 = st.date_input(
            "Date range",
            value=(date_min.date(), date_max.date()),
            min_value=date_min.date(),
            max_value=date_max.date(),
        )
        mask_date = (f["_Date"].dt.date >= d1) & (f["_Date"].dt.date <= d2)
        f = f[mask_date]

    # Region & Product filters
    if "_Region" in f.columns:
        regions = sorted([r for r in f["_Region"].dropna().unique()])
        pick_regions = st.multiselect("Region", regions, default=regions)
        f = f[f["_Region"].isin(pick_regions)]

    if "_Product" in f.columns:
        products = sorted([p for p in f["_Product"].dropna().unique()])
        default_products = products[: min(10, len(products))]
        pick_products = st.multiselect("Product", products, default=default_products)
        f = f[f["_Product"].isin(pick_products)]

    st.caption(f"Filtered rows: {len(f):,}")
    return f


def show_metrics(df: pd.DataFrame):
    st.subheader("📈 KPIs")
    total_rev = float(df["_Revenue"].sum()) if "_Revenue" in df.columns else 0.0
    total_qty = float(df["_Qty"].sum()) if "_Qty" in df.columns else np.nan
    orders = len(df)
    aov = (total_rev / orders) if orders else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"₹{total_rev:,.2f}")
    c2.metric("Orders", f"{orders:,}")
    c3.metric("Total Quantity", f"{0 if np.isnan(total_qty) else int(total_qty):,}")
    c4.metric("Avg Order Value", f"₹{aov:,.2f}")


def plot_line_trend(df: pd.DataFrame):
    if "_Date" not in df.columns or "_Revenue" not in df.columns:
        return None
    st.subhea = (
        df.groupby(pd.Grouper(key="_Date", freq="MS"))["_Revenue"].sum().reset_index()
    )
    fig, ax = plt.subplots()
    ax.plot(ts["_Date"], ts["_Revenue"], marker="o")
    ax.set_title("Monthly Revenue")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    st.pyplot(fig, use_container_width=True)
    return fig


def plot_bar_by_category(df: pd.DataFrame], category: str):
    # Typo guard intentionally corrected below in definition used by app.
    pass


def plot_bar_by_category_fixed(df: pd.DataFrame, category: str):
    if category not in df.columns or "_Revenue" not in df.columns:
        return None
    st.subheader(f"🏷️ Revenue by {category[1:]}")
    s = df.groupby(category)["_Revenue"].sum().sort_values(ascending=False).head(15)
    fig, ax = plt.subplots()
    s.plot(kind="bar", ax=ax)
    ax.set_title(f"Revenue by {category[1:]}")
    ax.set_xlabel(category[1:])
    ax.set_ylabel("Revenue")
    st.pyplot(fig, use_container_width=True)
    return fig


def plot_pie_share(df: pd.DataFrame, category: str):
    if category not in df.columns or "_Revenue" not in df.columns:
        return None
    st.subheader(f"🥧 Share by {category[1:]}")
    s = df.groupby(category)["_Revenue"].sum().sort_values(ascending=False).head(8)
    fig, ax = plt.subplots()
    ax.pie(s.values, labels=s.index, autopct="%1.1f%%")
    ax.set_title(f"Revenue Share by {category[1:]}")
    st.pyplot(fig, use_container_width=True)
    return fig


def top_table(df: pd.DataFrame, category: str, n: int = 10):
    if category not in df.columns or "_Revenue" not in df.columns:
        return
    st.subheader(f"🏆 Top {n} {category[1:]} by Revenue")
    tab = (
        df.groupby(category)
        .agg(Revenue=("_Revenue", "sum"), Orders=("_Revenue", "count"))
        .sort_values("Revenue", ascending=False)
        .head(n)
    )
    st.dataframe(tab)


# ----------------------------
# Pages
# ----------------------------

def page_upload_analyze():
    st.title("📊 Upload & Analyze")
    st.write("Upload your sales data (CSV/Excel), map columns, apply filters, and see insights.")

    up = st.file_uploader("Upload file", type=["csv", "xls", "xlsx"])
    if up is not None:
        try:
            data = up.read()
            df = read_file(data, up.name)
            # Save upload metadata
            with get_conn() as conn:
                conn.execute(
                    "INSERT INTO uploads (username, filename, uploaded_at, rows, cols) VALUES (?, ?, ?, ?, ?)",
                    (
                        st.session_state.auth_user,
                        up.name,
                        datetime.utcnow().isoformat(),
                        int(df.shape[0]),
                        int(df.shape[1]),
                    ),
                )
                conn.commit()

            st.success(f"Loaded: {up.name} — {df.shape[0]:,} rows × {df.shape[1]:,} cols")

            # Column mapping UI
            st.subheader("🧭 Map Your Columns")
            cols = ["(none)"] + list(df.columns)
            suggested_date = detect_date_column(df)
            date_col = st.selectbox("Date column", cols, index=(cols.index(suggested_date) if suggested_date in cols else 0))
            region_col = st.selectbox("Region column", cols, index=0)
            product_col = st.selectbox("Product column", cols, index=0)
            qty_col = st.selectbox("Quantity column", cols, index=0)
            price_col = st.selectbox("Unit Price column", cols, index=0)
            revenue_col = st.selectbox("Revenue column (if exists)", cols, index=0)

            mappings = {
                "date": None if date_col == "(none)" else date_col,
                "region": None if region_col == "(none)" else region_col,
                "product": None if product_col == "(none)" else product_col,
                "quantity": None if qty_col == "(none)" else qty_col,
                "unit_price": None if price_col == "(none)" else price_col,
                "revenue": None if revenue_col == "(none)" else revenue_col,
            }

            if st.button("✅ Prepare Data"):
                st.session_state.df = prepare_dataframe(df, mappings)
                st.success("Data prepared. Scroll for filters and insights.")

    # If we have data prepared, show filters & visuals
    if st.session_state.get("df") is not None:
        f = apply_filters(st.session_state.df)
        show_metrics(f)
        figs = {}
        fig_trend = plot_line_trend(f)
        if fig_trend:
            figs["trend_monthly.png"] = fig_trend
        fig_region_bar = plot_bar_by_category_fixed(f, "_Region")
        if fig_region_bar:
            figs["bar_region.png"] = fig_region_bar
        fig_product_bar = plot_bar_by_category_fixed(f, "_Product")
        if fig_product_bar:
            figs["bar_product.png"] = fig_product_bar
        fig_region_pie = plot_pie_share(f, "_Region")
        if fig_region_pie:
            figs["pie_region.png"] = fig_region_pie
        fig_product_pie = plot_pie_share(f, "_Product")
        if fig_product_pie:
            figs["pie_product.png"] = fig_product_pie

        st.session_state.filtered_df = f
        st.session_state.figures = figs


def page_eda():
    st.title("🔬 EDA & Insights")
    df = st.session_state.get("filtered_df")
    if df is None:
        st.info("Go to 'Upload & Analyze' to upload and prepare data first.")
        return

    # Missing values
    st.subheader("🚩 Missing Values")
    miss = df.isna().mean().sort_values(ascending=False)
    st.dataframe((miss * 100).round(2).rename("% Missing").to_frame())

    # Top tables
    top_table(df, "_Region", n=10)
    top_table(df, "_Product", n=10)

    # Correlations (numeric only)
    st.subheader("🔗 Correlation (numeric)")
    num = df.select_dtypes(include=[np.number])
    if not num.empty and num.shape[1] > 1:
        corr = num.corr(numeric_only=True)
        st.dataframe(corr)
    else:
        st.caption("Not enough numeric columns for correlation.")


def page_downloads():
    st.title("⬇️ Downloads")
    df = st.session_state.get("filtered_df")
    figs = st.session_state.get("figures", {})
    if df is None:
        st.info("No filtered data available. Use 'Upload & Analyze' first.")
        return

    # CSV download of filtered data
    csv_bytes = df.to_csv(index=False).encode()
    st.download_button(
        "Download Filtered CSV",
        data=csv_bytes,
        file_name="filtered_sales.csv",
        mime="text/csv",
    )

    # Summary CSV (KPI snapshot)
    total_rev = float(df["_Revenue"].sum()) if "_Revenue" in df.columns else 0.0
    orders = len(df)
    aov = (total_rev / orders) if orders else 0.0
    summary = pd.DataFrame(
        {
            "Metric": ["Total Revenue", "Orders", "Avg Order Value"],
            "Value": [total_rev, orders, aov],
        }
    )
    st.download_button(
        "Download KPI Summary (CSV)",
        data=summary.to_csv(index=False).encode(),
        file_name="kpi_summary.csv",
        mime="text/csv",
    )

    # ZIP of chart images
    if figs:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for name, fig in figs.items():
                img = io.BytesIO()
                fig.savefig(img, format="png", bbox_inches="tight")
                z.writestr(name, img.getvalue())
        st.download_button(
            "Download Charts (ZIP)",
            data=buf.getvalue(),
            file_name="charts.zip",
            mime="application/zip",
        )
    else:
        st.caption("No charts generated yet.")


def page_account():
    st.title("👤 Account")
    st.write(f"Logged in as **{st.session_state.auth_user}**")

    with get_conn() as conn:
        df = pd.read_sql_query(
            "SELECT filename, uploaded_at, rows, cols FROM uploads WHERE username=? ORDER BY uploaded_at DESC",
            conn,
            params=(st.session_state.auth_user,),
        )
    st.subheader("📥 Upload History")
    if df.empty:
        st.caption("No uploads yet.")
    else:
        st.dataframe(df)


# ----------------------------
# Main
# ----------------------------

def main():
    st.set_page_config(page_title="Sales Analysis", page_icon="💹", layout="wide")
    init_db()
    require_session()
    navbar()

    if not st.session_state.auth_user:
        login_screen()
        return

    page = st.session_state.nav
    if page == "Upload & Analyze":
        page_upload_analyze()
    elif page == "EDA & Insights":
        page_eda()
    elif page == "Downloads":
        page_downloads()
    elif page == "Account":
        page_account()
    else:
        page_upload_analyze()


# Correct the earlier placeholder/typo function reference
plot_bar_by_category = plot_bar_by_category_fixed

if __name__ == "__main__":
    main() 

