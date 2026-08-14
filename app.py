import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Silk Creators - Live Cocoon Rates",
    page_icon="🐛",
    layout="wide"
)

# Custom Header Styling
st.markdown("""
    <style>
    .main-title { font-size: 26px; font-weight: bold; color: #1E3A8A; }
    .sub-title { font-size: 14px; color: #6B7280; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🌾 Silk Creators - Live Market Analytics</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Dedicated to Farmers Service | Live Cocoon Market Rates</div>", unsafe_allow_html=True)

# Direct CSV URL for 'India Market Rate' tab
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysO7bTj3SGMa64vwVcwnojAdxU0J2JkdxvjeKZvuRSU/gviz/tq?tqx=out:csv&sheet=India%20Market%20Rate"

# 2. Data Loader & Cleaner
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

    # Controls Bar
    c_title, c_btn = st.columns([4, 1])
    with c_btn:
        if st.button("🔄 Refresh Rates"):
            st.cache_data.clear()
            st.rerun()

    # Separate DataFrames
    df_bv = df[df['Variety_Clean'] == 'Bi-Voltine (BV)'].copy()
    df_cb = df[df['Variety_Clean'] == 'Cross-Breed (CB)'].copy()

    # Main Navigation Tabs
    tab_bar, tab_line, tab_bv, tab_cb = st.tabs([
        "📊 Market Rates Bar Chart (Min/Max/Avg)", 
        "📈 Day-wise Price Trend", 
        "⚪ Bi-Voltine (BV) Table", 
        "🟡 Cross-Breed (CB) Table"
    ])

    # -------------------------------------------------------------
    # TAB 1: INTERACTIVE GROUPED BAR CHART (MIN, MAX, AVG)
    # -------------------------------------------------------------
    with tab_bar:
        st.markdown("### 📊 Market-Wise Min, Max & Avg Comparison (₹/kg)")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            # Variety Selector for Bar Chart
            bar_variety = st.radio("Select Cocoon Variety:", ["Bi-Voltine (BV)", "Cross-Breed (CB)"], horizontal=True)
        
        with col_f2:
            # Date Selector
            available_dates = sorted(df['Date'].dropna().unique(), reverse=True)
            selected_date = st.selectbox("📅 Select Date:", available_dates if available_dates else ["Latest"])

        # Filter Data
        bar_df = df[df['Variety_Clean'] == bar_variety].copy()
        if selected_date != "Latest" and 'Date' in bar_df.columns:
            bar_df = bar_df[bar_df['Date'] == selected_date]

        if not bar_df.empty:
            # Reshape data into long format for Min, Max, Avg grouped bars
            melted_df = pd.melt(
                bar_df,
                id_vars=['Market Name'],
                value_vars=['Min', 'Max', 'Avg'],
                var_name='Rate_Type',
                value_name='Price'
            ).dropna(subset=['Price'])

            # Custom Color Map: Red for Min, Green for Max, Amber Yellow for Avg
            color_map = {
                'Min': '#EF4444',  # Red
                'Max': '#10B981',  # Bright Green
                'Avg': '#F59E0B'   # Amber Yellow
            }

            fig_bar = px.bar(
                melted_df,
                x='Market Name',
                y='Price',
                color='Rate_Type',
                barmode='group',
                text_auto='.0f', # Displays values on top of bars
                title=f"{bar_variety} Cocoon Rates by Market (🔴 Min | 🟢 Max | 🟡 Avg)",
                labels={'Market Name': 'Mandi / Market', 'Price': 'Price (₹/kg)', 'Rate_Type': 'Rate Type'},
                color_discrete_map=color_map
            )

            fig_bar.update_traces(textposition='outside')
            fig_bar.update_layout(
                xaxis_title="Market / Mandi",
                yaxis_title="Rate (₹/kg)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=480,
                margin=dict(l=20, r=20, t=60, b=20)
            )

            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("No price data available for the selected variety/date.")

    # -------------------------------------------------------------
    # TAB 2: DAY-WISE PRICE TREND CHART
    # -------------------------------------------------------------
    with tab_line:
        st.markdown("### 📈 Day-wise Price Change Trend")
        
        available_markets = ["All Mandis (Overall Trend)"] + sorted([str(m) for m in df['Market Name'].dropna().unique() if str(m).strip() != ''])
        selected_market = st.selectbox("🎯 Filter Trend Chart by Market:", available_markets)

        if selected_market != "All Mandis (Overall Trend)":
            filtered_chart_df = df[df['Market Name'] == selected_market]
        else:
            filtered_chart_df = df.copy()

        daily_trend = filtered_chart_df.groupby(['Date_Parsed', 'Variety_Clean'])['Avg'].mean().reset_index()
        daily_trend['Date_Formatted'] = daily_trend['Date_Parsed'].astype(str)

        if not daily_trend.empty:
            color_map_line = {
                'Bi-Voltine (BV)': '#1E3A8A',    # Deep Navy Blue
                'Cross-Breed (CB)': '#D97706',   # Amber Gold
                'General': '#6B7280'             # Gray
            }

            fig_line = px.line(
                daily_trend,
                x='Date_Formatted',
                y='Avg',
                color='Variety_Clean',
                title=f"Daily Average Price Trend (₹/kg) — {selected_market}",
                markers=True,
                color_discrete_map=color_map_line,
                labels={'Date_Formatted': 'Date', 'Avg': 'Avg Rate (₹/kg)', 'Variety_Clean': 'Variety'}
            )

            fig_line.update_xaxes(type='category')
            fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
            fig_line.update_layout(
                xaxis_title="Date",
                yaxis_title="Average Price (₹/kg)",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=400
            )

            st.plotly_chart(fig_line, use_container_width=True)

    # -------------------------------------------------------------
    # TAB 3: BI-VOLTINE (BV) TABLE
    # -------------------------------------------------------------
    with tab_bv:
        st.subheader("⚪ Bi-Voltine (BV) Cocoon Rates")
        display_cols = ['Date', 'Market Name', 'Lots', 'Qty (kg)', 'Min', 'Max', 'Avg']
        display_cols = [c for c in display_cols if c in df.columns]

        if not df_bv.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("BV Lowest Rate", f"₹{df_bv['Min'].min():.0f}")
            m2.metric("BV Highest Rate", f"₹{df_bv['Max'].max():.0f}")
            m3.metric("BV Avg Rate", f"₹{df_bv['Avg'].mean():.0f}")

            st.dataframe(
                df_bv[display_cols].sort_values(by='Date', ascending=False),
                use_container_width=True,
                hide_index=True
            )

    # -------------------------------------------------------------
    # TAB 4: CROSS-BREED (CB) TABLE
    # -------------------------------------------------------------
    with tab_cb:
        st.subheader("🟡 Cross-Breed (CB) Cocoon Rates")
        if not df_cb.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("CB Lowest Rate", f"₹{df_cb['Min'].min():.0f}")
            c2.metric("CB Highest Rate", f"₹{df_cb['Max'].max():.0f}")
            c3.metric("CB Avg Rate", f"₹{df_cb['Avg'].mean():.0f}")

            st.dataframe(
                df_cb[display_cols].sort_values(by='Date', ascending=False),
                use_container_width=True,
                hide_index=True
            )

    st.success("✅ **Live Data Connected:** 'India Market Rate' Sheet")

except Exception as e:
    st.error(f"⚠️ Error loading sheet data: {e}")
