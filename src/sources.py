# -*- coding: utf-8 -*-
"""
RSSソース一覧。

設計方針（フォールバック方式）:
- ここに「候補」となるRSS URLを複数登録しておく。
- 実行時に生死を確認し、生きているものだけを使う。
- URLが死んでいても処理全体は止めない（fetcher.py側でtry/exceptして無視する）。
- メディアによって政治的立場が異なる可能性があるため、
  できるだけ「通信社（共同・時事）」「全国紙・地上波」「海外メディア」を
  バランスよく混ぜる。
- ここはURLが変わりやすい部分なので、通知が来なくなった/明らかに偏った
  場合はこのリストを更新すればよい。

NOTE: 2026年6月時点でURLの生存確認済みのものを優先しているが、
各社サイトのリニューアル等で変わることがあるため、fetcher側で
生死判定ロジックを必ず通すこと。
"""

POLITICS_SOURCES = [
    # 通信社（事実ベース・速報中心）
    {"name": "共同通信", "url": "https://www.kyodo.co.jp/rss/news.rdf"},
    {"name": "時事通信", "url": "https://www.jiji.com/rss/ranking.rdf"},
    # NHK（公共放送）
    {"name": "NHKニュース 主要", "url": "https://www3.nhk.or.jp/rss/news/cat0.xml"},
    {"name": "NHKニュース 主要(代替)", "url": "https://news.web.nhk/n-data/conf/na/rss/cat0.xml"},
    # 全国紙（立場が分かれるため複数混在させる）
    {"name": "朝日新聞", "url": "https://www.asahi.com/rss/asahi/newsheadlines.rdf"},
    {"name": "読売新聞", "url": "https://www.yomiuri.co.jp/rss/feed/yol_top.xml"},
    {"name": "毎日新聞", "url": "https://mainichi.jp/rss/etc/mainichi-flash.rss"},
    {"name": "産経新聞", "url": "https://www.sankei.com/politics/feed/"},
    {"name": "日本経済新聞 政治", "url": "https://www.nikkei.com/rss/news/category/politics.rdf"},
    # Googleニュース(政治カテゴリ): 個別メディアのサイトリニューアルに
    # 左右されにくい安定したフォールバック先として追加
    {
        "name": "Googleニュース 政治",
        "url": "https://news.google.com/news/rss/headlines/section/topic/POLITICS.ja_jp/%E6%94%BF%E6%B2%BB?ned=jp&hl=ja&gl=JP",
    },
]

ECONOMY_SOURCES = [
    {"name": "日本経済新聞 経済", "url": "https://www.nikkei.com/rss/news/category/economy.rdf"},
    {"name": "日本経済新聞 マーケット", "url": "https://www.nikkei.com/rss/news/category/markets.rdf"},
    # NHK経済カテゴリ: サイトリニューアルでカテゴリ番号が変動した形跡があるため、
    # 旧URL(www3)・新URL(news.web.nhk)・想定される番号違い(cat4/cat5)を
    # すべて候補として登録しておく(フォールバック方式で生きているものだけ使われる)
    {"name": "NHKニュース 経済(旧cat5)", "url": "https://www3.nhk.or.jp/rss/news/cat5.xml"},
    {"name": "NHKニュース 経済(旧cat4)", "url": "https://www3.nhk.or.jp/rss/news/cat4.xml"},
    {"name": "NHKニュース 経済(新cat5)", "url": "https://news.web.nhk/n-data/conf/na/rss/cat5.xml"},
    {"name": "NHKニュース 経済(新cat4)", "url": "https://news.web.nhk/n-data/conf/na/rss/cat4.xml"},
    {"name": "共同通信", "url": "https://www.kyodo.co.jp/rss/news.rdf"},
    {"name": "時事通信 経済", "url": "https://www.jiji.com/rss/economy.rdf"},
    # 海外経済（世界経済を含めるため）
    {"name": "Reuters Japan Business", "url": "https://jp.reuters.com/rssFeed/businessNews"},
    {"name": "Bloomberg Japan", "url": "https://www.bloomberg.co.jp/feed/topics/business"},
    {"name": "ロイター(三次配信)", "url": "https://rss.app/feeds/reuters-business.xml"},
    # Googleニュース(ビジネスカテゴリ): 個別メディアのサイトリニューアルに
    # 左右されにくい安定したフォールバック先として追加
    {
        "name": "Googleニュース ビジネス",
        "url": "https://news.google.com/news/rss/headlines/section/topic/BUSINESS.ja_jp/%E3%83%93%E3%82%B8%E3%83%8D%E3%82%B9?ned=jp&hl=ja&gl=JP",
    },
]

ALL_SOURCES = {
    "politics": POLITICS_SOURCES,
    "economy": ECONOMY_SOURCES,
}

# 政治・経済として「関連あり」と判定するキーワード（簡易フィルタ用）
POLITICS_KEYWORDS = [
    "国会", "衆院", "衆議院", "参院", "参議院", "内閣", "首相", "総理",
    "与党", "野党", "自民", "立憲", "公明", "維新", "国民民主", "共産党",
    "法案", "予算案", "閣議", "省庁", "官邸", "選挙", "解散", "改造",
    "外相", "財務相", "防衛相", "大臣", "政府", "政権", "国会議員",
]

ECONOMY_KEYWORDS = [
    "日銀", "金融政策", "金利", "インフレ", "物価", "GDP", "成長率",
    "株価", "日経平均", "為替", "ドル", "円安", "円高", "FRB", "FOMC",
    "中国経済", "米経済", "貿易", "関税", "輸出", "輸入", "雇用統計",
    "賃金", "景気", "決算", "市場", "投資", "ECB", "世界経済",
]
