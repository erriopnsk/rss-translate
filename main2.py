# coding:utf-8
import configparser
from pygtrans import Translate
from bs4 import BeautifulSoup
from urllib import request, parse
import urllib
import hashlib
import os
import requests

# =======================
# 🔥 Telegram Settings
# =======================
TELEGRAM_TOKEN = "PUT_NEW_TOKEN_HERE"
CHAT_ID = "@Qassamcircler"

def send_telegram(text, image=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    try:
        if image:
            requests.post(url + "/sendPhoto", data={
                "chat_id": CHAT_ID,
                "photo": image,
                "caption": text[:1024]
            })
        else:
            requests.post(url + "/sendMessage", data={
                "chat_id": CHAT_ID,
                "text": text
            })
    except Exception as e:
        print("Telegram error:", e)

# =======================
# Utils
# =======================
def get_md5_value(src):
    _m = hashlib.md5()
    _m.update(src.encode('utf-8'))
    return _m.hexdigest()

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
# MAIN FUNCTION
# =======================
def tran(sec):

    out_dir = BASE + get_cfg(sec, 'name')
    url = get_cfg(sec, 'url')
    max_item = int(get_cfg(sec, 'max'))
    source, target = get_cfg_tra(sec)

    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

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

        title = title.text if title else ""
        desc = desc.text if desc else ""

        # translate
        try:
            title = GT.translate(title, target=target, source=source).translatedText
            desc = GT.translate(desc, target=target, source=source).translatedText
        except:
            pass

        img = get_image(item)

        msg = f"{title}\n\n{desc}"

        send_telegram(msg, img)

        count += 1

    print("DONE:", url)

# =======================
# RUN
# =======================
for x in secs[1:]:
    tran(x)

with open('test.ini', 'w') as f:
    config.write(f)
