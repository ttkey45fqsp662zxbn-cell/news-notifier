# -*- coding: utf-8 -*-
"""
LINE Messaging API でプッシュ通知を送るモジュール。

事前準備(README参照):
- LINE公式アカウントを作成
- Messaging APIを有効化してチャネルアクセストークンを発行
- 自分自身のユーザーIDを取得
- 上記2つをGitHub Secretsに LINE_CHANNEL_ACCESS_TOKEN / LINE_USER_ID として登録

LINE Notifyは2025年3月末に終了しているため、後継のMessaging APIを使う。
"""
from __future__ import annotations

import os
import sys

import requests

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
MAX_TEXT_LENGTH = 4900  # LINEの1メッセージあたりの上限(5000文字)に少し余裕を持たせる


def _get_credentials() -> tuple[str, str]:
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")
    if not token or not user_id:
        raise RuntimeError(
            "環境変数 LINE_CHANNEL_ACCESS_TOKEN / LINE_USER_ID が設定されていません。"
        )
    return token, user_id


def send_text(message: str) -> bool:
    """1件のテキストメッセージをLINEに送信する。成功時True。"""
    token, user_id = _get_credentials()

    if len(message) > MAX_TEXT_LENGTH:
        message = message[:MAX_TEXT_LENGTH] + "\n…(以下省略)"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}],
    }

    try:
        resp = requests.post(LINE_PUSH_URL, headers=headers, json=payload, timeout=10)
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
