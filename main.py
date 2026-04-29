# coding:utf-8
import configparser
import hashlib
import socket
import time
import requests
import re
from bs4 import BeautifulSoup
from urllib import request, parse
from pygtrans import Translate

# =======================
# ⚡ منع التعليق
# =======================
socket.setdefaulttimeout(10)

# =======================
# 🔥 Telegram
# =======================
TELEGRAM_TOKEN = "8715919493:AAGPmTrIEG-msszdRaO1Ujdr3AogPablXkI"
CHAT_ID = "@Qassamcircler"

def send(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML",  # 🔥 لتفعيل bold
                "disable_web_page_preview": True
            },
            timeout=10
        )
    except:
        pass

# =======================
# أدوات تنظيف
# =======================
seen = set()

def md5(x):
    return hashlib.md5(x.encode()).hexdigest()

def clean_text(text):
    text = BeautifulSoup(text, "html.parser").text
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# 🔥 إزالة التكرار داخل الجمل
def remove_duplicate(text):
    parts = re.split(r'[.!?]', text)
    unique = []
    for p in parts:
        p = p.strip()
        if p and p not in unique:
            unique.append(p)
    return ". ".join(unique)

# =======================
# تحميل الإعدادات
# =======================
with open("test.ini", "r", encoding="utf-8") as f:
    ini = parse.unquote(f.read())

config = configparser.ConfigParser()
config.read_string(ini)
secs = config.sections()

def get(sec, key):
    return config.get(sec, key).strip('"')

# =======================
# الترجمة
# =======================
GT = Translate()

def translate(text):
    try:
        en = GT.translate(text, target="en").translatedText
    except:
        en = text

    try:
        fa = GT.translate(text, target="fa").translatedText
    except:
        fa = text

    # 🔥 إزالة التكرار
    en = remove_duplicate(en)
    fa = remove_duplicate(fa)

    # 🔥 تنظيف كلمات عاجل
    en = en.replace("Urgent | Urgent |", "").replace("Urgent |", "").strip()
    fa = fa.replace("فوری | فوری |", "").replace("فوری |", "").strip()

    return en, fa

# =======================
# تنسيق الرسالة (Bold كامل)
# =======================
def format_msg(title, en, fa):
    return f"""<b>🔴 عاجل | {title}</b>

<b>⭕️Urgent| {en}</b>

<b>⭕️فوری| {fa}</b>
"""

# =======================
# RSS CORE
# =======================
def run(sec):

    url = get(sec, "url")
    max_item = int(get(sec, "max"))

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        req = request.Request(url, headers=headers)
        xml = request.urlopen(req, timeout=10).read().decode("utf-8")
    except Exception:
        print("RSS ERROR:", url)
        return

    soup = BeautifulSoup(xml, "html.parser")
    items = soup.find_all("item")

    count = 0

    for item in items:

        if count >= max_item:
            break

        title = clean_text(item.title.text if item.title else "")

        if not title:
            continue

        # 🔥 منع تكرار الأخبار
        key = md5(title)
        if key in seen:
            continue
        seen.add(key)

        # ✅ نستخدم العنوان فقط (حل المشكلة)
        text = title

        en, fa = translate(text)

        msg = format_msg(title, en, fa)

        send(msg)

        print("SENT:", title[:60])

        count += 1
        time.sleep(1)

# =======================
# تشغيل دائم
# =======================
while True:
    for sec in secs[1:]:
        run(sec)

    time.sleep(5)
