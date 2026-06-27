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
    # Googleニュース(検索クエリ形式): トピックページ形式(/section/topic/...)は
    # 内部的にハッシュ化URLへリダイレクトされ不安定なため、
    # 確実に動作する検索クエリ形式(/rss/search?q=...)を使う。
    {
        "name": "Googleニュース 政治",
        "url": "https://news.google.com/rss/search?q=%E6%94%BF%E6%B2%BB&hl=ja&gl=JP&ceid=JP:ja",
    },
    # トピックページ形式: 検索クエリ形式よりノイズが少なく主要記事中心になりやすいため、
    # 動いていれば優先的にこちらも併用する(フォールバック方式)
    {
        "name": "Googleニュース 政治(トピック)",
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
    # Googleニュース(検索クエリ形式): トピックページ形式は内部的に
    # ハッシュ化URLへリダイレクトされ不安定なため、検索クエリ形式を使う。
    # 「市場」は曖昧で関係ない記事(スポーツの移籍市場等)が混入しやすいため、
    # より経済特有の語「日銀」を使う。
    {
        "name": "Googleニュース 経済",
        "url": "https://news.google.com/rss/search?q=%E7%B5%8C%E6%B8%88&hl=ja&gl=JP&ceid=JP:ja",
    },
    {
        "name": "Googleニュース 日銀",
        "url": "https://news.google.com/rss/search?q=%E6%97%A5%E9%8A%80&hl=ja&gl=JP&ceid=JP:ja",
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
    "株価", "日経平均", "為替", "ドル円", "円安", "円高", "FRB", "FOMC",
    "中国経済", "米経済", "貿易", "関税", "輸出", "輸入", "雇用統計",
    "賃金", "景気", "決算", "ECB", "世界経済", "財務省", "経済対策",
]
# 関連キーワードに一致しても、これらを含む場合は除外する
# (例: 「ベネズエラ国会議長」は「国会」に一致してしまうが日本政治とは無関係。
#  「首相動静」のような実質的に内容のないルーティン記事も除外する)
EXCLUDE_KEYWORDS = [
    # 無関係な海外ニュースの誤検知防止(日本政治とは無関係な文脈で「国会」等が出るケース)
    "ベネズエラ", "地震", "死者", "津波", "台風", "豪雨", "土砂",
    # 内容の薄いルーティン記事
    "動静", "日程",
]
