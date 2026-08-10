import streamlit as st
import pandas as pd

# 1. Mobile-friendly Page Setup
st.set_page_config(
    page_title="Silk Creators - Live Cocoon Rates",
    page_icon="🐛",
    layout="centered"
)

# Custom Styling for Farmers Mobile View
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #1E3A8A; text-align: center; }
    .sub-header { font-size: 14px; color: #4B5563; text-align: center; margin-bottom: 15px; }
    .metric-card { background-color: #F3F4F6; padding: 10px; border-radius: 8px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Branding Header
st.markdown("<div class='main-header'>🌾 Silk Creators - ರೇಷ್ಮೆ ಮಾರುಕಟ್ಟೆ</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Dedicated to Farmers Service | 2026-27 Cocoon Market Rates</div>", unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysO7bTj3SGMa64vwVcwnojAdxU0J2JkdxvjeKZvuRSU/export?format=csv&gid=0"

# 2. Smart Data Loader (Handles Header Rows Automatically)
@st.cache_data(ttl=60) # Refreshes every 60 seconds
def load_silk_data():
    # Read raw sheet without header assumption
    raw_df = pd.read_csv(SHEET_URL, header=None)
    
    # Locate the header row containing "Min." or "Avg."
    header_idx = None
    for idx, row in raw_df.iterrows():
        row_str = " ".join(row.astype(str).values)
        if "Min" in row_str and "Max" in row_str and "Avg" in row_str:
            header_idx = idx
            break
            
    if header_idx is not None:
        # Re-read with detected header row
        df = pd.read_csv(SHEET_URL, header=header_idx)
    else:
        df = pd.read_csv(SHEET_URL)
        
    # Drop empty rows & title metadata rows
    df = df.dropna(how='all')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')] # Drop blank columns
    
    return df

try:
    df = load_silk_data()

    # Refresh Button
    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # Identify Key Columns
    cols = df.columns.tolist()
    
    # 3. Market Dropdown Search Filter
    market_col = [c for c in cols if 'Market' in c or 'mkt' in c.lower()]
    market_col_name = market_col[0] if market_col else cols[1] if len(cols) > 1 else cols[0]
    
    # Clean list of unique markets
    markets = df[market_col_name].dropna().astype(str).unique()
    markets = [m for m in markets if m.strip() != "" and "BV" not in m and "Date" not in m]

    selected_market = st.selectbox("🔍 Search / Select Market (ಮಾರುಕಟ್ಟೆ / मार्केट):", ["All Markets"] + list(markets))

    if selected_market != "All Markets":
        filtered_df = df[df[market_col_name].astype(str) == selected_market]
    else:
        filtered_df = df

    # 4. Display Key Summary Metrics (Top Highlights)
    st.subheader("📊 Rate Highlights (₹/Kg)")
    
    # Attempt to calculate Min/Max/Avg summary if columns exist
    min_col = [c for c in cols if 'Min' in c]
    max_col = [c for c in cols if 'Max' in c]
    avg_col = [c for c in cols if 'Avg' in c]

    if min_col and max_col and avg_col:
        c1, c2, c3 = st.columns(3)
        
        # Numeric conversion for clean metrics
        min_val = pd.to_numeric(filtered_df[min_col[0]], errors='coerce').min()
        max_val = pd.to_numeric(filtered_df[max_col[0]], errors='coerce').max()
        avg_val = pd.to_numeric(filtered_df[avg_col[0]], errors='coerce').mean()

        with c1:
            st.metric("Lowest Rate", f"₹{min_val:.0f}" if pd.notnull(min_val) else "N/A")
        with c2:
            st.metric("Highest Rate", f"₹{max_val:.0f}" if pd.notnull(max_val) else "N/A")
        with c3:
            st.metric("Average Rate", f"₹{avg_val:.0f}" if pd.notnull(avg_val) else "N/A")

    st.markdown("---")

    # 5. Full Market Rates Table View
    st.subheader("📋 Market Wise Cocoon Rates")
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption("⚡ Live updates active. Data automatically syncs with Silk Creators sheet.")

except Exception as e:
    st.error("⚠️ Loading data... If table does not appear, refresh the page.")
    # Display fallback raw view if needed
    raw_df = pd.read_csv(SHEET_URL)
    st.dataframe(raw_df, use_container_width=True)
