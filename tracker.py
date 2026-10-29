import time
import random
import html
import ssl
import json
import os
import re
import requests
import cloudscraper
from bs4 import BeautifulSoup

TOKEN = "8996279782:AAEJ-n3vP4K9bts15GC0_htKMceRC4yHj8E"
CHAT = "5124680786"

LINKS = [
    "https://www.amazon.eg/dp/B0FSY8XC99",
    "https://www.amazon.eg/dp/B098TTS66G",
    "https://www.amazon.eg/dp/B0F7LLTK3K",
    "https://www.amazon.eg/dp/B0DR7897QL",
    "https://www.amazon.eg/dp/B09W3PMS75",
    "https://www.amazon.eg/dp/B08WJPZXMJ",
    "https://www.amazon.eg/dp/B09WKSXTJ9",
    "https://www.amazon.eg/dp/B08Z6F4LZB",
    "https://www.amazon.eg/dp/B0H1D61L5C",
    "https://www.amazon.eg/dp/B0GJPYRBC8",
    "https://www.amazon.eg/dp/B0H9XSKG4L",
    "https://www.amazon.eg/dp/B0FPFSK7P5",
    "https://www.amazon.eg/dp/B0DR78TWXH",
    "https://www.amazon.eg/dp/B0CDV8VC24",
    "https://www.amazon.eg/dp/B0GNZL4LDW",
    "https://www.amazon.eg/dp/B0F9KW5QFR",
    "https://www.amazon.eg/dp/B0D2D8RHWQ",
    "https://www.amazon.eg/dp/B0G6ZK28XD",
    "https://www.amazon.eg/dp/B098KPQKH4",
    "https://www.amazon.eg/dp/B091J53S75",
    "https://www.amazon.eg/dp/B091K4FSMH",
    "https://www.amazon.eg/dp/B09T7KXCPH",
    "https://www.amazon.eg/dp/B0CDVHRG14",
    "https://www.amazon.eg/dp/B091P1D477",
    "https://www.amazon.eg/dp/B09TBHN2GG",
    "https://www.amazon.eg/dp/B0D294DCZ5",
    "https://www.amazon.eg/dp/B09TT5HYKN",
    "https://www.amazon.eg/dp/B0FTMJ3145",
    "https://www.amazon.eg/dp/B0F7LDT517",
    "https://www.amazon.eg/dp/B0D9YP55PL",
    "https://www.amazon.eg/dp/B09W44JLV3",
    "https://www.amazon.eg/dp/B09N6YP9F3",
    "https://www.amazon.eg/dp/B091NZ7PG9",
    "https://www.amazon.eg/dp/B0GNN5C3VT",
    "https://www.amazon.eg/dp/B08X63FTM3",
    "https://www.amazon.eg/dp/B09T7NDTMH",
    "https://www.amazon.eg/dp/B0FTMJJQB8",
    "https://www.amazon.eg/dp/B0FCM8KP9R",
    "https://www.amazon.eg/dp/B09TW2ZD5G",
    "https://www.amazon.eg/dp/B092Q348ZC",
    "https://www.amazon.eg/dp/B0DR79BW47",
    "https://www.amazon.eg/dp/B0HBXFM7W6",
    "https://www.amazon.eg/dp/B091DBNSVV",
    "https://www.amazon.eg/dp/B0GHYBWMMM",
    "https://www.amazon.eg/dp/B09Y5TYD9K",
    "https://www.amazon.eg/dp/B0CK2NH39L",
    "https://www.amazon.eg/dp/B08ZNT5F8R",
    "https://www.amazon.eg/dp/B098KQVZSK",
    "https://www.amazon.eg/dp/B0GNN3VJ7D",
    "https://www.amazon.eg/dp/B0H31G3G46"
]

DB_FILE = "direct_products_prices.json"

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
}

AR = str.maketrans("٠١٢٣٤٥٦٧٨٩٫٬", "0123456789.,")

if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_prices = json.load(f)
    except Exception:
        last_prices = {}
else:
    last_prices = {}

def save_prices():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(last_prices, f, ensure_ascii=False, indent=2)

def create_scraper():
    ctx = ssl.create_default_context()
    ctx.set_ciphers("DEFAULT@SECLEVEL=1")
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True},
        ssl_context=ctx
    )
    scraper.headers.update(H)
    return scraper

scraper = create_scraper()

def send(msg):
    u = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(u, json={"chat_id": CHAT, "text": msg, "parse_mode": "HTML"}, timeout=15)
        time.sleep(1.5)
    except Exception as e:
        print("Telegram error:", e)

def clean(text):
    x = text.translate(AR).replace(",", "")
    m = re.search(r"\d+(?:\.\d+)?", x)
    return float(m.group(0)) if m else None

def extract_asin_from_url(url):
    m = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
    return m.group(1) if m else None

def check_product(url):
    global scraper
    asin = extract_asin_from_url(url)
    if not asin:
        return

    print(f"Checking ASIN: {asin}...", end=" ", flush=True)
    try:
        r = scraper.get(url, timeout=15)
        print(f"[Status: {r.status_code}]")
        
        if r.status_code != 200:
            print("-> تم حظر الطلب أو حدث خطأ، جاري إعادة ضبط السكريبر...")
            scraper = create_scraper()
            return

        s = BeautifulSoup(r.text, "html.parser")
        
        title_tag = s.select_one("#productTitle")
        raw_name = title_tag.get_text(strip=True) if title_tag else f"منتج أمازون ({asin})"
        
        price = None
        price_selectors = [
            ".priceToPay span.a-offscreen",
            "#apex_desktop .a-price .a-offscreen",
            ".a-price .a-offscreen", 
            "#corePrice_desktop .a-price-whole", 
            "#priceblock_ourprice", 
            "#priceblock_dealprice",
            ".a-price-whole",
            "span[data-a-color='price'] span.a-offscreen"
        ]
        for sel in price_selectors:
            tag = s.select_one(sel)
            if tag:
                price = clean(tag.get_text())
                if price and price > 0:
                    break

        if price is None:
            print("-> لم يتم العثور على السعر (ربما صفحة حماية أو نفاد الكمية).")
            return

        old_price = last_prices.get(asin)
        
        # 1. لو أول مرة يرصد المنتج: يحفظ السعر بصمت بدون إرسال إشعار
        if old_price is None:
            last_prices[asin] = price
            save_prices()
            print(f"-> أول رصد للمنتج بالسعر: {price} ج.م (تم الحفظ بدون إشعار)")
            return

        # 2. لو السعر نزل: نحسب نسبة الخصم
        if price < old_price:
            drop_amount = old_price - price
            drop_percent = (drop_amount / old_price) * 100
            
            # شرط إرسال الإشعار: نسبة الخصم أكبر من 20%
            if drop_percent > 20:
                safe_name = html.escape(raw_name)
                product_link = f"https://www.amazon.eg/dp/{asin}"
                
                price_status_text = (
                    f"\n📉 السعر السابق: <s>{old_price} ج.م</s>"
                    f"\n💰 السعر الحالي: <b>{price} ج.م</b>"
                    f"\n🔥 هبوط قوي بنسبة <b>{drop_percent:.1f}%</b> (وفرت {drop_amount:.0f} ج.م)"
                )
                
                msg = (
                    f"🚨 <b>تنبيه خصم كبير (+20%):</b>\n\n"
                    f"🛒 <a href='{product_link}'>{safe_name}</a>"
                    f"{price_status_text}"
                )
                send(msg)
                
                # تحديث السعر في قاعدة البيانات بعد إرسال الإشعار
                last_prices[asin] = price
                save_prices()
                print(f"-> 🔥 تم إرسال إشعار! خصم {drop_percent:.1f}% (السعر الجديد: {price} ج.م)")
            else:
                # لم نحدث السعر هنا لكي لا يضيع الخصم لو نزل السعر تدريجياً على عدة مرات
                print(f"-> انخفاض بسيط ({drop_percent:.1f}%) أقل من 20% (لم يتم الإرسال)")
        
        # 3. لو السعر زاد: نحدث السعر الجديد بصمت لنقارن أي خصم قادم بناءً عليه
        elif price > old_price:
            last_prices[asin] = price
            save_prices()
            print(f"-> ارتفع السعر إلى {price} ج.م (تم التحديث بصمت)")
            
        # 4. لو السعر ثابت
        else:
            print(f"-> السعر ثابت ({price} ج.م)")
        
    except Exception as e:
        print(f"-> خطأ في الاتصال: {e}")
        scraper = create_scraper()

while True:
    for link in LINKS:
        check_product(link)
        time.sleep(random.randint(8, 15))
    print("\n--- تم فحص جميع المنتجات، جاري الانتظار للجولة القادمة ---\n")
    time.sleep(1800)
