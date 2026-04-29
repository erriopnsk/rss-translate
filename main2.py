# coding:utf-8
import configparser
from pygtrans import Translate
from bs4 import BeautifulSoup
from urllib import request, parse
import urllib
import hashlib
import os
import requests
import html
import re

# =======================
# 🔥 Telegram Config
# =======================
TELEGRAM_TOKEN = "8715919493:AAGPmTrIEG-msszdRaO1Ujdr3AogPablXkI"
CHAT_ID = "@Qassamcircler"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": True
        })
    except Exception as e:
        print("Telegram error:", e)

# =======================
# 🧠 Clean Text
# =======================
def clean(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r'<.*?>', '', text)
    text = text.replace("\r", "")
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

# =======================
# MD5 (prevent duplicate)
# =======================
def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

# =======================
# Load config
# =======================
with open('test.ini', mode='r') as f:
    ini_data = parse.unquote(f.read())

config = configparser.ConfigParser()
config.read_string(ini_data)
secs = config.sections()

def get(sec, name):
    return config.get(sec, name).strip('"')

def setv(sec, name, value):
    config[sec][name] = '"%s"' % value

def get_tra(sec):
    c = config.get(sec, "action").strip('"')
    if "->" in c:
        return c.split("->")[0], c.split("->")[1]
    return "auto", "ar"

BASE = get("cfg", "base")
os.makedirs(BASE, exist_ok=True)

GT = Translate()

# =======================
# 🚀 MAIN FUNCTION
# =======================
def run(sec):

    url = get(sec, "url")
    max_item = int(get(sec, "max"))
    source, target = get_tra(sec)
    old_md5 = get(sec, "md5") if "md5" in config[sec] else ""

    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    xml = request.urlopen(req).read().decode("utf8")

    # 🔁 منع التكرار
    new_md5 = md5(xml)
    if new_md5 == old_md5:
        return
    setv(sec, "md5", new_md5)

    soup = BeautifulSoup(xml, "html.parser")
    items = soup.find_all("item")

    count = 0

    for item in items:

        if count >= max_item:
            break

        title = item.find("title")
        desc = item.find("description")

        title = title.text if title else ""
        desc = desc.text if desc else ""

        if len(title.strip()) < 3:
            continue

        # 🔥 translate
        try:
            arabic = GT.translate(desc, target="ar", source=source).translatedText
            english = GT.translate(desc, target="en", source=source).translatedText
            farsi = GT.translate(desc, target="fa", source=source).translatedText

            title = GT.translate(title, target="ar", source=source).translatedText
        except:
            arabic = desc
            english = desc
            farsi = desc

        # 🧹 clean
        arabic = clean(arabic)
        english = clean(english)
        farsi = clean(farsi)
        title = clean(title)

        # 📡 message format (NO COLORS)
        msg = f"""⭕️ {title}

العربية:
{arabic}

English:
{english}

فارسی:
{farsi}
"""

        send_telegram(msg)

        count += 1

    print("DONE:", url)

# =======================
# RUN ALL SOURCES
# =======================
for s in secs[1:]:
    try:
        run(s)
    except Exception as e:
        print("ERROR:", s, e)

with open("test.ini", "w") as f:
    config.write(f)
