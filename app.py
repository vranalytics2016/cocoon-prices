import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(
    page_title="Silk Creators - Live Cocoon Rates",
    page_icon="🐛",
    layout="wide"
)

# Header
st.title("🌾 Silk Creators - Live Cocoon Market Dashboard")
st.caption("Real-Time Price Analytics & Day-wise Market Trends")

# Direct CSV URL targeting the 'India Market Rate' tab directly
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysO7bTj3SGMa64vwVcwnojAdxU0J2JkdxvjeKZvuRSU/gviz/tq?tqx=out:csv&sheet=India%20Market%20Rate"

# 2. Data Loader & Cleaning
@st.cache_data(ttl=30)  # Auto-refreshes every 30 seconds
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Clean numeric columns (Remove ₹ and commas)
    numeric_cols = ['Min', 'Max', 'Avg', 'Lots', 'Qty (kg)']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('₹', '').str.replace(',', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convert Date column for chronological charting
    if 'Date' in df.columns:
        df['Date_Parsed'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        df = df.sort_values(by='Date_Parsed', ascending=True)

    return df

try:
    df = load_data()

    # Refresh Button
    c_title, c_btn = st.columns([4, 1])
    with c_btn:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    # Separate Data into BV and CB DataFrames
    bv_mask = df['Variety'].astype(str).str.contains('BV|Bi-Voltine|ದ್ವಿತಳಿ', case=False, na=False)
    cb_mask = df['Variety'].astype(str).str.contains('CB|Cross|ಮಿಶ್ರತಳಿ', case=False, na=False)

    df_bv = df[bv_mask].copy()
    df_cb = df[cb_mask].copy()

    # -------------------------------------------------------------
    # SECTION 1: DAY-WISE PRICE CHANGE CHART
    # -------------------------------------------------------------
    st.markdown("## 📈 Day-wise Price Change Trend")
    
    col_chart_1, col_chart_2 = st.columns(2)
    with col_chart_1:
        # Market Filter for Chart
        available_markets = ["All Markets"] + list(df['Market Name'].dropna().unique())
        selected_market_chart = st.selectbox("🎯 Filter Chart by Market:", available_markets)

    with col_chart_2:
        variety_choice = st.radio("Select Variety for Trend Chart:", ["Both (BV & CB)", "Bi-Voltine (BV) Only", "Cross-Breed (CB) Only"], horizontal=True)

    # Filter chart dataframe
    chart_df = df.copy()
    if selected_market_chart != "All Markets":
        chart_df = chart_df[chart_df['Market Name'] == selected_market_chart]

    if variety_choice == "Bi-Voltine (BV) Only":
        chart_df = chart_df[chart_df['Variety'].astype(str).str.contains('BV|Bi-Voltine|ದ್ವಿತಳಿ', case=False, na=False)]
    elif variety_choice == "Cross-Breed (CB) Only":
        chart_df = chart_df[chart_df['Variety'].astype(str).str.contains('CB|Cross|ಮಿಶ್ರತಳಿ', case=False, na=False)]

    if not chart_df.empty and 'Date_Parsed' in chart_df.columns and 'Avg' in chart_df.columns:
        fig = px.line(
            chart_df,
            x='Date_Parsed',
            y='Avg',
            color='Market Name',
            symbol='Variety',
            title=f"Daily Average Price Trend (₹/kg) - {selected_market_chart}",
            labels={'Date_Parsed': 'Date', 'Avg': 'Average Rate (₹)'},
            markers=True
        )
        fig.update_layout(hovermode="x unified", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient date points available yet to render trend chart.")

    st.markdown("---")

    # -------------------------------------------------------------
    # SECTION 2: SEPARATE TABLES FOR BV AND CB
    # -------------------------------------------------------------
    st.markdown("## 📋 Market Rates by Variety")
    
    # Create Tabs for BV and CB
    tab_bv, tab_cb, tab_all = st.tabs([
        "⚪ Bi-Voltine (BV) – ದ್ವಿತಳಿ", 
        "🟡 Cross-Breed (CB) – ಮಿಶ್ರತಳಿ", 
        "📊 All Combined Data"
    ])

    # Display Columns Setup
    display_cols = ['Date', 'Market Name', 'Lots', 'Qty (kg)', 'Min', 'Max', 'Avg']
    display_cols = [c for c in display_cols if c in df.columns]

    # TAB 1: Bi-Voltine (BV)
    with tab_bv:
        st.subheader("⚪ Bi-Voltine (BV) Cocoon Rates")
        if not df_bv.empty:
            # Summary Metrics for BV
            m1, m2, m3 = st.columns(3)
            m1.metric("BV Lowest Rate", f"₹{df_bv['Min'].min():.0f}")
            m2.metric("BV Highest Rate", f"₹{df_bv['Max'].max():.0f}")
            m3.metric("BV Today's Avg Rate", f"₹{df_bv['Avg'].mean():.0f}")

            st.dataframe(
                df_bv[display_cols].sort_values(by='Date', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No Bi-Voltine (BV) data records found.")

    # TAB 2: Cross-Breed (CB)
    with tab_cb:
        st.subheader("🟡 Cross-Breed (CB) Cocoon Rates")
        if not df_cb.empty:
            # Summary Metrics for CB
            c1, c2, c3 = st.columns(3)
            c1.metric("CB Lowest Rate", f"₹{df_cb['Min'].min():.0f}")
            c2.metric("CB Highest Rate", f"₹{df_cb['Max'].max():.0f}")
            c3.metric("CB Today's Avg Rate", f"₹{df_cb['Avg'].mean():.0f}")

            st.dataframe(
                df_cb[display_cols].sort_values(by='Date', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No Cross-Breed (CB) data records found.")

    # TAB 3: Combined View
    with tab_all:
        st.subheader("📊 All Markets Raw Feed")
        all_cols = ['Date', 'Market Name', 'Variety', 'Lots', 'Qty (kg)', 'Min', 'Max', 'Avg']
        all_cols = [c for c in all_cols if c in df.columns]
        st.dataframe(
            df[all_cols].sort_values(by='Date', ascending=False),
            use_container_width=True,
            hide_index=True
        )

    st.success("✅ **Connected Live to Google Sheet:** 'India Market Rate' tab.")

except Exception as e:
    st.error(f"⚠️ Unable to load Google Sheet data: {e}")
