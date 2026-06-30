# -*- coding: utf-8 -*-
"""
朝・夕のまとめ通知を実行するメインスクリプト。

実行例:
    python src/digest_main.py --label "朝"
    python src/digest_main.py --label "夕"
    python src/digest_main.py --label "朝" --force   # 時刻チェックを無視して強制実行(動作確認用)

GitHub Actionsから毎時呼び出される想定。
NOTE: GitHub Actionsのschedule(cron)は指定時刻ちょうどに実行される保証がなく、
数十分~数時間ズレることがある(GitHub側の仕様)。そのため「朝7:00」「夕18:00」と
ピンポイントでcronを指定するのではなく、毎時0分に実行されるようにcronを設定し、
このスクリプト側で「現在が朝/夕の対象時間帯かどうか」を判定する方式にしている。
対象時間帯でなければ何もせず終了することで、実行タイミングが多少ズレても
対象の時間帯のどこかで確実に1回処理が走るようにする。

NOTE: 速報チェックで既に送った記事も、まとめには再度含める。
理由: 速報判定(複数ソース一致)に該当した記事だけ除外すると、その日の主要記事が
「速報で送ったから」という理由でまとめから消えてしまい、「特に大きな動きは
ありませんでした」という実態と異なる表示になることがあったため。
まとめは「直近N時間の主要記事の一覧」として独立して動作させる。
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone

from fetcher import fetch_recent
from line_notify import build_digest_message, send_text

JST = timezone(timedelta(hours=9))

# 各ラベルが対象とする時間帯(JST、その時刻ちょうどの「時」を指す)
# 例: 朝→8時台(8:00〜8:59)に実行されたときだけ処理する
TARGET_HOUR = {
    "朝": 8,
    "夕": 18,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, help="朝 または 夕")
    parser.add_argument("--hours", type=int, default=12, help="何時間前までの記事を対象にするか")
    parser.add_argument(
        "--force",
        action="store_true",
        help="時刻チェックを無視して強制的に実行する(動作確認用の手動実行で使う)",
    )
    args = parser.parse_args()

    now_jst = datetime.now(JST)
    target_hour = TARGET_HOUR.get(args.label)

    if not args.force and target_hour is not None and now_jst.hour != target_hour:
        print(
            f"[INFO] 現在{now_jst.hour}時台のため、"
            f"{args.label}(対象は{target_hour}時台)の処理対象外としてスキップします",
            file=sys.stderr,
        )
        return

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
