# -*- coding: utf-8 -*-
"""
送信済み記事の履歴管理。

GitHub Actions はジョブごとに環境が初期化されるステートレスな実行環境なので、
「前回何を送ったか」をリポジトリ内のJSONファイルに保存し、
ワークフロー側でcommit & pushすることで状態を持続させる。

- send済みの記事は (category, link) のハッシュをキーとして記録する。
- 古い記録(48時間より前)は自動的に間引いて、ファイルが肥大化しないようにする。
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
HISTORY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sent_history.json")
RETENTION_HOURS = 48


def _hash_article(article: dict) -> str:
    key = f"{article['category']}::{article['link']}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def load_history() -> dict:
    if not os.path.exists(HISTORY_PATH):
        return {}
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_history(history: dict) -> None:
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def prune_history(history: dict) -> dict:
    cutoff = datetime.now(JST) - timedelta(hours=RETENTION_HOURS)
    pruned = {}
    for h, sent_at_str in history.items():
        try:
            sent_at = datetime.fromisoformat(sent_at_str)
        except Exception:
            continue
        if sent_at >= cutoff:
            pruned[h] = sent_at_str
    return pruned


def filter_unsent(articles: list[dict], history: dict) -> list[dict]:
    """まだ送信していない記事だけを返す。"""
    return [a for a in articles if _hash_article(a) not in history]


def mark_as_sent(articles: list[dict], history: dict) -> dict:
    """送信済みとして履歴に追記する(保存はしない。呼び出し側でsave_historyすること)。"""
    now_str = datetime.now(JST).isoformat()
    for a in articles:
        history[_hash_article(a)] = now_str
    return history
