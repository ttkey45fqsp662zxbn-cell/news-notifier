# -*- coding: utf-8 -*-
"""
朝・夕のまとめ通知を実行するメインスクリプト。

実行例:
    python src/digest_main.py --label "朝"
    python src/digest_main.py --label "夕"

GitHub Actionsから1日2回(朝/夕)呼び出される想定。

NOTE: 速報チェックで既に送った記事も、まとめには再度含める。
理由: 速報判定(複数ソース一致)に該当した記事だけ除外すると、その日の主要記事が
「速報で送ったから」という理由でまとめから消えてしまい、「特に大きな動きは
ありませんでした」という実態と異なる表示になることがあったため。
まとめは「直近N時間の主要記事の一覧」として独立して動作させる。
"""
from __future__ import annotations

import argparse
import sys

from fetcher import fetch_recent
from line_notify import build_digest_message, send_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, help="朝 または 夕")
    parser.add_argument("--hours", type=int, default=12, help="何時間前までの記事を対象にするか")
    args = parser.parse_args()

    politics = fetch_recent("politics", hours=args.hours)
    economy = fetch_recent("economy", hours=args.hours)

    message = build_digest_message(politics, economy, label=args.label)
    ok = send_text(message)

    if ok:
        print(f"[INFO] {args.label}のまとめ通知を送信しました"
              f"(政治{len(politics)}件, 経済{len(economy)}件)", file=sys.stderr)
    else:
        print("[ERROR] 通知送信に失敗しました。", file=sys.stderr)


if __name__ == "__main__":
    main()
