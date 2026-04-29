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
    text = re.sub(r".*?", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

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

    # تنظيف بسيط من التكرار
    en = en.replace("Urgent | Urgent |", "Urgent |").strip()
    fa = fa.replace("فوری | فوری |", "فوری |").strip()

    return en, fa

# =======================
# تنسيق الرسالة (المطلوب)
# =======================
def format_msg(title, en, fa):
    return f"""🔴 عاجل | {title}

⭕️Urgent| {en}

⭕️فوری| {fa}
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

    soup = BeautifulSoup(xml, "xml")
    items = soup.find_all("item")

    count = 0

    for item in items:

        if count >= max_item:
            break

        title = clean_text(item.title.text if item.title else "")
        desc
