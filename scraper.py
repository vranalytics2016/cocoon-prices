import os
import re
import urllib.request
from datetime import datetime
import pandas as pd

CSV_FILE = "cocoon_rates.csv"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_url_content(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        return urllib.request.urlopen(req, timeout=12).read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def extract_date(text):
    # Match "17 August 2026" or "18 August 2026"
    m1 = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})', text)
    if m1:
        day, month_str, year = m1.groups()
        try:
            dt = datetime.strptime(f"{day} {month_str} {year}", "%d %B %Y")
            return dt.strftime("%d/%m/%Y")
        except Exception:
            pass
    
    # Match "17/08/2026" or "17-08-2026"
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

def parse_page_content(html_content, items):
    # Clean HTML comments
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # Extract page title
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    page_title = title_match.group(1) if title_match else ""

    display_date = extract_date(page_title + " " + html_content)
    market_name = extract_market_name(page_title)

    # Convert HTML to clean whitespace-separated text
    clean_text = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
    clean_text = re.sub(r'</?(p|tr|td|div|h1|h2|h3)[^>]*>', ' \n ', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
    clean_text = re.sub(r'&nbsp;', ' ', clean_text)
    clean_text = re.sub(r'&#8377;', '₹', clean_text)

    # Keywords for BV and CB
    bv_pattern = re.compile(r'(Bi[\s\-]?Voltine|BV|ದ್ವಿತಳಿ)', re.IGNORECASE)
    cb_pattern = re.compile(r'(Cross[\s\-]?Breed|CB|ಮಿಶ್ರತಳಿ)', re.IGNORECASE)

    # Parse BV
    for bv_match in bv_pattern.finditer(clean_text):
        idx = bv_match.start()
        snippet = clean_text[idx:idx+300]
        nums = re.findall(r'\b\d+(?:\.\d+)?\b', snippet)
        
        # Filter out 4-digit years like 2026 if present
        nums = [n for n in nums if n != '2026' and n != '2025']

        if len(nums) >= 5:
            items.append({
                "Date": display_date,
                "Market Name": market_name,
                "Variety": "Bi-Voltine (BV) – ದ್ವಿತಳಿ",
                "Lots": nums[0],
                "Qty (kg)": nums[1],
                "Min": nums[2],
                "Max": nums[3],
                "Avg": nums[4]
            })
            break
        elif len(nums) >= 3:
            items.append({
                "Date": display_date,
                "Market Name": market_name,
                "Variety": "Bi-Voltine (BV) – ದ್ವಿತಳಿ",
                "Lots": "-",
                "Qty (kg)": "-",
                "Min": nums[0],
                "Max": nums[1],
                "Avg": nums[2]
            })
            break

    # Parse CB
    for cb_match in cb_pattern.finditer(clean_text):
        idx = cb_match.start()
        snippet = clean_text[idx:idx+300]
        nums = re.findall(r'\b\d+(?:\.\d+)?\b', snippet)
        nums = [n for n in nums if n != '2026' and n != '2025']

        if len(nums) >= 5:
            items.append({
                "Date": display_date,
                "Market Name": market_name,
                "Variety": "Cross-Breed (CB) – ಮಿಶ್ರತಳಿ",
                "Lots": nums[0],
                "Qty (kg)": nums[1],
                "Min": nums[2],
                "Max": nums[3],
                "Avg": nums[4]
            })
            break
        elif len(nums) >= 3:
            items.append({
                "Date": display_date,
                "Market Name": market_name,
                "Variety": "Cross-Breed (CB) – ಮಿಶ್ರತಳಿ",
                "Lots": "-",
                "Qty (kg)": "-",
                "Min": nums[0],
                "Max": nums[1],
                "Avg": nums[2]
            })
            break

def parse_all_sources():
    items = []
    visited_urls = set()

    # Step 1: Discover individual market article links from category pages
    category_urls = [
        "https://kannadatopnews.com/category/announcement/sericulture/",
        "https://kannadatopnews.com/category/announcement/sericulture/silk-cocoon/"
    ]

    article_urls = []
    for cat_url in category_urls:
        html = fetch_url_content(cat_url)
        if html:
            link_regex = re.compile(r'href="(https:\/\/kannadatopnews\.com\/[a-z0-9\-]*silk-cocoon-market[a-z0-9\-]*\/)"', re.IGNORECASE)
            found_links = link_regex.findall(html)
            for l in found_links:
                if l not in visited_urls:
                    visited_urls.add(l)
                    article_urls.append(l)

    print(f"Found {len(article_urls)} market article links.")

    # Step 2: Fetch each individual article page directly
    for a_url in article_urls[:15]:
        art_html = fetch_url_content(a_url)
        if art_html:
            parse_page_content(art_html, items)

    # Step 3: Also parse RSS feeds
    feed_urls = [
        "https://kannadatopnews.com/category/announcement/sericulture/feed/",
        "https://kannadatopnews.com/category/announcement/sericulture/silk-cocoon/feed/"
    ]
    for f_url in feed_urls:
        feed_html = fetch_url_content(f_url)
        if feed_html:
            parse_page_content(feed_html, items)

    return pd.DataFrame(items)

def update_csv():
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

    combined_df.to_csv(CSV_FILE, index=False)
    print(f"CSV successfully updated. Total historical records: {len(combined_df)}")

if __name__ == "__main__":
    update_csv()
