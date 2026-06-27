# -*- coding: utf-8 -*-
"""
LINE Messaging API で通知を送るモジュール。

事前準備(README参照):
- LINE公式アカウントを作成
- Messaging APIを有効化してチャネルアクセストークンを発行
- GitHub Secretsに LINE_CHANNEL_ACCESS_TOKEN として登録

配信方式について:
- 「ブロードキャスト配信」を使用している(LINE公式アカウントの友だち全員にメッセージを送る方式)。
- このアカウントの友だちは自分一人だけなので、実質的に自分専用の通知になる。
- ユーザーID(LINE_USER_ID)の取得が不要になるメリットがある一方、
  もし将来このアカウントに他の人を友だち追加すると、その人にも同じ通知が届く点に注意。
- ブロードキャストには無料枠の上限がある(プランによる)。超えた場合は送信が失敗するので、
  send_text()の戻り値(成功/失敗)をログで確認すること。

LINE Notifyは2025年3月末に終了しているため、後継のMessaging APIを使う。
"""
from __future__ import annotations

import os
import sys

import requests

LINE_BROADCAST_URL = "https://api.line.me/v2/bot/message/broadcast"
MAX_TEXT_LENGTH = 4900  # LINEの1メッセージあたりの上限(5000文字)に少し余裕を持たせる


def _get_credentials() -> str:
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    if not token:
        raise RuntimeError(
            "環境変数 LINE_CHANNEL_ACCESS_TOKEN が設定されていません。"
        )
    return token


def send_text(message: str) -> bool:
    """1件のテキストメッセージを、このアカウントの友だち全員にブロードキャスト送信する。成功時True。"""
    token = _get_credentials()

    if len(message) > MAX_TEXT_LENGTH:
        message = message[:MAX_TEXT_LENGTH] + "\n…(以下省略)"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {
        "messages": [{"type": "text", "text": message}],
    }

    try:
        resp = requests.post(LINE_BROADCAST_URL, headers=headers, json=payload, timeout=10)
        if resp.status_code != 200:
            print(f"[ERROR] LINE送信失敗: status={resp.status_code} body={resp.text}",
                  file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"[ERROR] LINE送信例外: {e}", file=sys.stderr)
        return False


def build_digest_message(politics_articles: list[dict], economy_articles: list[dict],
                          label: str, max_items_per_category: int = 6) -> str:
    """朝/夕のまとめ通知用のテキストを作る。"""
    lines = [f"📰 {label}のニュースまとめ", ""]

    lines.append("【政治】")
    if politics_articles:
        for art in politics_articles[:max_items_per_category]:
            lines.append(f"・{art['title']}（{art['source']}）")
            lines.append(f"  {art['link']}")
    else:
        lines.append("特に大きな動きはありませんでした。")

    lines.append("")
    lines.append("【経済】")
    if economy_articles:
        for art in economy_articles[:max_items_per_category]:
            lines.append(f"・{art['title']}（{art['source']}）")
            lines.append(f"  {art['link']}")
    else:
        lines.append("特に大きな動きはありませんでした。")

    return "\n".join(lines)


def build_breaking_message(article: dict) -> str:
    """速報1件分の通知テキストを作る。"""
    category_label = "政治" if article["category"] == "politics" else "経済"
    lines = [
        f"🚨 速報【{category_label}】",
        article["title"],
        f"（{article['source']} ほか複数ソースが報道）",
        article["link"],
    ]
    return "\n".join(lines)
