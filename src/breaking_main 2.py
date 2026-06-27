# -*- coding: utf-8 -*-
"""
速報チェックを実行するメインスクリプト。

GitHub Actionsから15〜30分おきに呼び出される想定。
「複数ソースで同時に報じられた」記事だけを速報として通知する。
一度通知した記事は再通知しない(state.pyで管理)。
"""
from __future__ import annotations

import sys

from fetcher import fetch_recent
from breaking_detector import detect_breaking
from line_notify import build_breaking_message, send_text
from state import load_history, filter_unsent, mark_as_sent, save_history, prune_history

# 速報判定は直近どれくらいの時間幅で見るか(短すぎると同時報道を捉えにくい)
BREAKING_WINDOW_HOURS = 2


def main():
    history = prune_history(load_history())

    politics = fetch_recent("politics", hours=BREAKING_WINDOW_HOURS)
    economy = fetch_recent("economy", hours=BREAKING_WINDOW_HOURS)

    breaking_politics = detect_breaking(politics)
    breaking_economy = detect_breaking(economy)
    breaking_all = breaking_politics + breaking_economy

    unsent = filter_unsent(breaking_all, history)

    if not unsent:
        print("[INFO] 新規の速報なし。", file=sys.stderr)
        save_history(history)
        return

    sent_articles = []
    for art in unsent:
        message = build_breaking_message(art)
        ok = send_text(message)
        if ok:
            sent_articles.append(art)
            print(f"[INFO] 速報送信: {art['title']}", file=sys.stderr)
        else:
            print(f"[ERROR] 速報送信失敗: {art['title']}", file=sys.stderr)

    history = mark_as_sent(sent_articles, history)
    save_history(history)


if __name__ == "__main__":
    main()
