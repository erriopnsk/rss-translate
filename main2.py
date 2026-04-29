# coding:utf-8
import configparser
import hashlib
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib import request, parse

# =======================
# 🔥 Telegram
# =======================
TELEGRAM_TOKEN = "8715919493:AAGPmTrIEG-msszdRaO1Ujdr3AogPablXkI"
CHAT_ID = "@Qassamcircler"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        })
    except Exception as e:
        print("Telegram error:", e)

# =======================
# تنظيف النص
# =======================
def clean(text):
    text = BeautifulSoup(text, "html.parser").text
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_breaking(text):
    text = clean(text)
    text = text.replace("⭕️", "")
    text = re.sub(r'عاجل\s*\|', '', text)
    return text.strip()

# =======================
# MD5 منع تكرار
# =======================
def md5(text):
    return hashlib.md5(text.encode()).hexdigest()

seen = set()

# =======================
# config
# =======================
with open("test.ini", "r", encoding="utf-8") as f:
    ini = parse.unquote(f.read())

config = configparser.ConfigParser()
config.read_string(ini)
secs = config.sections()

def get(sec, key):
    return config.get(sec, key).strip('"')

# =======================
# استخراج RSS قوي
# =======================
def parse_item(item):

    title = item.find("title")
    desc = item.find("description")
    content = item.find("content:encoded")

    title = title.text if title else ""
    desc = desc.text if desc else ""
    content = content.text if content else ""

    full = f"{title}\n{desc}\n{content}"
    return full

# =======================
# تشغيل مصدر
# =======================
def run(sec):

    url = get(sec, "url")
    max_item = int(get(sec, "max"))

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        req = request.Request(url, headers=headers)
        xml = request.urlopen(req, timeout=10).read().decode("utf-8")
    except:
        return

    soup = BeautifulSoup(xml, "xml")
    items = soup.find_all("item")

    count = 0

    for item in items:

        if count >= max_item:
            break

        text = parse_item(item)
        text = remove_breaking(text)

        uid = md5(text)

        if uid in seen:
            continue

        seen.add(uid)

        # =======================
        # شكل احترافي نهائي
        # =======================
        msg = f"""🟥 <b>عاجل</b> | {text}
"""

        send_telegram(msg)

        count += 1
        time.sleep(2)

# =======================
# تشغيل دائم 24/7
# =======================
while True:
    for sec in secs[1:]:
        try:
            run(sec)
        except Exception as e:
            print("Error:", e)

    time.sleep(15)
