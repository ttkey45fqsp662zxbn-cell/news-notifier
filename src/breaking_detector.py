# -*- coding: utf-8 -*-
"""
速報判定モジュール。

方針(シンプル方式):
- 直近の記事群を対象に、見出しからキーワード(名詞っぽい語)を抜き出す。
- 異なる2ソース以上で、十分なキーワードが重複している記事群があれば
  「複数ソースで同時に報じられた」と判定し、速報候補とする。
- 形態素解析にはjanome(pure Python)を使う。MeCab等の外部バイナリ不要で
  GitHub Actions上でも `pip install` だけで動く。
"""
from __future__ import annotations

from itertools import combinations

from janome.tokenizer import Tokenizer

_tokenizer = Tokenizer()

# 一致率の判定に使う最低限のキーワード数・一致率の閾値
MIN_KEYWORDS = 2
MATCH_RATIO_THRESHOLD = 0.5


def extract_keywords(title: str) -> set[str]:
    """見出しから名詞・固有名詞を抜き出す(簡易版)。"""
    keywords = set()
    for token in _tokenizer.tokenize(title):
        pos = token.part_of_speech.split(",")[0]
        if pos == "名詞" and len(token.surface) >= 2:
            keywords.add(token.surface)
    return keywords


def _similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = a & b
    smaller = min(len(a), len(b))
    if smaller == 0:
        return 0.0
    return len(intersection) / smaller


def detect_breaking(articles: list[dict]) -> list[dict]:
    """
    複数ソースで同時に報じられたとみなせる記事クラスタを検出する。

    戻り値は articles のうち、速報条件を満たしたものの代表(最初に見つかった記事)
    のリスト。重複したクラスタは1件にまとめる。
    """
    if len(articles) < 2:
        return []

    enriched = []
    for art in articles:
        kws = extract_keywords(art["title"])
        if len(kws) >= MIN_KEYWORDS:
            enriched.append((art, kws))

    breaking_candidates = []
    used_indices = set()

    for i, j in combinations(range(len(enriched)), 2):
        if i in used_indices or j in used_indices:
            continue
        art_a, kws_a = enriched[i]
        art_b, kws_b = enriched[j]

        # 同じソース同士の一致は「同時報道」の根拠にならないので除外
        if art_a["source"] == art_b["source"]:
            continue

        sim = _similarity(kws_a, kws_b)
        if sim >= MATCH_RATIO_THRESHOLD:
            breaking_candidates.append(art_a)
            used_indices.add(i)
            used_indices.add(j)

    return breaking_candidates
