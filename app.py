import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Silk Creators - Live Cocoon Rates",
    page_icon="🐛",
    layout="centered"
)

# Header Title
st.title("🌾 Silk Creators - ರೇಷ್ಮೆ ಮಾರುಕಟ್ಟೆ")
st.caption("Dedicated to Farmers Service | 2026-27 Live Cocoon Market Rates")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysO7bTj3SGMa64vwVcwnojAdxU0J2JkdxvjeKZvuRSU/export?format=csv&gid=0"

# 2. Function to automatically fix duplicate column names
def make_columns_unique(columns):
    seen = {}
    new_cols = []
    for col in columns:
        col_str = str(col).strip()
        if col_str in seen:
            seen[col_str] += 1
            new_cols.append(f"{col_str} ({seen[col_str]})")
        else:
            seen[col_str] = 0
            new_cols.append(col_str)
    return new_cols

# 3. Clean Data Loader
@st.cache_data(ttl=30)  # Auto-refreshes every 30 seconds
def load_clean_data():
    # Read row 4 as header
    df = pd.read_csv(SHEET_URL, header=4)
    
    # Fix duplicate column names
    df.columns = make_columns_unique(df.columns)
    
    # Remove blank/unnamed columns
    df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
    
    # Keep only rows with valid dates (e.g. '21/05/2026')
    date_col = df.columns[0]
    df = df[df[date_col].astype(str).str.contains('/', na=False)]
    
    return df.reset_index(drop=True)

try:
    df = load_clean_data()

    # Manual Refresh Button
    col_title, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # 4. Smart Market Column Finder (Finds text names like Ramnagara, Sidlagatta)
    market_col_name = None
    for col in df.columns:
        if 'market' in col.lower() and 'holiday' not in col.lower() and 'share' not in col.lower():
            # Ensure column contains alphabetic market names, not numbers
            sample_vals = df[col].dropna().astype(str).tolist()
            if any(v.isalpha() for v in sample_vals):
                market_col_name = col
                break

    if not market_col_name:
        market_col_name = df.columns[1] # Default fallback to 2nd column

    # Dropdown Filter
    market_list = ["All Markets"] + [m for m in df[market_col_name].dropna().unique() if str(m).strip() != ""]
    selected_market = st.selectbox("🔍 Select / Filter Market (ಮಾರುಕಟ್ಟೆ):", market_list)

    if selected_market != "All Markets":
        filtered_df = df[df[market_col_name] == selected_market]
    else:
        filtered_df = df

    # 5. Calculate Rate Highlights
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

    # 6. Display Table
    st.subheader("📋 Market Wise Cocoon Rates")
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    st.success("✅ **Live Data Synchronized!**")

except Exception as e:
    st.error(f"⚠️ Error loading sheet data: {e}")
