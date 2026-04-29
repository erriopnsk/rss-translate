# coding:utf-8
import configparser
import hashlib
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib import request, parse
from deep_translator import GoogleTranslator

# =======================
# 🔥 Telegram
# =======================
TOKEN = "8715919493:AAGPmTrIEG-msszdRaO1Ujdr3AogPablXkI"
CHAT = "@Qassamcircler"

def send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": CHAT,
            "text": text,
            "disable_web_page_preview": True
        }, timeout=10)
    except:
        pass

# =======================
# تنظيف احترافي
# =======================
def clean(t):
    t = BeautifulSoup(t, "html.parser").text
    t = re.sub(r'http\S+', '', t)
    t = re.sub(r'&quot;|&amp;|&lt;|&gt;', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

def clean_title(t):
    t = clean(t)
    t = re.sub(r'⭕️|🚨|🔴', '', t)
    t = re.sub(r'عاجل\s*\|', '', t)
    return t.strip()

# =======================
# منع تكرار قوي
# =======================
seen = set()

def uid(t):
    return hashlib.md5(t.encode()).hexdigest()

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
# RSS
# =======================
def extract(item):
    title = item.find("title")
    desc = item.find("description")
    content = item.find("content:encoded")

    return (
        title.text if title else "",
        desc.text if desc else "",
        content.text if content else ""
    )

# =======================
# ترجمة محسنة
# =======================
def translate(text):

    try:
        en = GoogleTranslator(source='auto', target='en').translate(text)
    except:
        en = ""

    try:
        fa = GoogleTranslator(source='auto', target='fa').translate(text)
    except:
        fa = ""

    return clean(en), clean(fa)

# =======================
# تحسين صياغة عاجل
# =======================
def format_news(title, desc, content):

    arabic = clean_title(title)

    if desc:
        arabic += " | " + clean(desc)

    if content:
        arabic += " " + clean(content)

    en, fa = translate(arabic)

    # تحسين أسلوب عاجل
    if not arabic.startswith("عاجل"):
        arabic = "عاجل | " + arabic

    msg = f"""🔴 {arabic}

🔴 URGENT | {en}

🔴 فوری | {fa}
"""

    return msg

# =======================
# فلترة ذكية
# =======================
def valid(text):
    if len(text) < 25:
        return False
    if "http" in text and len(text) < 50:
        return False
    return True

# =======================
# تشغيل
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

        title, desc, content = extract(item)

        full = title + desc + content

        if not valid(full):
            continue

        key = uid(full)

        if key in seen:
            continue

        seen.add(key)

        send(format_news(title, desc, content))

        count += 1
        time.sleep(1.0)

# =======================
# تشغيل دائم 24/7
# =======================
while True:
    for sec in secs[1:]:
        try:
            run(sec)
        except:
            pass

    time.sleep(5)
