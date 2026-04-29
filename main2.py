# coding:utf-8
import configparser
from pygtrans import Translate
from bs4 import BeautifulSoup
from urllib import request, parse
import urllib
import hashlib
import os
import requests
import re
import time

# =======================
# 🔥 Telegram Settings
# =======================
TELEGRAM_TOKEN = "8715919493:AAGPmTrIEG-msszdRaO1Ujdr3AogPablXkI"
CHAT_ID = "@Qassamcircler"

# =======================
# إرسال تيليجرام (نص فقط)
# =======================
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": text
        })
    except Exception as e:
        print("Telegram error:", e)

# =======================
# أدوات تنظيف
# =======================
def get_md5_value(src):
    m = hashlib.md5()
    m.update(src.encode('utf-8'))
    return m.hexdigest()

def clean(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_breaking(text):
    text = clean(text)
    text = re.sub(r'^(⭕️?\s*)?عاجل\s*\|\s*', '', text)
    text = re.sub(r'\bعاجل\b\s*\|\s*', '', text)
    return text.strip()

# =======================
# تحميل الإعدادات
# =======================
with open('test.ini', mode='r') as f:
    ini_data = parse.unquote(f.read())

config = configparser.ConfigParser()
config.read_string(ini_data)
secs = config.sections()

def get_cfg(sec, name):
    return config.get(sec, name).strip('"')

def get_cfg_tra(sec):
    cc = config.get(sec, "action").strip('"')
    if "->" in cc:
        return cc.split('->')[0], cc.split('->')[1]
    return "auto", "en"

BASE = get_cfg("cfg", "base")

try:
    os.makedirs(BASE)
except:
    pass

GT = Translate()

# =======================
# منع تكرار الأخبار
# =======================
sent_news = set()

# =======================
# النظام الرئيسي
# =======================
def tran(sec):

    url = get_cfg(sec, 'url')
    max_item = int(get_cfg(sec, 'max'))
    source, target = get_cfg_tra(sec)

    headers = {'User-Agent': 'Mozilla/5.0'}

    req = urllib.request.Request(url, headers=headers)
    xml = request.urlopen(req).read().decode('utf8')

    soup = BeautifulSoup(xml, "html.parser")
    items = soup.find_all('item')

    count = 0

    for item in items:

        if count >= max_item:
            break

        title = item.find('title')
        desc = item.find('description')

        title = clean_breaking(title.text if title else "")
        desc = clean_breaking(desc.text if desc else "")

        # منع التكرار
        news_id = get_md5_value(title + desc)
        if news_id in sent_news:
            continue
        sent_news.add(news_id)

        try:
            english = GT.translate(desc, target="en", source=source).translatedText
            farsi = GT.translate(desc, target="fa", source=source).translatedText
        except:
            english = desc
            farsi = desc

        msg = f"""⭕️ عاجل | {title}

🚨 English: Urgent: {english}

🚨 فارسی: فوری: {farsi}
"""

        send_telegram(msg)

        count += 1
        time.sleep(1)

    print("DONE:", url)

# =======================
# تشغيل كل المصادر
# =======================
for x in secs[1:]:
    tran(x)

# حفظ md5 في الملف
with open('test.ini', 'w') as f:
    config.write(f)
