import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(
    page_title="Silk Creators - Live Cocoon Rates",
    page_icon="🐛",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size: 26px; font-weight: bold; color: #1E3A8A; }
    .sub-title { font-size: 14px; color: #6B7280; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🌾 Silk Creators - Live Market Analytics</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Real-Time Price Tracking & Day-Wise Market Trends</div>", unsafe_allow_html=True)

# Direct CSV URL for 'India Market Rate' tab
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysO7bTj3SGMa64vwVcwnojAdxU0J2JkdxvjeKZvuRSU/gviz/tq?tqx=out:csv&sheet=India%20Market%20Rate"

# 2. Data Loader & Cleaning
@st.cache_data(ttl=30)
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

    # Convert Date column strictly to Date objects (removes 00:00 time noise)
    if 'Date' in df.columns:
        df['Date_Parsed'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
        df = df.dropna(subset=['Date_Parsed'])
        df = df.sort_values(by='Date_Parsed', ascending=True)

    return df

try:
    df = load_data()

    # Top Controls Bar
    col_a, col_b = st.columns([4, 1])
    with col_b:
        if st.button("🔄 Refresh Rates"):
            st.cache_data.clear()
            st.rerun()

    # Separate DataFrames
    df_bv = df[df['Variety_Clean'] == 'Bi-Voltine (BV)'].copy()
    df_cb = df[df['Variety_Clean'] == 'Cross-Breed (CB)'].copy()

    # -------------------------------------------------------------
    # SECTION 1: CLEAN DAY-WISE PRICE TREND CHART
    # -------------------------------------------------------------
    st.markdown("### 📈 Day-wise Price Change Trend")
    
    # Market Selector
    available_markets = ["All Mandis (Overall Trend)"] + sorted([str(m) for m in df['Market Name'].dropna().unique() if str(m).strip() != ''])
    selected_market = st.selectbox("🎯 Filter Trend Chart by Market:", available_markets)

    # Filter data for chart
    if selected_market != "All Mandis (Overall Trend)":
        filtered_chart_df = df[df['Market Name'] == selected_market]
    else:
        filtered_chart_df = df.copy()

    # Group by Date and Variety to get clean 1-point per day averages
    daily_trend = filtered_chart_df.groupby(['Date_Parsed', 'Variety_Clean'])['Avg'].mean().reset_index()
    daily_trend['Date_Formatted'] = daily_trend['Date_Parsed'].astype(str)

    if not daily_trend.empty:
        # Custom color map for clean distinction
        color_map = {
            'Bi-Voltine (BV)': '#1E3A8A',    # Deep Navy Blue
            'Cross-Breed (CB)': '#D97706',   # Amber Gold
            'General': '#6B7280'             # Gray
        }

        fig = px.line(
            daily_trend,
            x='Date_Formatted',
            y='Avg',
            color='Variety_Clean',
            title=f"Average Price Trend (₹/kg) — {selected_market}",
            markers=True,
            color_discrete_map=color_map,
            labels={'Date_Formatted': 'Date', 'Avg': 'Avg Rate (₹/kg)', 'Variety_Clean': 'Variety'}
        )

        # Styling adjustments for clean presentation
        fig.update_xaxes(type='category')  # Ensures no 00:00 time ticks!
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Average Price (₹/kg)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20),
            height=380
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sufficient date entries available to plot the trend graph.")

    st.markdown("---")

    # -------------------------------------------------------------
    # SECTION 2: SEPARATE TABLES FOR BV AND CB
    # -------------------------------------------------------------
    st.markdown("### 📋 Market Rates by Variety")
    
    tab_bv, tab_cb, tab_all = st.tabs([
        "⚪ Bi-Voltine (BV) – ದ್ವಿತಳಿ", 
        "🟡 Cross-Breed (CB) – ಮಿಶ್ರತಳಿ", 
        "📊 All Records Feed"
    ])

    display_cols = ['Date', 'Market Name', 'Lots', 'Qty (kg)', 'Min', 'Max', 'Avg']
    display_cols = [c for c in display_cols if c in df.columns]

    # TAB 1: BV
    with tab_bv:
        st.subheader("⚪ Bi-Voltine (BV) Cocoon Rates")
        if not df_bv.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("Lowest Rate", f"₹{df_bv['Min'].min():.0f}")
            m2.metric("Highest Rate", f"₹{df_bv['Max'].max():.0f}")
            m3.metric("Average Rate", f"₹{df_bv['Avg'].mean():.0f}")

            st.dataframe(
                df_bv[display_cols].sort_values(by='Date', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No Bi-Voltine (BV) entries found.")

    # TAB 2: CB
    with tab_cb:
        st.subheader("🟡 Cross-Breed (CB) Cocoon Rates")
        if not df_cb.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Lowest Rate", f"₹{df_cb['Min'].min():.0f}")
            c2.metric("Highest Rate", f"₹{df_cb['Max'].max():.0f}")
            c3.metric("Average Rate", f"₹{df_cb['Avg'].mean():.0f}")

            st.dataframe(
                df_cb[display_cols].sort_values(by='Date', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No Cross-Breed (CB) entries found.")

    # TAB 3: Combined
    with tab_all:
        st.subheader("📊 Combined Live Feed")
        raw_cols = ['Date', 'Market Name', 'Variety', 'Lots', 'Qty (kg)', 'Min', 'Max', 'Avg']
        raw_cols = [c for c in raw_cols if c in df.columns]
        st.dataframe(
            df[raw_cols].sort_values(by='Date', ascending=False),
            use_container_width=True,
            hide_index=True
        )

    st.success("✅ **Live Data Connected:** 'India Market Rate' Sheet")

except Exception as e:
    st.error(f"⚠️ Error loading sheet data: {e}")
