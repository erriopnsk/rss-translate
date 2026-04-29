# coding:utf-8
import configparser
from pygtrans import Translate
from bs4 import BeautifulSoup
import sys
import os
from urllib import request, parse
import urllib
import hashlib

import datetime
import time
from rfeed import *
import feedparser


def get_md5_value(src):
    _m = hashlib.md5()
    _m.update(src.encode('utf-8'))
    return _m.hexdigest()


def getTime(e):
    try:
        struct_time = e.published_parsed
    except:
        struct_time = time.localtime()
    return datetime.datetime(*struct_time[:6])


def getSubtitle(e):
    try:
        sub = e.subtitle
    except:
        sub = ""
    return sub


class GoogleTran:
    def __init__(self, url, source='auto', target='zh-CN'):
        self.url = url
        self.source = source
        self.target = target

        self.d = feedparser.parse(url)
        self.GT = Translate()

    def tr(self, content):
        if self.source == 'proxy':
            return content
        try:
            tt = self.GT.translate(content, target=self.target, source=self.source)
            return tt.translatedText
        except:
            return content

    def get_newconent(self, max=2):
        item_list = []

        if not self.d.entries:
            return ""

        if len(self.d.entries) < max:
            max = len(self.d.entries)

        for entry in self.d.entries[:max]:

            title = getattr(entry, "title", "No Title")
            summary = getattr(entry, "summary", "")

            one = Item(
                title=self.tr(title),
                link=getattr(entry, "link", ""),
                description=self.tr(summary),
                guid=Guid(getattr(entry, "link", "")),
                pubDate=getTime(entry)
            )
            item_list.append(one)

        feed = self.d.feed if hasattr(self.d, "feed") else {}

        title = getattr(feed, "title", "No Title")
        link = getattr(feed, "link", self.url)
        desc = getattr(feed, "subtitle", "")

        newfeed = Feed(
            title=self.tr(title),
            link=link,
            description=self.tr(desc),
            lastBuildDate=datetime.datetime.now(),
            items=item_list
        )

        return newfeed.rss()


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

    if cc == "auto":
        return 'auto', 'zh-CN'
    elif cc == "proxy":
        return 'proxy', 'proxy'
    else:
        return cc.split('->')[0], cc.split('->')[1]


BASE = get_cfg("cfg", 'base')

try:
    os.makedirs(BASE)
except:
    pass


links = []


def tran(sec):
    out_dir = BASE + get_cfg(sec, 'name')
    url = get_cfg(sec, 'url')
    max_item = int(get_cfg(sec, 'max'))
    old_md5 = get_cfg(sec, 'md5')
    source, target = get_cfg_tra(sec)

    global links

    links += [" - %s [%s](%s) -> [%s](%s)\n" % (
        sec, url, url, get_cfg(sec, 'name'), parse.quote(out_dir)
    )]

    GT = GoogleTran(url, target=target, source=source)

    c = GT.get_newconent(max=max_item)

    if not c:
        print("Skip empty feed:", url)
        return

    with open(out_dir, 'w', encoding='utf-8') as f:
        f.write(c)

    print("GT: " + url + " > " + out_dir)


for x in secs[1:]:
    tran(x)
    print(config.items(x))


with open('test.ini', 'w') as configfile:
    config.write(configfile)


def get_idx(l):
    for idx, line in enumerate(l):
        if "## rss translate links" in line:
            return idx + 2


YML = "README.md"

f = open(YML, "r+", encoding="UTF-8")
list1 = f.readlines()

list1 = list1[:get_idx(list1)] + links

f = open(YML, "w+", encoding="UTF-8")
f.writelines(list1)
f.close()
