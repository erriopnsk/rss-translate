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

def clean_all(text):
    text = re.sub(r"(عاجل\s*\|\s*)+", "", text)
    text = re.sub(r"(Urgent\s*\|\s*)+", "", text)
    text = re.sub(r"(فوری\s*\|\s*)+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def smart_dedupe(text):
    parts = re.split(r'[.!؟?]', text)
    seen_local = set()
    out = []

    for p in parts:
        p = p.strip()
        if not p:
            continue
        if any(p in x or x in p for x in seen_local):
            continue
        seen_local.add(p)
        out.append(p)

    return ". ".join(out).strip()

def make_key(text):
    text = clean_all(text)
    text = smart_dedupe(text)
    return md5(text)

# =======================
# فلترة الأخبار
# =======================
FILTER_WORDS = [
    "إسرائيل","الاحتلال","إيران","لبنان","فلسطين","غزة",
    "Israel","Iran","Lebanon","Palestine","Gaza"
]

def is_valid_news(text):
    return any(w.lower() in text.lower() for w in FILTER_WORDS)

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
    text = smart_dedupe(text)

    try:
        en = GT.translate(text, target="en").translatedText
    except:
        en = text

    try:
        fa = GT.translate(text, target="fa").translatedText
    except:
        fa = text

    en = smart_dedupe(clean_all(en))
    fa = smart_dedupe(clean_all(fa))

    return en, fa

# =======================
# تنسيق الرسالة
# =======================
def format_msg(title, en, fa):
    return f"""<b>🔴 عاجل | {title}</b>

<b>🔴 Urgent | {en}</b>

<b>🔴 فوری | {fa}</b>
"""

# =======================
# RSS CORE (آخر خبر فقط)
# =======================
def run(sec):

    url = get(sec, "url")

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        req = request.Request(url, headers=headers)
        xml = request.urlopen(req, timeout=10).read().decode("utf-8")
    except:
        print("RSS ERROR:", url)
        return

    soup = BeautifulSoup(xml, "html.parser")
    items = soup.find_all("item")

    if not items:
        return

    # 🔥 فقط أحدث خبر
    item = items[0]

    title = clean_text(item.title.text if item.title else "")
    desc = clean_text(item.description.text if item.description else "")

    if not title:
        return

    text = clean_all(f"{title} {desc}")
    text = smart_dedupe(text)

    key = make_key(text)
    if key in seen:
        return
    seen.add(key)

    en, fa = translate(text)

    msg = format_msg(text, en, fa)

    send(msg)

    print("SENT LATEST:", title[:60])

# =======================
# تشغيل دائم
# =======================
while True:
    for sec in secs[1:]:
        run(sec)
        time.sleep(10)

    time.sleep(60)
