import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd

CSV_FILE = "cocoon_rates.csv"
FEED_URL = "https://kannadatopnews.com/category/announcement/sericulture/silk-cocoon/feed/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def parse_feed():
    items = []
    try:
        req = urllib.request.Request(FEED_URL, headers=HEADERS)
        html_raw = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        
        # Clean XML entities
        html_raw = html_raw.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#8377;", "₹")
        
        root = ET.fromstring(html_raw)
        channel = root.find('channel')
        
        for item in channel.findall('item'):
            title = item.find('title').text if item.find('title') is not None else ""
            desc = item.find('description').text if item.find('description') is not None else ""
            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ""
            
            # Extract Market Name
            market_name = title.replace("Silk Cocoon Market", "").replace("Government Silk Cocoon", "") \
                               .replace("Daily Rate Report", "").replace("Market Rates", "") \
                               .split("–")[0].split("-")[0].strip()
            
            clean_text = re.sub(r'<br\s*/?>', '\n', desc, flags=re.IGNORECASE)
            clean_text = re.sub(r'</?(p|tr|td)[^>]*>', ',', clean_text, flags=re.IGNORECASE)
            clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
            clean_text = re.sub(r'\s+', ' ', clean_text)
            
            # Extract Date
            date_match = re.search(r'Date:\s*([0-9]{1,2}[\/\.-][0-9]{1,2}[\/\.-][0-9]{2,4})', clean_text, re.IGNORECASE)
            if date_match:
                display_date = date_match.group(1).strip()
            elif pubDate:
                try:
                    dt = datetime.strptime(pubDate[:25].strip(), "%a, %d %b %Y %H:%M:%S")
                    display_date = dt.strftime("%d/%m/%Y")
                except Exception:
                    display_date = datetime.now().strftime("%d/%m/%Y")
            else:
                display_date = datetime.now().strftime("%d/%m/%Y")
                
            # Regex to extract variety lines
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
    except Exception as e:
        print("Parsing error:", e)
        
    return pd.DataFrame(items)

def update_csv():
    new_df = parse_feed()
    if new_df.empty:
        print("No new data parsed.")
        return
        
    if os.path.exists(CSV_FILE):
        existing_df = pd.read_csv(CSV_FILE)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        # Deduplicate based on Date, Market Name, and Variety
        combined_df.drop_duplicates(subset=["Date", "Market Name", "Variety"], keep="last", inplace=True)
    else:
        combined_df = new_df
        
    combined_df.to_csv(CSV_FILE, index=False)
    print(f"CSV successfully updated. Total historical records: {len(combined_df)}")

if __name__ == "__main__":
    update_csv()
