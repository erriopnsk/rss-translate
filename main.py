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
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            },
            timeout=10
        )
    except:
        pass

# =======================
# أدوات
# =======================
seen = set()

def md5(x):
    return hashlib.md5(x.encode()).hexdigest()

def clean_text(text):
    text = BeautifulSoup(text, "html.parser").text
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def remove_duplicate(text):
    parts = re.split(r'[.!?]', text)
    unique = []
    for p in parts:
        p = p.strip()
        if p and p not in unique:
            unique.append(p)
    return ". ".join(unique)

# =======================
# فلترة الأخبار
# =======================
FILTER_WORDS = [
    "إسرائيل","اسرائيل","الاحتلال","الكيان",
    "إيران","إيراني",
    "لبنان","حزب الله",
    "فلسطين","غزة","الضفة","القدس",
    "Israel","Israeli","Iran","Lebanon","Palestine","Gaza"
]

def is_valid_news(text):
    for w in FILTER_WORDS:
        if w.lower() in text.lower():
            return True
    return False

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

    en = remove_duplicate(en)
    fa = remove_duplicate(fa)

    en = en.replace("Urgent |", "").strip()
    fa = fa.replace("فوری |", "").strip()

    return en, fa

# =======================
# تنسيق الرسالة
# =======================
def format_msg(title, en, fa):
    return f"""<b>🔴 عاجل | {title}</b>

<b>⭕️Urgent| {en}</b>

<b>⭕️فوری| {fa}</b>
"""

# =======================
# RSS CORE (مصحح 100%)
# =======================
def run(sec):

    url = get(sec, "url")
    max_item = int(get(sec, "max"))

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        req = request.Request(url, headers=headers)
        xml = request.urlopen(req, timeout=10).read().decode("utf-8")
    except:
        print("RSS ERROR:", url)
        return

    soup = BeautifulSoup(xml, "html.parser")
    items = soup.find_all("item")

    count = 0

    for item in items:

        if count >= max_item:
            break

        title = clean_text(item.title.text if item.title else "")
        desc = clean_text(item.description.text if item.description else "")

        # 🔥 أهم تعديل: دمج الخبر الكامل
        text = f"{title} {desc}".strip()

        if not title:
            continue

        # فلترة
        if not is_valid_news(text):
            continue

        # منع التكرار
        key = md5(title)
        if key in seen:
            continue
        seen.add(key)

        # ترجمة النص الكامل
        en, fa = translate(text)

        msg = format_msg(text, en, fa)

        send(msg)

        print("SENT:", title[:60])

        count += 1
        time.sleep(2)

# =======================
# تشغيل دائم
# =======================
while True:
    for sec in secs[1:]:
        run(sec)
        time.sleep(15)

    time.sleep(60)
