# coding:utf-8
import configparser
import hashlib
import os
import socket
import time
import requests
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
                "disable_web_page_preview": True
            },
            timeout=10
        )
    except:
        pass

# =======================
# أدوات
# =======================
def md5(x):
    return hashlib.md5(x.encode()).hexdigest()

def clean(t):
    return BeautifulSoup(t, "html.parser").text.strip()

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

    return en, fa

# =======================
# RSS
# =======================
def run(sec):

    count = 0

    for item in items:

        if count >= max_item:
            break

        title = item.find('title')
        desc = item.find('description')

        title = title.text if title else ""
        desc = desc.text if desc else ""

        count += 1

    for item in items:

        if count >= max_item:
            break

        title = clean(item.title.text if item.title else "")
        desc = clean(item.description.text if item.description else "")

        if not title:
            continue

        text = title + " " + desc

        en, fa = translate(text)

        msg = f"""🔴 {title}

🔴 URGENT | {en}

🔴 فوری | {fa}
"""

        send(msg)

        print("SENT:", title[:40])

        count += 1
        time.sleep(1)

# =======================
# تشغيل دائم
# =======================
while True:
    for sec in secs[1:]:
        run(sec)

    time.sleep(5)
