import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Silk Creators - Live Cocoon Rates",
    page_icon="🐛",
    layout="wide"
)

# Title Header
st.markdown("<h2 style='color: #1E3A8A;'>🌾 Silk Creators - Live Market Analytics</h2>", unsafe_allow_html=True)
st.caption("Dedicated to Farmers Service | Live Cocoon Market Rates Side-by-Side Comparison")

# Direct CSV URL for 'India Market Rate' tab
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysO7bTj3SGMa64vwVcwnojAdxU0J2JkdxvjeKZvuRSU/gviz/tq?tqx=out:csv&sheet=India%20Market%20Rate"

# 2. Data Loader & Cleaner
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

    # Convert Date column cleanly
    if 'Date' in df.columns:
        df['Date_Parsed'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
        df = df.dropna(subset=['Date_Parsed'])
        df = df.sort_values(by='Date_Parsed', ascending=True)

    return df

try:
    df = load_data()

    # Refresh Control
    c_title, c_btn = st.columns([4, 1])
    with c_btn:
        if st.button("🔄 Refresh Rates"):
            st.cache_data.clear()
            st.rerun()

    # Data Subset DataFrames
    df_bv = df[df['Variety_Clean'] == 'Bi-Voltine (BV)'].copy()
    df_cb = df[df['Variety_Clean'] == 'Cross-Breed (CB)'].copy()

    # Main Navigation Tabs
    tab_bar, tab_line, tab_bv, tab_cb = st.tabs([
        "📊 Side-by-Side Bar Charts (BV vs CB)", 
        "📈 Day-wise Price Trend", 
        "⚪ Bi-Voltine (BV) Table", 
        "🟡 Cross-Breed (CB) Table"
    ])

    # Color Scheme (Matching your Excel image)
    color_map = {
        'Min': '#EF4444',  # Red
        'Max': '#10B981',  # Bright Green
        'Avg': '#F59E0B'   # Amber Yellow
    }

    # -------------------------------------------------------------
    # TAB 1: SIDE-BY-SIDE BAR CHARTS (BV vs CB)
    # -------------------------------------------------------------
    with tab_bar:
        st.markdown("### 📊 Market Rates Side-by-Side Comparison (₹/kg)")
        
        # Shared Date Selector
        available_dates = sorted(df['Date'].dropna().unique(), reverse=True)
        selected_date = st.selectbox("📅 Select Date for Charts:", available_dates if available_dates else ["Latest"])

        # Filter Data by Date
        date_filtered_df = df.copy()
        if selected_date != "Latest" and 'Date' in date_filtered_df.columns:
            date_filtered_df = date_filtered_df[date_filtered_df['Date'] == selected_date]

        # CREATE TWO SIDE-BY-SIDE COLUMNS
        col_bv, col_cb = st.columns(2)

        # LEFT COLUMN: BI-VOLTINE (BV) CHART
        with col_bv:
            st.subheader("⚪ Bi-Voltine (BV) Rates")
            bv_chart_df = date_filtered_df[date_filtered_df['Variety_Clean'] == 'Bi-Voltine (BV)'].copy()

            if not bv_chart_df.empty:
                melted_bv = pd.melt(
                    bv_chart_df,
                    id_vars=['Market Name'],
                    value_vars=['Min', 'Max', 'Avg'],
                    var_name='Rate_Type',
                    value_name='Price'
                ).dropna(subset=['Price'])

                fig_bv = px.bar(
                    melted_bv,
                    x='Market Name',
                    y='Price',
                    color='Rate_Type',
                    barmode='group',
                    text_auto='.0f', # Numbers on top of bars
                    title=f"⚪ BV Rates: {selected_date} (🔴 Min | 🟢 Max | 🟡 Avg)",
                    labels={'Market Name': 'Mandi', 'Price': 'Price (₹/kg)', 'Rate_Type': 'Rate'},
                    color_discrete_map=color_map
                )
                fig_bv.update_traces(textposition='outside')
                fig_bv.update_layout(
                    xaxis_title="Market / Mandi",
                    yaxis_title="Rate (₹/kg)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    height=450,
                    margin=dict(l=10, r=10, t=50, b=10)
                )
                st.plotly_chart(fig_bv, use_container_width=True)
            else:
                st.info("No Bi-Voltine (BV) entries available for this date.")

        # RIGHT COLUMN: CROSS-BREED (CB) CHART
        with col_cb:
            st.subheader("🟡 Cross-Breed (CB) Rates")
            cb_chart_df = date_filtered_df[date_filtered_df['Variety_Clean'] == 'Cross-Breed (CB)'].copy()

            if not cb_chart_df.empty:
                melted_cb = pd.melt(
                    cb_chart_df,
                    id_vars=['Market Name'],
                    value_vars=['Min', 'Max', 'Avg'],
                    var_name='Rate_Type',
                    value_name='Price'
                ).dropna(subset=['Price'])

                fig_cb = px.bar(
                    melted_cb,
                    x='Market Name',
                    y='Price',
                    color='Rate_Type',
                    barmode='group',
                    text_auto='.0f', # Numbers on top of bars
                    title=f"🟡 CB Rates: {selected_date} (🔴 Min | 🟢 Max | 🟡 Avg)",
                    labels={'Market Name': 'Mandi', 'Price': 'Price (₹/kg)', 'Rate_Type': 'Rate'},
                    color_discrete_map=color_map
                )
                fig_cb.update_traces(textposition='outside')
                fig_cb.update_layout(
                    xaxis_title="Market / Mandi",
                    yaxis_title="Rate (₹/kg)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    height=450,
                    margin=dict(l=10, r=10, t=50, b=10)
                )
                st.plotly_chart(fig_cb, use_container_width=True)
            else:
                st.info("No Cross-Breed (CB) entries available for this date.")

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
                'General': '#6B7280'
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
