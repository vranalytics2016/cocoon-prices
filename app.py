import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# 1. Page Configuration
st.set_page_config(
    page_title="Silk Creators - Live Cocoon Rates",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Modern UI CSS Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    .brand-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        color: white;
        padding: 22px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2);
    }
    .brand-header h1 { font-size: 26px; margin: 0; font-weight: 800; }
    .brand-header p { font-size: 14px; margin-top: 6px; opacity: 0.95; }

    .section-title {
        font-size: 20px;
        font-weight: 800;
        color: #0F172A;
        padding: 8px 12px;
        background: #FFFFFF;
        border-left: 5px solid #2563EB;
        border-radius: 4px;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .calc-card {
        background: #FFFFFF;
        padding: 18px;
        border-radius: 12px;
        border: 2px solid #2563EB;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    .top-mandi-card {
        background: white;
        padding: 12px;
        border-radius: 10px;
        border-left: 4px solid #10B981;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 8px;
    }

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
        <h1>🌾 Silk Creators - ರೇಷ್ಮೆ ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು</h1>
        <p>Dedicated to Farmers Service | Live Cocoon Market Rates across India</p>
    </div>
""", unsafe_allow_html=True)

# Direct CSV URL for 'India Market Rate' tab
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysO7bTj3SGMa64vwVcwnojAdxU0J2JkdxvjeKZvuRSU/gviz/tq?tqx=out:csv&sheet=India%20Market%20Rate"

# 3. Data Loader
@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = [str(c).strip() for c in df.columns]
    
    numeric_cols = ['Min', 'Max', 'Avg', 'Lots', 'Qty (kg)']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('₹', '').str.replace(',', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'Variety' in df.columns:
        df['Variety_Clean'] = df['Variety'].apply(
            lambda x: 'Bi-Voltine (BV)' if any(k in str(x).lower() for k in ['bv', 'bivoltine', 'ದ್ವಿತಳಿ']) 
            else ('Cross-Breed (CB)' if any(k in str(x).lower() for k in ['cb', 'cross', 'ಮಿಶ್ರತಳಿ']) else 'General')
        )

    if 'Date' in df.columns:
        df['Date_Parsed'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
        df = df.dropna(subset=['Date_Parsed'])
        df = df.sort_values(by='Date_Parsed', ascending=True)

    return df

try:
    df = load_data()

    # Top Control Bar
    ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])
    with ctrl1:
        available_dates = sorted(df['Date'].dropna().unique(), reverse=True)
        selected_date = st.selectbox("📅 Select Date / ದಿನಾಂಕ:", available_dates if available_dates else ["Latest"])
    
    with ctrl2:
        st.write("") # Spacer
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Filter Data by Selected Date
    if selected_date != "Latest" and 'Date' in df.columns:
        date_df = df[df['Date'] == selected_date].copy()
    else:
        date_df = df.copy()

    df_bv = date_df[date_df['Variety_Clean'] == 'Bi-Voltine (BV)'].copy()
    df_cb = date_df[date_df['Variety_Clean'] == 'Cross-Breed (CB)'].copy()

    # WhatsApp Sharing
    with ctrl3:
        st.write("") # Spacer
        bv_avg_str = f"₹{df_bv['Avg'].mean():.0f}" if not df_bv.empty else "N/A"
        cb_avg_str = f"₹{df_cb['Avg'].mean():.0f}" if not df_cb.empty else "N/A"
        
        wa_text = f"🌾 *Silk Creators - Live Cocoon Rates ({selected_date})*\n\n⚪ *BV Avg Rate:* {bv_avg_str}/kg\n🟡 *CB Avg Rate:* {cb_avg_str}/kg\n\nCheck full mandi rates online:\nhttps://cocoon-prices.streamlit.app"
        encoded_wa_text = urllib.parse.quote(wa_text)
        wa_link = f"https://api.whatsapp.com/send?text={encoded_wa_text}"
        
        st.markdown(f"""
            <a href="{wa_link}" target="_blank" style="text-decoration:none;">
                <button style="width:100%; background-color:#25D366; color:white; border:none; padding:9px; border-radius:8px; font-weight:bold; cursor:pointer;">
                    📲 Share WhatsApp
                </button>
            </a>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # NEW ENHANCEMENT 1: FARMER COCOON INCOME ESTIMATOR / CALCULATOR WIDGET
    # -------------------------------------------------------------------------
    with st.expander("🧮 **Farmer Revenue Estimator / ಆದಾಯ ಲೆಕ್ಕಾಚಾರ (Click to Calculate Your Payout)**", expanded=False):
        st.markdown("<div class='calc-card'>", unsafe_allow_html=True)
        st.subheader("💰 Calculate Your Estimated Harvest Payout")
        
        c_calc1, c_calc2, c_calc3 = st.columns(3)
        with c_calc1:
            farmer_qty = st.number_input("Enter Harvest Weight (Kg):", min_value=10, max_value=5000, value=100, step=10)
        with c_calc2:
            calc_variety = st.selectbox("Select Variety:", ["Bi-Voltine (BV)", "Cross-Breed (CB)"])
        with c_calc3:
            all_mandis = sorted([str(m) for m in date_df['Market Name'].dropna().unique() if str(m).strip() != ''])
            calc_mandi = st.selectbox("Select Target Mandi:", all_mandis if all_mandis else ["Ramanagara"])

        # Calculate estimated revenue
        calc_match = date_df[(date_df['Variety_Clean'] == calc_variety) & (date_df['Market Name'] == calc_mandi)]
        if not calc_match.empty and 'Avg' in calc_match.columns:
            m_avg = calc_match['Avg'].values[0]
            m_max = calc_match['Max'].values[0]
            
            est_avg_payout = farmer_qty * m_avg
            est_max_payout = farmer_qty * m_max
            
            st.success(f"📊 Estimated Payout at **{calc_mandi}** for **{farmer_qty} Kg** of **{calc_variety}**:")
            res1, res2, res3 = st.columns(3)
            res1.metric("Expected Avg Income", f"₹{est_avg_payout:,.0f}", f"Rate: ₹{m_avg:.0f}/kg")
            res2.metric("Potential Max Income", f"₹{est_max_payout:,.0f}", f"Rate: ₹{m_max:.0f}/kg")
            res3.info(f"💡 Target Mandi: **{calc_mandi}**")
        else:
            st.info("No rate data available for this selected combination today.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 🏆 HIGHEST PAYING MANDIS
    st.markdown("---")
    st.markdown("### 🏆 Top Highest Paying Mandis Today")
    top_col1, top_col2 = st.columns(2)

    with top_col1:
        st.markdown("**⚪ Top 3 BV Markets (Highest Rates)**")
        if not df_bv.empty:
            top_bv = df_bv.sort_values(by='Max', ascending=False).head(3)
            for idx, row in top_bv.iterrows():
                st.markdown(f"<div class='top-mandi-card'>🥇 <b>{row['Market Name']}</b> — Max: <b>₹{row['Max']:.0f}/kg</b> (Avg: ₹{row['Avg']:.0f})</div>", unsafe_allow_html=True)
        else:
            st.caption("No BV data for this date.")

    with top_col2:
        st.markdown("**🟡 Top 3 CB Markets (Highest Rates)**")
        if not df_cb.empty:
            top_cb = df_cb.sort_values(by='Max', ascending=False).head(3)
            for idx, row in top_cb.iterrows():
                st.markdown(f"<div class='top-mandi-card'>🥇 <b>{row['Market Name']}</b> — Max: <b>₹{row['Max']:.0f}/kg</b> (Avg: ₹{row['Avg']:.0f})</div>", unsafe_allow_html=True)
        else:
            st.caption("No CB data for this date.")

    # -------------------------------------------------------------------------
    # NEW ENHANCEMENT 2: INSTANT MANDI SEARCH BAR
    # -------------------------------------------------------------------------
    st.markdown("---")
    search_mandi = st.text_input("🔍 Search Mandi / Market Name (e.g. Ramanagara, Sidlaghatta, Kolar, Gokak):", "").strip()

    if search_mandi:
        df_bv = df_bv[df_bv['Market Name'].str.contains(search_mandi, case=False, na=False)]
        df_cb = df_cb[df_cb['Market Name'].str.contains(search_mandi, case=False, na=False)]

    # =========================================================================
    # SECTION 1: LIVE MARKET TABLES (SIDE-BY-SIDE)
    # =========================================================================
    st.markdown("<div class='section-title'>📋 SECTION 1: LIVE MARKET TABLES (SIDE-BY-SIDE)</div>", unsafe_allow_html=True)

    col_tbl_bv, col_tbl_cb = st.columns(2)
    display_cols = ['Date', 'Market Name', 'Lots', 'Qty (kg)', 'Min', 'Max', 'Avg']
    display_cols = [c for c in display_cols if c in df.columns]

    # LEFT: BV TABLE
    with col_tbl_bv:
        st.markdown("### ⚪ Bi-Voltine (BV) – ದ್ವಿತಳಿ")
        if not df_bv.empty:
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
            st.info("No Bi-Voltine (BV) entries found.")

    # RIGHT: CB TABLE
    with col_tbl_cb:
        st.markdown("### 🟡 Cross-Breed (CB) – ಮಿಶ್ರತಳಿ")
        if not df_cb.empty:
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
            st.info("No Cross-Breed (CB) entries found.")

    # CSV DOWNLOAD
    st.write("")
    csv_data = date_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Today's Rates Report (CSV / Excel)",
        data=csv_data,
        file_name=f"Silk_Cocoon_Rates_{selected_date}.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.markdown("---")

    # =========================================================================
    # SECTION 2: CHARTS & VISUAL ANALYTICS
    # =========================================================================
    st.markdown("<div class='section-title'>📊 SECTION 2: MARKET VISUALIZATIONS & PRICE TRENDS</div>", unsafe_allow_html=True)

    color_map = {'Min': '#EF4444', 'Max': '#10B981', 'Avg': '#F59E0B'}

    # SUB-SECTION 2A: SIDE-BY-SIDE BAR CHARTS
    st.markdown("#### 📊 Market Rate Comparison (🔴 Min | 🟢 Max | 🟡 Avg)")
    col_bar_bv, col_bar_cb = st.columns(2)

    with col_bar_bv:
        if not df_bv.empty:
            melted_bv = pd.melt(df_bv, id_vars=['Market Name'], value_vars=['Min', 'Max', 'Avg'], var_name='Rate_Type', value_name='Price').dropna(subset=['Price'])
            fig_bv = px.bar(melted_bv, x='Market Name', y='Price', color='Rate_Type', barmode='group', text_auto='.0f', title=f"⚪ BV Rates: {selected_date}", labels={'Market Name': 'Mandi', 'Price': 'Rate (₹/kg)'}, color_discrete_map=color_map)
            fig_bv.update_traces(textposition='outside')
            fig_bv.update_layout(xaxis_title="Mandi", yaxis_title="Rate (₹/kg)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=420, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig_bv, use_container_width=True)

    with col_bar_cb:
        if not df_cb.empty:
            melted_cb = pd.melt(df_cb, id_vars=['Market Name'], value_vars=['Min', 'Max', 'Avg'], var_name='Rate_Type', value_name='Price').dropna(subset=['Price'])
            fig_cb = px.bar(melted_cb, x='Market Name', y='Price', color='Rate_Type', barmode='group', text_auto='.0f', title=f"🟡 CB Rates: {selected_date}", labels={'Market Name': 'Mandi', 'Price': 'Rate (₹/kg)'}, color_discrete_map=color_map)
            fig_cb.update_traces(textposition='outside')
            fig_cb.update_layout(xaxis_title="Mandi", yaxis_title="Rate (₹/kg)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=420, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig_cb, use_container_width=True)

    st.markdown("---")

    # SUB-SECTION 2B: DAY-WISE PRICE TREND TRAJECTORY
    st.markdown("#### 📈 Day-wise Price Trajectory Trend")
    available_markets = ["All Mandis (Overall Trend)"] + sorted([str(m) for m in df['Market Name'].dropna().unique() if str(m).strip() != ''])
    selected_market = st.selectbox("🎯 Select Market for Day-wise Price Trajectory:", available_markets)

    if selected_market != "All Mandis (Overall Trend)":
        trend_df = df[df['Market Name'] == selected_market].copy()
    else:
        trend_df = df.copy()

    daily_trend = trend_df.groupby(['Date_Parsed', 'Variety_Clean'])['Avg'].mean().reset_index()
    daily_trend['Date_Formatted'] = daily_trend['Date_Parsed'].astype(str)

    if not daily_trend.empty:
        color_map_line = {'Bi-Voltine (BV)': '#1E3A8A', 'Cross-Breed (CB)': '#D97706', 'General': '#6B7280'}
        fig_line = px.line(daily_trend, x='Date_Formatted', y='Avg', color='Variety_Clean', title=f"Average Daily Rate Trend (₹/kg) — {selected_market}", markers=True, color_discrete_map=color_map_line)
        fig_line.update_xaxes(type='category')
        fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
        fig_line.update_layout(xaxis_title="Date", yaxis_title="Average Rate (₹/kg)", hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=380, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")
    st.caption("✅ **Live Sync Active:** Connected to Google Sheets 'India Market Rate' tab.")

except Exception as e:
    st.error(f"⚠️ Error loading sheet data: {e}")
