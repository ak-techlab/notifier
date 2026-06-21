import os
import requests
from bs4 import BeautifulSoup
import json

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage
)

# LINE設定
# デバッグ用
# ACCESS_TOKEN = "5S3qGtycjYqkl/x+DNdi7LeTo+PODfdSb5dgsneRnmQOPKQSf/sUpGhkOIWxzemONgj8Mk64bDpEuE9cW+iF1hVCwrjGQ4Wl3kTL9oF+DLR90w2FPC/3x/7wlHkseMMCQ6sztwbVshau2ROPh0z+uwdB04t89/1O/w1cDnyilFU="
# USER_ID = "U6776a321be1193f406c363388bf45485"

# 本番用
ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
USER_ID = os.environ["LINE_USER_ID"]

CACHE_FILE = "events_cache.json"

# スクレイピングURL
url = "https://www.av-event.jp/search/?begin_date=20260510&pref_id=23"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# HTML取得
html = requests.get(url, headers=headers).text

# パース
soup = BeautifulSoup(html, "html.parser")

events = []
print("aaa")

# イベント取得
for item in soup.select(".c-event-item"):

    # タイトル
    title_el = item.select_one(".c-event-item_title a")
    title = title_el.get_text(strip=True) if title_el else ""

    # URL
    link = title_el["href"] if title_el else ""

    if link.startswith("/"):
        link = "https://www.av-event.jp" + link

    # 開催場所
    location = ""

    # 開催日
    date = ""

    details = item.select(".c-event-item_detail")

    for detail in details:

        term_el = detail.select_one(".c-event-item_detail-term")
        desc_el = detail.select_one(".c-event-item_detail-desc")

        if not term_el or not desc_el:
            continue

        term = term_el.get_text(strip=True)
        value = desc_el.get_text(strip=True)

        if "開催場所" in term:
            location = value

        elif "開催日" in term:
            date = value

    events.append({
        "title": title,
        "location": location,
        "date": date,
        "url": link
    })

# =========================
# 前回データ読み込み
# =========================

old_events = []

if os.path.exists(CACHE_FILE):

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        old_events = json.load(f)

# 比較しやすくする
old_urls = {
    event["url"]
    for event in old_events
}

# 新規イベント抽出
new_events = [
    event
    for event in events
    if event["url"] not in old_urls
]

# =========================
# LINE通知
# =========================

if new_events:

    lines = []

    for event in new_events:

        lines.append(
            f"""【新着イベント】
タイトル: {event['title']}
開催日: {event['date']}
場所: {event['location']}
URL:
{event['url']}
"""
        )

    text = "\n-------------------\n".join(lines)

    chunks = [
        text[i:i + 4000]
        for i in range(0, len(text), 4000)
    ]

    messages = [
        TextMessage(text=chunk)
        for chunk in chunks
    ]

    configuration = Configuration(
        access_token=ACCESS_TOKEN
    )

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        line_bot_api.push_message(
            PushMessageRequest(
                to=USER_ID,
                messages=messages[:5]
            )
        )

    print("新規イベント通知完了")

else:
    print("新規イベントなし")

# =========================
# キャッシュ保存
# =========================

with open(CACHE_FILE, "w", encoding="utf-8") as f:

    json.dump(
        events,
        f,
        ensure_ascii=False,
        indent=2
    )