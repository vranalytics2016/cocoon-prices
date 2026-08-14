import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config (Wide Layout for Side-by-Side View)
st.set_page_config(
    page_title="Silk Creators - Live Cocoon Rates",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Trending Custom CSS for Modern UI
st.markdown("""
    <style>
    /* Background & Font Styling */
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Card Container */
    .metric-card {
        background: #FFFFFF;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
        text-align: center;
        margin-bottom: 12px;
    }
    
    /* Section Headers */
    .section-title {
        font-size: 22px;
        font-weight: 800;
        color: #0F172A;
        padding: 8px 12px;
        background: #FFFFFF;
        border-left: 5px solid #2563EB;
        border-radius: 4px;
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Main Branding Header */
    .brand-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2);
    }
    .brand-header h1 { font-size: 28px; margin: 0; font-weight: 800; }
    .brand-header p { font-size: 14px; margin-top: 5px; opacity: 0.9; }

    /* Custom Scrollbars for Data Tables */
    div[data-testid="stDataFrame"] {
        background: white;
        border-radius: 12px;
        padding: 8px;
        border: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# Branding Banner Header
st.markdown("""
    <div class='brand-header'>
        <h1>🌾 Silk Creators - Live Cocoon Rates</h1>
        <p>Dedicated to Farmers Service | ರೇಷ್ಮೆ ಮಾರುಕಟ್ಟೆ | Real-Time Market Intelligence</p>
    </div>
""", unsafe_allow_html=True)

# Direct CSV URL for 'India Market Rate' tab
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysO7bTj3SGMa64vwVcwnojAdxU0J2JkdxvjeKZvuRSU/gviz/tq?tqx=out:csv&sheet=India%20Market%20Rate"

# 3. Data Loader & Cleaner
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

    # Standardize Variety labels
    if 'Variety' in df.columns:
        df['Variety_Clean'] = df['Variety'].apply(
            lambda x: 'Bi-Voltine (BV)' if any(k in str(x).lower() for k in ['bv', 'bivoltine', 'ದ್ವಿತಳಿ']) 
            else ('Cross-Breed (CB)' if any(k in str(x).lower() for k in ['cb', 'cross', 'ಮಿಶ್ರತಳಿ']) else 'General')
        )

    # Convert Date column cleanly
    if 'Date' in df.columns:
        df['Date_Parsed'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
        df = df.dropna(subset=['Date_Parsed'])
        df = df.sort_values(by='Date_Parsed', ascending=True)

    return df

try:
    df = load_data()

    # Top Controls Bar (Date & Refresh)
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 1])
    with ctrl_col1:
        available_dates = sorted(df['Date'].dropna().unique(), reverse=True)
        selected_date = st.selectbox("📅 Select Date:", available_dates if available_dates else ["Latest"])
    
    with ctrl_col3:
        st.write("") # Spacer
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Filter main DataFrame by date
    if selected_date != "Latest" and 'Date' in df.columns:
        date_df = df[df['Date'] == selected_date].copy()
    else:
        date_df = df.copy()

    # Separate DataFrames for BV and CB
    df_bv = date_df[date_df['Variety_Clean'] == 'Bi-Voltine (BV)'].copy()
    df_cb = date_df[date_df['Variety_Clean'] == 'Cross-Breed (CB)'].copy()

    # Display columns setup
    display_cols = ['Date', 'Market Name', 'Lots', 'Qty (kg)', 'Min', 'Max', 'Avg']
    display_cols = [c for c in display_cols if c in df.columns]

    # =========================================================================
    # SECTION 1: LIVE MARKET TABLES (SIDE-BY-SIDE)
    # =========================================================================
    st.markdown("<div class='section-title'>📋 SECTION 1: LIVE MARKET TABLES (SIDE-BY-SIDE)</div>", unsafe_allow_html=True)

    col_tbl_bv, col_tbl_cb = st.columns(2)

    # --- LEFT SIDE: BI-VOLTINE (BV) TABLE ---
    with col_tbl_bv:
        st.markdown("### ⚪ Bi-Voltine (BV) – ದ್ವಿತಳಿ")
        if not df_bv.empty:
            # Summary Cards for BV
            m1, m2, m3 = st.columns(3)
            m1.metric("Lowest", f"₹{df_bv['Min'].min():.0f}")
            m2.metric("Highest", f"₹{df_bv['Max'].max():.0f}")
            m3.metric("Average", f"₹{df_bv['Avg'].mean():.0f}")

            st.dataframe(
                df_bv[display_cols].sort_values(by='Date', ascending=False),
                use_container_width=True,
                hide_index=True,
                height=350
            )
        else:
            st.info("No Bi-Voltine (BV) entries found for this date.")

    # --- RIGHT SIDE: CROSS-BREED (CB) TABLE ---
    with col_tbl_cb:
        st.markdown("### 🟡 Cross-Breed (CB) – ಮಿಶ್ರತಳಿ")
        if not df_cb.empty:
            # Summary Cards for CB
            c1, c2, c3 = st.columns(3)
            c1.metric("Lowest", f"₹{df_cb['Min'].min():.0f}")
            c2.metric("Highest", f"₹{df_cb['Max'].max():.0f}")
            c3.metric("Average", f"₹{df_cb['Avg'].mean():.0f}")

            st.dataframe(
                df_cb[display_cols].sort_values(by='Date', ascending=False),
                use_container_width=True,
                hide_index=True,
                height=350
            )
        else:
            st.info("No Cross-Breed (CB) entries found for this date.")

    st.markdown("---")

    # =========================================================================
    # SECTION 2: CHARTS & VISUAL ANALYTICS
    # =========================================================================
    st.markdown("<div class='section-title'>📊 SECTION 2: MARKET VISUALIZATIONS & PRICE TRENDS</div>", unsafe_allow_html=True)

    color_map = {
        'Min': '#EF4444',  # Red
        'Max': '#10B981',  # Bright Green
        'Avg': '#F59E0B'   # Amber Yellow
    }

    # SUB-SECTION 2A: SIDE-BY-SIDE GROUPED BAR CHARTS
    st.markdown("#### 📊 Market Rate Comparison (🔴 Min | 🟢 Max | 🟡 Avg)")
    col_bar_bv, col_bar_cb = st.columns(2)

    # LEFT BAR CHART: BV
    with col_bar_bv:
        if not df_bv.empty:
            melted_bv = pd.melt(
                df_bv, id_vars=['Market Name'], value_vars=['Min', 'Max', 'Avg'],
                var_name='Rate_Type', value_name='Price'
            ).dropna(subset=['Price'])

            fig_bv = px.bar(
                melted_bv, x='Market Name', y='Price', color='Rate_Type',
                barmode='group', text_auto='.0f',
                title=f"⚪ BV Rates Comparison: {selected_date}",
                labels={'Market Name': 'Mandi', 'Price': 'Rate (₹/kg)', 'Rate_Type': 'Rate'},
                color_discrete_map=color_map
            )
            fig_bv.update_traces(textposition='outside')
            fig_bv.update_layout(
                xaxis_title="Mandi", yaxis_title="Rate (₹/kg)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=420, margin=dict(l=10, r=10, t=50, b=10)
            )
            st.plotly_chart(fig_bv, use_container_width=True)
        else:
            st.info("No BV chart data available.")

    # RIGHT BAR CHART: CB
    with col_bar_cb:
        if not df_cb.empty:
            melted_cb = pd.melt(
                df_cb, id_vars=['Market Name'], value_vars=['Min', 'Max', 'Avg'],
                var_name='Rate_Type', value_name='Price'
            ).dropna(subset=['Price'])

            fig_cb = px.bar(
                melted_cb, x='Market Name', y='Price', color='Rate_Type',
                barmode='group', text_auto='.0f',
                title=f"🟡 CB Rates Comparison: {selected_date}",
                labels={'Market Name': 'Mandi', 'Price': 'Rate (₹/kg)', 'Rate_Type': 'Rate'},
                color_discrete_map=color_map
            )
            fig_cb.update_traces(textposition='outside')
            fig_cb.update_layout(
                xaxis_title="Mandi", yaxis_title="Rate (₹/kg)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=420, margin=dict(l=10, r=10, t=50, b=10)
            )
            st.plotly_chart(fig_cb, use_container_width=True)
        else:
            st.info("No CB chart data available.")

    st.markdown("---")

    # SUB-SECTION 2B: DAY-WISE PRICE TREND TRAJECTORY
    st.markdown("#### 📈 Day-wise Price Change Trajectory")
    
    available_markets = ["All Mandis (Overall Trend)"] + sorted([str(m) for m in df['Market Name'].dropna().unique() if str(m).strip() != ''])
    selected_market = st.selectbox("🎯 Select Market to View Day-wise Price Trajectory:", available_markets)

    if selected_market != "All Mandis (Overall Trend)":
        trend_df = df[df['Market Name'] == selected_market].copy()
    else:
        trend_df = df.copy()

    daily_trend = trend_df.groupby(['Date_Parsed', 'Variety_Clean'])['Avg'].mean().reset_index()
    daily_trend['Date_Formatted'] = daily_trend['Date_Parsed'].astype(str)

    if not daily_trend.empty:
        color_map_line = {
            'Bi-Voltine (BV)': '#1E3A8A',    # Navy Blue
            'Cross-Breed (CB)': '#D97706',   # Amber Gold
            'General': '#6B7280'
        }

        fig_line = px.line(
            daily_trend, x='Date_Formatted', y='Avg', color='Variety_Clean',
            title=f"Average Daily Rate Trend (₹/kg) — {selected_market}",
            markers=True, color_discrete_map=color_map_line,
            labels={'Date_Formatted': 'Date', 'Avg': 'Avg Rate (₹/kg)', 'Variety_Clean': 'Variety'}
        )

        fig_line.update_xaxes(type='category')
        fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
        fig_line.update_layout(
            xaxis_title="Date", yaxis_title="Average Rate (₹/kg)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=380, margin=dict(l=10, r=10, t=40, b=10)
        )

        st.plotly_chart(fig_line, use_container_width=True)

    # Footer
    st.markdown("---")
    st.caption("✅ **Live Sync Active:** Connected directly to Google Sheets 'India Market Rate' tab.")

except Exception as e:
    st.error(f"⚠️ Error loading sheet data: {e}")
