import streamlit as st
import pandas as pd

# 1. Page Configuration (Mobile Responsive)
st.set_page_config(
    page_title="Live Cocoon Prices",
    page_icon="🐛",
    layout="centered"
)

# 2. Header & Title
st.title("🌾 Daily Live Cocoon Prices")
st.caption("Real-time price updates directly from Indian Mandis & Markets")

# Your exact Google Sheet CSV link
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ysO7bTj3SGMa64vwVcwnojAdxU0J2JkdxvjeKZvuRSU/export?format=csv&gid=0"

# 3. Fetch Live Data Directly from Google Sheets (No delay, 100% Live)
def load_live_data():
    df = pd.read_csv(SHEET_URL)
    df = df.dropna(how='all')  # Drop completely empty rows
    return df

try:
    df = load_live_data()

    # Manual Refresh Button
    if st.button("🔄 Refresh Rates Now"):
        st.rerun()

    st.markdown("---")

    # 4. Filter Options for Farmers
    text_columns = df.select_dtypes(include=['object']).columns.tolist()

    if text_columns:
        primary_col = text_columns[0]  # Usually Market/Mandi/State column
        categories = ["Show All"] + list(df[primary_col].dropna().unique())
        selected_category = st.selectbox(f"🔍 Select Market / Mandi ({primary_col}):", categories)

        if selected_category != "Show All":
            filtered_df = df[df[primary_col] == selected_category]
        else:
            filtered_df = df
    else:
        filtered_df = df

    # 5. Display Count and Main Data Table
    st.write(f"Showing **{len(filtered_df)}** records:")
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.success("✅ **Live Sync Active:** Prices update automatically whenever you edit your Google Sheet.")

except Exception as e:
    st.error("⚠️ Could not load live data. Make sure Google Sheet permissions are set to 'Anyone with the link'.")
