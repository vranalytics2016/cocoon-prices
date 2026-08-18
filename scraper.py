import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd

CSV_FILE = "cocoon_rates.csv"

# Parent category feeds and web URLs
FEED_URLS = [
    "https://kannadatopnews.com/category/announcement/sericulture/feed/",
    "https://kannadatopnews.com/category/announcement/sericulture/silk-cocoon/feed/",
    "https://kannadatopnews.com/feed/"
]

WEB_URL = "https://kannadatopnews.com/category/announcement/sericulture/"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def extract_items_from_text(title, content_text, pubDate, items):
    # 1. Extract Date directly from Title (e.g. "17 August 2026" -> "17/08/2026")
    display_date = None
    
    # Check title for "17 August 2026" or "17/08/2026"
    title_date_match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', title)
    if title_date_match:
        day, month_str, year = title_date_match.groups()
        try:
            dt = datetime.strptime(f"{day} {month_str} {year}", "%d %B %Y")
            display_date = dt.strftime("%d/%m/%Y")
        except Exception:
            pass

    if not display_date:
        numeric_date_match = re.search(r'([0-9]{1,2}[\/\.-][0-9]{1,2}[\/\.-][0-9]{2,4})', title)
        if numeric_date_match:
            display_date = numeric_date_match.group(1).strip()

    if not display_date:
        body_date_match = re.search(r'Date:\s*([0-9]{1,2}[\/\.-][0-9]{1,2}[\/\.-][0-9]{2,4})', content_text, re.IGNORECASE)
        if body_date_match:
            display_date = body_date_match.group(1).strip()

    if not display_date and pubDate:
        try:
            dt = datetime.strptime(pubDate[:25].strip(), "%a, %d %b %Y %H:%M:%S")
            display_date = dt.strftime("%d/%m/%Y")
        except Exception:
            display_date = datetime.now().strftime("%d/%m/%Y")

    if not display_date:
        display_date = datetime.now().strftime("%d/%m/%Y")

    # 2. Extract Market Name from Title
    clean_title = re.sub(r'\d{1,2}\s+[A-Za-z]+\s+\d{4}', '', title) # Remove date from title
    market_name = clean_title.replace("Silk Cocoon Market", "").replace("Government Silk Cocoon", "") \
                       .replace("Daily Rate Report", "").replace("Market Rates", "") \
                       .replace("Market", "").replace("–", "").replace("-", "").replace("|", "").strip()

    if not market_name:
        market_name = "General Market"

    # 3. Clean Text
    clean_text = re.sub(r'<br\s*/?>', '\n', content_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'</?(p|tr|td)[^>]*>', ',', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text)

    # 4. Regex for Variety lines (Supports comma separated and text lines)
    csv_regex = re.compile(
        r'(Cross[\s\-]?Breed|Bi[\s\-]?Voltine|CB|BV|ಮಿಶ್ರತಳಿ|ದ್ವಿತಳಿ)[^\n,]*,\s*([0-9\.]+)\s*,\s*([0-9\.]+)\s*,\s*₹?\s*([0-9\.]+)\s*,\s*₹?\s*([0-9\.]+)\s*,\s*₹?\s*([0-9\.]+)',
        re.IGNORECASE
    )

    for m in csv_regex.finditer(clean_text):
        raw_v = m.group(1).lower()
        v_label = "Bi-Voltine (BV) – ದ್ವಿತಳಿ" if any(x in raw_v for x in ['bi', 'bv', 'ದ್ವಿತಳಿ']) else "Cross-Breed (CB) – ಮಿಶ್ರತಳಿ"

        items.append({
            "Date": display_date,
            "Market Name": market_name,
            "Variety": v_label,
            "Lots": m.group(2).strip(),
            "Qty (kg)": m.group(3).strip(),
            "Min": m.group(4).strip(),
            "Max": m.group(5).strip(),
            "Avg": m.group(6).strip()
        })

def parse_feed():
    items = []

    # Method 1: Scan multiple RSS feeds
    for feed_url in FEED_URLS:
        try:
            req = urllib.request.Request(feed_url, headers=HEADERS)
            html_raw = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
            html_raw = html_raw.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#8377;", "₹")

            if "<item>" in html_raw:
                root = ET.fromstring(html_raw)
                channel = root.find('channel')
                for item in channel.findall('item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    desc = item.find('description').text if item.find('description') is not None else ""
                    pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    extract_items_from_text(title, desc, pubDate, items)
        except Exception as e:
            print(f"Feed error ({feed_url}):", e)

    # Method 2: Direct Category Scraping Fallback
    if len(items) == 0:
        try:
            req = urllib.request.Request(WEB_URL, headers=HEADERS)
            cat_html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')

            link_regex = re.compile(r'href="(https:\/\/kannadatopnews\.com\/[a-z0-9\-]*silk-cocoon-market[a-z0-9\-]*\/)"', re.IGNORECASE)
            article_urls = list(set(link_regex.findall(cat_html)))[:12]

            for url in article_urls:
                try:
                    areq = urllib.request.Request(url, headers=HEADERS)
                    art_html = urllib.request.urlopen(areq, timeout=10).read().decode('utf-8', errors='ignore')
                    title_match = re.search(r'<title>(.*?)</title>', art_html, re.IGNORECASE)
                    title = title_match.group(1) if title_match else "Silk Cocoon Market"
                    extract_items_from_text(title, art_html, None, items)
                except Exception as err:
                    print("Article fetch error:", err)
        except Exception as e:
            print("Web scraping error:", e)

    return pd.DataFrame(items)

def update_csv():
    new_df = parse_feed()

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

    combined_df.to_csv(CSV_FILE, index=False)
    print(f"CSV successfully updated. Total historical records: {len(combined_df)}")

if __name__ == "__main__":
    update_csv()
