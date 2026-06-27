# -*- coding: utf-8 -*-
"""
RSS取得モジュール。

フォールバック方式:
- sources.py に登録された各URLについて取得を試みる。
- タイムアウトやパースエラーが起きたソースはログに残してスキップし、
  全体の処理は止めない。
- 取得した記事は {title, link, source, published, category} の辞書にして返す。
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timedelta, timezone

import feedparser

from sources import ALL_SOURCES, POLITICS_KEYWORDS, ECONOMY_KEYWORDS, EXCLUDE_KEYWORDS

JST = timezone(timedelta(hours=9))
REQUEST_TIMEOUT = 10  # 秒
USER_AGENT = "Mozilla/5.0 (compatible; PersonalNewsNotifier/1.0)"


def _parse_published(entry) -> datetime:
    """feedparserのentryから公開時刻を取り出す。取れなければ現在時刻扱い。"""
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            try:
                return datetime(*value[:6], tzinfo=timezone.utc).astimezone(JST)
            except Exception:
                pass
    return datetime.now(JST)


def fetch_one_source(source: dict, category: str) -> list[dict]:
    """1つのRSSソースから記事一覧を取得する。失敗時は空リストを返す。"""
    articles: list[dict] = []
    try:
        feed = feedparser.parse(
            source["url"],
            agent=USER_AGENT,
        )
        # bozo=Trueでもentriesが取れる場合があるので、entriesの有無で判定する
        if not feed.entries:
            print(f"[WARN] ソース取得失敗(記事0件): {source['name']} ({source['url']})", file=sys.stderr)
            return []

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if not title or not link:
                continue
            articles.append({
                "title": title,
                "link": link,
                "source": source["name"],
                "published": _parse_published(entry),
                "category": category,
            })
    except Exception as e:
        print(f"[WARN] ソース取得エラー: {source['name']} ({source['url']}) -> {e}", file=sys.stderr)
        return []

    return articles


def fetch_all(category: str) -> list[dict]:
    """指定カテゴリ(politics/economy)の全ソースから記事を集める(フォールバック方式)。"""
    sources = ALL_SOURCES.get(category, [])
    all_articles: list[dict] = []
    alive_count = 0

    for source in sources:
        articles = fetch_one_source(source, category)
        if articles:
            alive_count += 1
            all_articles.extend(articles)
        time.sleep(0.5)  # サーバー負荷軽減のための小休止

    print(f"[INFO] category={category}: {alive_count}/{len(sources)} ソースが生存, "
          f"記事数={len(all_articles)}", file=sys.stderr)
    return all_articles
  

def filter_relevant(articles: list[dict]) -> list[dict]:
    """キーワードフィルタで「政治/経済として関連性が高い」記事だけ残す。

    EXCLUDE_KEYWORDSに一致する記事(無関係な海外ニュースの誤検知、
    内容の薄いルーティン記事など)は、関連キーワードに一致していても除外する。
    """
    result = []
    for art in articles:
        keywords = POLITICS_KEYWORDS if art["category"] == "politics" else ECONOMY_KEYWORDS
        title = art["title"]
        if any(ex in title for ex in EXCLUDE_KEYWORDS):
            continue
        if any(kw in title for kw in keywords):
            result.append(art)
    return result



def fetch_recent(category: str, hours: int = 12) -> list[dict]:
    """直近N時間以内の、関連性フィルタを通過した記事を返す。"""
    articles = fetch_all(category)
    relevant = filter_relevant(articles)
    print(f"[INFO] category={category}: キーワードフィルタ通過={len(relevant)}/{len(articles)}件",
          file=sys.stderr)
    cutoff = datetime.now(JST) - timedelta(hours=hours)
    recent = [a for a in relevant if a["published"] >= cutoff]
    print(f"[INFO] category={category}: 時間フィルタ(直近{hours}時間)通過={len(recent)}/{len(relevant)}件",
          file=sys.stderr)
    # 新しい順に並べる
    recent.sort(key=lambda a: a["published"], reverse=True)
    return recent
