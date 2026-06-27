# -*- coding: utf-8 -*-
"""
朝・夕のまとめ通知を実行するメインスクリプト。

実行例:
    python src/digest_main.py --label "朝"
    python src/digest_main.py --label "夕"

GitHub Actionsから1日2回(朝/夕)呼び出される想定。
速報で既に送った記事は、まとめの対象から除外する(二重通知を避けるため)。
"""
from __future__ import annotations

import argparse
import sys

from fetcher import fetch_recent
from line_notify import build_digest_message, send_text
from state import load_history, filter_unsent, mark_as_sent, save_history, prune_history


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, help="朝 または 夕")
    parser.add_argument("--hours", type=int, default=12, help="何時間前までの記事を対象にするか")
    args = parser.parse_args()

    history = prune_history(load_history())

    politics = fetch_recent("politics", hours=args.hours)
    economy = fetch_recent("economy", hours=args.hours)

    # 速報で既に送信済みの記事はまとめから除外する
    politics_unsent = filter_unsent(politics, history)
    economy_unsent = filter_unsent(economy, history)

    if not politics_unsent and not economy_unsent:
        print("[INFO] 新規記事なし。通知はスキップします。", file=sys.stderr)
        # 履歴ファイルは(prune結果を反映するため)保存しておく
        save_history(history)
        return

    message = build_digest_message(politics_unsent, economy_unsent, label=args.label)
    ok = send_text(message)

    if ok:
        history = mark_as_sent(politics_unsent, history)
        history = mark_as_sent(economy_unsent, history)
        print(f"[INFO] {args.label}のまとめ通知を送信しました"
              f"(政治{len(politics_unsent)}件, 経済{len(economy_unsent)}件)", file=sys.stderr)
    else:
        print("[ERROR] 通知送信に失敗しました。履歴は更新しません。", file=sys.stderr)

    save_history(history)


if __name__ == "__main__":
    main()
