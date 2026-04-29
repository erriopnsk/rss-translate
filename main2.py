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
# 🔥 Telegram Settings
# =======================
TELEGRAM_TOKEN = "8715919493:AAGPmTrIEG-msszdRaO1Ujdr3AogPablXkI"
CHAT_ID = "@Qassamcircler"

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
# 🧠 Clean text system
# =======================
def clean_text(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r'<.*?>', '', text)
    text = text.replace("\r", "")
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

# =======================
# Utils
# =======================
def get_md5_value(src):
    return hashlib.md5(src.encode('utf-8')).hexdigest()

def get_image(item):
    try:
        if item.find("enclosure"):
            return item.find("enclosure").get("url")
    except:
        pass
    return None

# =======================
# Load config
# =======================
with open('test.ini', mode='r') as f:
    ini_data = parse.unquote(f.read())

config = configparser.ConfigParser()
config.read_string(ini_data)
secs = config.sections()

def get_cfg(sec, name):
    return config.get(sec, name).strip('"')

def set_cfg(sec, name, value):
    config[sec][name] = '"%s"' % value

def get_cfg_tra(sec):
    cc = config.get(sec, "action").strip('"')
    if "->" in cc:
        return cc.split('->')[0], cc.split('->')[1]
    return "auto", "zh-CN"

BASE = get_cfg("cfg", 'base')

try:
    os.makedirs(BASE)
except:
    pass

GT = Translate()

# =======================
# MAIN ENGINE
# =======================
def tran(sec):

    url = get_cfg(sec, 'url')
    max_item = int(get_cfg(sec, 'max'))
    source, target = get_cfg_tra(sec)
    old_md5 = get_cfg(sec, 'md5')

    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    xml = request.urlopen(req).read().decode('utf8')

    # 🔥 منع التكرار
    new_md5 = get_md5_value(xml)
    if new_md5 == old_md5:
        return
    set_cfg(sec, 'md5', new_md5)

    soup = BeautifulSoup(xml, "html.parser")
    items = soup.find_all('item')

    count = 0

    for item in items:

        if count >= max_item:
            break

        title = item.find('title')
        desc = item.find('description')

        title = title.text if title else ""
        desc = desc.text if desc else ""

        if len(title.strip()) < 3:
            continue

        # 🔥 translate safely
        try:
            title = GT.translate(title, target=target, source=source).translatedText
            desc = GT.translate(desc, target=target, source=source).translatedText
        except:
            pass

        # 🧠 clean
        msg = clean_text(f"{title}\n\n{desc}")

        # 🚀 send
        send_telegram(msg)

        count += 1

    print("DONE:", url)

# =======================
# RUN ALL SOURCES
# =======================
for x in secs[1:]:
    try:
        tran(x)
    except Exception as e:
        print("Error in", x, e)

with open('test.ini', 'w') as f:
    config.write(f)
