# 自分専用ニュース通知ツール

政治（政府・国会の動き）と経済（日本含む世界経済）のニュースをLINEに通知するツールです。

- 朝・夕の2回、まとめて通知（直近12時間分）
- 複数の報道ソースで同時に報じられたニュースは「速報」として即時通知（30分おきにチェック）
- 政治的な偏りを抑えるため、通信社・全国紙・海外メディアを複数ミックスして収集

すべてGitHub Actions上で動くため、自分のPC・スマホは常時起動しておく必要はありません。

---

## 0. 全体の流れ

1. LINE公式アカウントを作る
2. Messaging APIを有効化し、チャネルアクセストークンを取得する
3. 自分のLINEユーザーIDを取得する
4. このリポジトリをGitHubにアップロードする
5. GitHub Secretsに上記の2つの値を登録する
6. ワークフローが自動的に動き出す（手動実行で先に動作確認もできる）

すべてスマホのブラウザから操作可能です。

---

## 1. LINE公式アカウントの作成

1. [LINE Official Account Manager](https://manager.line.biz/) にアクセスし、LINEアカウントでログイン
2. 「アカウントを作成」を選び、名前・業種などを入力（個人利用なので適当な名前でOK）
3. 作成後、「設定」→「Messaging API」を開き、「Messaging APIを利用する」を選択
4. 表示されるQRコードを自分のLINEアプリで読み取り、この公式アカウントを「友だち追加」する
   - ここで友だち追加しておかないと、後でメッセージが届きません

## 2. チャネルアクセストークンの取得

1. [LINE Developers コンソール](https://developers.line.biz/console/) にログイン
2. 先ほど作成したプロバイダー・チャネルを選択
3. 「Messaging API設定」タブを開き、一番下までスクロール
4. 「チャネルアクセストークン（長期）」の「発行」をクリック
5. 表示された文字列をコピーして、メモ帳などに一時的に保存しておく
   - これが `LINE_CHANNEL_ACCESS_TOKEN` になります

## 3. 自分のLINEユーザーIDの取得

1. 同じ「Messaging API設定」タブの中に、ボットの「あなたのユーザーID」という項目があれば、それをコピー
   - 表示されていない場合は、一度LINEアプリから公式アカウントに何かメッセージを送り、
     LINE Developersコンソールの「統計」や「Webhook」のログから確認する方法もあります
   - 確認が難しい場合は、教えてください。一緒に確認します
2. `U` から始まる文字列です。これが `LINE_USER_ID` になります

## 4. GitHubリポジトリの準備

1. GitHubにログイン（アカウントがなければ作成）
2. 「New repository」で新規リポジトリを作成（Public でOK）
3. このフォルダの中身（`.github/`, `src/`, `data/`, `requirements.txt`, `README.md`）を
   そのままアップロードする
   - スマホのブラウザでもGitHub上の「Add file」→「Upload files」からアップロード可能です

## 5. GitHub Secretsの登録

1. 作成したリポジトリの「Settings」→「Secrets and variables」→「Actions」を開く
2. 「New repository secret」を2回押して、以下を登録する
   - `LINE_CHANNEL_ACCESS_TOKEN` : 手順2で取得した値
   - `LINE_USER_ID` : 手順3で取得した値

## 6. 動作確認

1. リポジトリの「Actions」タブを開く
2. 「朝のニュースまとめ通知」を選び、「Run workflow」で手動実行
3. LINEに通知が来れば成功です
4. 同様に「夕方のニュースまとめ通知」「速報ニュースチェック」も手動実行して確認してください

設定後は、何もしなくても自動的に
- 朝7:00 / 夕18:00 にまとめ通知
- 日中30分おきに速報チェック
が動き続けます。

---

## 構成ファイル

```
news-notifier/
├── .github/workflows/
│   ├── morning.yml     # 朝7時のまとめ通知
│   ├── evening.yml     # 夕18時のまとめ通知
│   └── breaking.yml    # 30分おきの速報チェック
├── src/
│   ├── sources.py            # RSSソース一覧・キーワード設定
│   ├── fetcher.py            # RSS取得(フォールバック方式)
│   ├── breaking_detector.py  # 複数ソース同時報道の判定
│   ├── line_notify.py        # LINE Messaging APIへの送信
│   ├── state.py               # 送信済み履歴の管理(重複通知防止)
│   ├── digest_main.py        # 朝/夕まとめ通知の実行スクリプト
│   └── breaking_main.py      # 速報チェックの実行スクリプト
├── data/sent_history.json    # 送信済み記事の履歴(自動更新)
└── requirements.txt
```

## カスタマイズしたくなったら

- **通知時刻を変えたい** → `morning.yml` / `evening.yml` の `cron` の値を変更
  （UTC基準なので JST-9時間で指定）
- **速報チェックの頻度を変えたい** → `breaking.yml` の `cron: "*/30 * * * *"` を変更
- **キーワードを増やしたい/減らしたい** → `src/sources.py` の `POLITICS_KEYWORDS` /
  `ECONOMY_KEYWORDS` を編集
- **ソースを追加/削除したい** → `src/sources.py` の `POLITICS_SOURCES` /
  `ECONOMY_SOURCES` を編集（生きていないURLは自動的に無視されます）
- **速報の判定を厳しく/緩くしたい** → `src/breaking_detector.py` の
  `MIN_KEYWORDS` / `MATCH_RATIO_THRESHOLD` を調整

## 既知の制約・注意点

- RSSのURLはメディア側のサイトリニューアル等で変わることがあります。
  通知が来なくなったソースがあれば `sources.py` を更新してください。
- GitHub Actionsの `schedule` は数分程度の遅延が発生することがあります
  （GitHub側の仕様で、厳密な時刻保証はありません）。
- 速報判定はキーワード一致ベースの簡易ロジックです。誤判定（拾いすぎ/拾えなさすぎ）
  があれば `breaking_detector.py` のしきい値を調整してください。
- Yahoo!ニュースのRSSは「個人利用のみ可・再配信不可」の規約があるため、
  このリストには含めていません。
