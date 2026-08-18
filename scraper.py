import os
import re
import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd

CSV_FILE = "cocoon_rates.csv"
SUMMARY_FILE = "summary.json"

CATEGORY_URLS = [
    "https://kannadatopnews.com/category/announcement/sericulture/",
    "https://kannadatopnews.com/category/announcement/sericulture/silk-cocoon/"
]

FEED_URLS = [
    "https://kannadatopnews.com/category/announcement/sericulture/feed/",
    "https://kannadatopnews.com/category/announcement/sericulture/silk-cocoon/feed/"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 🔄 AUTO-RETRY NETWORK RESILIENCE
def fetch_url_with_retry(url, retries=3, delay=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            return urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print(f"Failed to fetch {url} after {retries} attempts: {e}")
                return ""

def extract_date(text):
    m1 = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})', text)
    if m1:
        day, month_str, year = m1.groups()
        try:
            dt = datetime.strptime(f"{day} {month_str} {year}", "%d %B %Y")
            return dt.strftime("%d/%m/%Y")
        except Exception:
            pass
    
    m2 = re.search(r'(\d{1,2}[\/\.-]\d{1,2}[\/\.-]20\d{2})', text)
    if m2:
        return m2.group(1).replace('-', '/').replace('.', '/')
        
    return datetime.now().strftime("%d/%m/%Y")

def extract_market_name(text):
    clean = re.sub(r'\d{1,2}\s+[A-Za-z]+\s+20\d{2}', '', text)
    clean = re.sub(r'\d{1,2}[\/\.-]\d{1,2}[\/\.-]20\d{2}', '', clean)
    clean = clean.replace("Silk Cocoon Market", "").replace("Government Silk Cocoon", "") \
                 .replace("Daily Rate Report", "").replace("Market Rates", "") \
                 .replace("Kannada Top News", "").replace("Market", "") \
                 .replace("–", "").replace("-", "").replace("|", "").strip()
    return clean if clean else "General Market"

# 🛡️ DATA QUALITY GUARDRAIL (Sanitizes typos/outliers)
def is_valid_rate(val):
    try:
        f = float(val)
        return 150 <= f <= 2000  # Valid cocoon rates in India range between ₹150/kg and ₹2,000/kg
    except Exception:
        return False

def parse_page_content(html_content, items):
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    page_title = title_match.group(1) if title_match else ""

    display_date = extract_date(page_title + " " + html_content)
    market_name = extract_market_name(page_title)

    clean_text = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
    clean_text = re.sub(r'</?(p|tr|td|div|h1|h2|h3)[^>]*>', ' \n ', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
    clean_text = re.sub(r'&nbsp;', ' ', clean_text)
    clean_text = re.sub(r'&#8377;', '₹', clean_text)

    bv_pattern = re.compile(r'(Bi[\s\-]?Voltine|BV|ದ್ವಿತಳಿ)', re.IGNORECASE)
    cb_pattern = re.compile(r'(Cross[\s\-]?Breed|CB|ಮಿಶ್ರತಳಿ)', re.IGNORECASE)

    # Parse BV
    for bv_match in bv_pattern.finditer(clean_text):
        idx = bv_match.start()
        snippet = clean_text[idx:idx+300]
        nums = re.findall(r'\b\d+(?:\.\d+)?\b', snippet)
        nums = [n for n in nums if n not in ['2025', '2026', '2027']]

        if len(nums) >= 5 and is_valid_rate(nums[2]) and is_valid_rate(nums[3]):
            items.append({
                "Date": display_date,
                "Market Name": market_name,
                "Variety": "Bi-Voltine (BV) – ದ್ವಿತಳಿ",
                "Lots": nums[0],
                "Qty (kg)": nums[1],
                "Min": float(nums[2]),
                "Max": float(nums[3]),
                "Avg": float(nums[4])
            })
            break

    # Parse CB
    for cb_match in cb_pattern.finditer(clean_text):
        idx = cb_match.start()
        snippet = clean_text[idx:idx+300]
        nums = re.findall(r'\b\d+(?:\.\d+)?\b', snippet)
        nums = [n for n in nums if n not in ['2025', '2026', '2027']]

        if len(nums) >= 5 and is_valid_rate(nums[2]) and is_valid_rate(nums[3]):
            items.append({
                "Date": display_date,
                "Market Name": market_name,
                "Variety": "Cross-Breed (CB) – ಮಿಶ್ರತಳಿ",
                "Lots": nums[0],
                "Qty (kg)": nums[1],
                "Min": float(nums[2]),
                "Max": float(nums[3]),
                "Avg": float(nums[4])
            })
            break

def parse_all_sources():
    items = []
    visited_urls = set()

    # Discover direct article URLs
    article_urls = []
    for cat_url in CATEGORY_URLS:
        html = fetch_url_with_retry(cat_url)
        if html:
            link_regex = re.compile(r'href="(https:\/\/kannadatopnews\.com\/[a-z0-9\-]*silk-cocoon-market[a-z0-9\-]*\/)"', re.IGNORECASE)
            found_links = link_regex.findall(html)
            for l in found_links:
                if l not in visited_urls:
                    visited_urls.add(l)
                    article_urls.append(l)

    # Crawl each market article page
    for a_url in article_urls[:15]:
        art_html = fetch_url_with_retry(a_url)
        if art_html:
            parse_page_content(art_html, items)

    # RSS Feeds fallback
    for f_url in FEED_URLS:
        feed_html = fetch_url_with_retry(f_url)
        if feed_html:
            parse_page_content(feed_html, items)

    return pd.DataFrame(items)

def update_csv_and_summary():
    today_str = datetime.now().strftime("%d/%m/%Y")

    # ⏱️ SMART EARLY EXIT CHECK
    if os.path.exists(CSV_FILE):
        try:
            df_check = pd.read_csv(CSV_FILE)
            today_records = df_check[df_check['Date'] == today_str]
            # If 10+ major markets for today are already captured, exit in 1s
            if len(today_records) >= 12:
                print(f"⚡ Smart Early Exit: All {len(today_records)} major markets for today ({today_str}) are already fully recorded.")
                return
        except Exception:
            pass

    new_df = parse_all_sources()

    if os.path.exists(CSV_FILE):
        existing_df = pd.read_csv(CSV_FILE)
        if not new_df.empty:
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.drop_duplicates(subset=["Date", "Market Name", "Variety"], keep="last", inplace=True)
        else:
            combined_df = existing_df
    else:
        if not new_df.empty:
            combined_df = new_df
        else:
            combined_df = pd.DataFrame(columns=["Date", "Market Name", "Variety", "Lots", "Qty (kg)", "Min", "Max", "Avg"])

    # Save main CSV
    combined_df.to_csv(CSV_FILE, index=False)
    print(f"CSV updated. Total historical records: {len(combined_df)}")

    # ⚡ GENERATE FAST TODAY SUMMARY JSON FOR MOBILE APP
    try:
        latest_date = combined_df['Date'].iloc[-1] if not combined_df.empty else today_str
        latest_df = combined_df[combined_df['Date'] == latest_date]
        
        summary_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "latest_date": str(latest_date),
            "total_markets": len(latest_df['Market Name'].unique()),
            "bv_avg": float(latest_df[latest_df['Variety'].str.contains('BV|Bi-Voltine', na=False)]['Avg'].mean() or 0),
            "cb_avg": float(latest_df[latest_df['Variety'].str.contains('CB|Cross', na=False)]['Avg'].mean() or 0)
        }
        
        with open(SUMMARY_FILE, "w") as f:
            json.dump(summary_data, f, indent=2)
        print("Summary JSON generated successfully.")
    except Exception as e:
        print("Error generating summary JSON:", e)

if __name__ == "__main__":
    update_csv_and_summary()
