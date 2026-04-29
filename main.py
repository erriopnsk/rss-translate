# coding:utf-8
import sqlite3
import hashlib
import time
import requests
import re
from bs4 import BeautifulSoup
from urllib import request
from pygtrans import Translate

# =========================
# 🔥 CONFIG
# =========================
TELEGRAM_TOKEN = "8715919493:AAGPmTrIEG-msszdRaO1Ujdr3AogPablXkI"
CHAT_ID = "@Qassamcircler"

RSS_FEEDS = [
    "https://tg.i-c-a.su/rss/AjaNews",
    "https://tg.i-c-a.su/rss/almayadeen"
]

# =========================
# 🧠 DATABASE
# =========================
conn = sqlite3.connect("rss_bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS sent_news (
    id TEXT PRIMARY KEY
)
""")
conn.commit()

def already_sent(news_id):
    cur.execute("SELECT id FROM sent_news WHERE id=?", (news_id,))
    return cur.fetchone() is not None

def save_news(news_id):
    cur.execute("INSERT OR IGNORE INTO sent_news (id) VALUES (?)", (news_id,))
    conn.commit()

# =========================
# ⚡ TOOLS
# =========================
GT = Translate()

def md5(text):
    return hashlib.md5(text.encode()).hexdigest()

def clean(text):
    text = BeautifulSoup(text, "html.parser").text
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def normalize(text):
    text = re.sub(r"(عاجل\s*\|\s*)+", "", text)
    text = re.sub(r"(Urgent\s*\|\s*)+", "", text)
    text = re.sub(r"(فوری\s*\|\s*)+", "", text)
    text = re.sub(r"^🔴\s*", "", text)
    return text.strip()

# =========================
# 🌍 TRANSLATION
# =========================
def translate(text):
    try:
        en = GT.translate(text, target="en").translatedText
    except:
        en = text

    try:
        fa = GT.translate(text, target="fa").translatedText
    except:
        fa = text

    return normalize(en), normalize(fa)

# =========================
# 📩 TELEGRAM
# =========================
def send(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            },
            timeout=10
        )
    except:
        pass

# =========================
# 📰 FORMAT (BOLD FULL)
# =========================
def format_msg(ar, en, fa):
    return f"""**🔴 عاجل | {ar}**

**🔴 Urgent | {en}**

**🔴 فوری | {fa}**
"""

# =========================
# 🌐 FETCH RSS
# =========================
def fetch(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    req = request.Request(url, headers=headers)
    xml = request.urlopen(req, timeout=10).read().decode("utf-8")
    return BeautifulSoup(xml, "xml")

# =========================
# 🧠 PROCESS (FIXED CORE)
# =========================
def process(url):

    soup = fetch(url)
    items = soup.find_all("item")

    if not items:
        return

    item = items[0]  # أحدث خبر فقط

    title = clean(item.title.text if item.title else "")
    desc = clean(item.description.text if item.description else "")

    # منع تكرار النص داخل نفسه
    if desc and (title in desc or desc in title):
        desc = ""

    text = clean(f"{title} {desc}" if desc else title)

    if not text:
        return

    news_id = md5(text)

    if already_sent(news_id):
        return

    save_news(news_id)

    en, fa = translate(text)

    msg = format_msg(text, en, fa)

    send(msg)

    print("SENT:", title[:60])

# =========================
# 🚀 ENGINE
# =========================
def run():
    while True:
        for url in RSS_FEEDS:
            try:
                process(url)
                time.sleep(5)
            except Exception as e:
                print("ERROR:", url, e)

        time.sleep(60)

# =========================
run()
