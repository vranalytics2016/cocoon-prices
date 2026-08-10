import streamlit as st
import pandas as pd

# 1. Mobile-friendly Page Setup
st.set_page_config(
    page_title="Silk Creators - Live Cocoon Rates",
    page_icon="🐛",
    layout="centered"
)

# Custom Title Styling
st.title("🌾 Silk Creators - ರೇಷ್ಮೆ ಮಾರುಕಟ್ಟೆ")
st.caption("Dedicated to Farmers Service | 2026-27 Live Cocoon Market Rates")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysO7bTj3SGMa64vwVcwnojAdxU0J2JkdxvjeKZvuRSU/export?format=csv&gid=0"

# 2. Precise Data Loader using Header Row 4
@st.cache_data(ttl=30)  # Auto-refreshes every 30 seconds
def load_clean_data():
    # Row index 4 is the exact header row from your sheet
    df = pd.read_csv(SHEET_URL, header=4)
    
    # Strip spaces from column names
    df.columns = [str(c).strip() for c in df.columns]
    
    # Remove unnamed/blank columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # The first column is 'Date'. Keep only actual date rows (e.g. containing '/')
    date_col = df.columns[0]
    df = df[df[date_col].astype(str).str.contains('/', na=False)]
    
    # Reset index cleanly
    df = df.reset_index(drop=True)
    return df

try:
    df = load_clean_data()

    # Refresh Button
    col_title, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Identify Market Column (usually 2nd column)
    market_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]

    # 3. Filter by Market
    markets = ["All Markets"] + list(df[market_col].dropna().unique())
    selected_market = st.selectbox("🔍 Select / Filter Market (ಮಾರುಕಟ್ಟೆ):", markets)

    if selected_market != "All Markets":
        filtered_df = df[df[market_col] == selected_market]
    else:
        filtered_df = df

    # 4. Top Rate Highlights (Min / Max / Avg Cards)
    min_cols = [c for c in df.columns if 'Min' in c]
    max_cols = [c for c in df.columns if 'Max' in c]
    avg_cols = [c for c in df.columns if 'Avg' in c]

    if min_cols and max_cols and avg_cols:
        st.subheader("📊 Price Highlights (₹/Kg)")
        c1, c2, c3 = st.columns(3)

        min_val = pd.to_numeric(filtered_df[min_cols[0]], errors='coerce').min()
        max_val = pd.to_numeric(filtered_df[max_cols[0]], errors='coerce').max()
        avg_val = pd.to_numeric(filtered_df[avg_cols[0]], errors='coerce').mean()

        with c1:
            st.metric("Min Rate", f"₹{min_val:.0f}" if pd.notnull(min_val) else "N/A")
        with c2:
            st.metric("Max Rate", f"₹{max_val:.0f}" if pd.notnull(max_val) else "N/A")
        with c3:
            st.metric("Avg Rate", f"₹{avg_val:.0f}" if pd.notnull(avg_val) else "N/A")

    st.markdown("---")

    # 5. Display Clean Data Table
    st.subheader("📋 Market Wise Cocoon Rates")
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    st.success("✅ **Live Data Loaded Successfully!**")

except Exception as e:
    st.error(f"⚠️ Error loading sheet data: {e}")
