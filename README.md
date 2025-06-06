# Twitter Scraper

効率的なTwitter（X）のスクレイピング、アカウント情報収集、自動DM生成のための包括的ツールセットです。特定のキーワードに基づいたターゲットアカウント発見から、カスタマイズされたDM送信支援までを一貫して実行できます。

## 📋 プロジェクト概要

Twitter Scraperは、マーケティング担当者やリサーチャー向けに設計された高度な情報収集・コミュニケーションツールです。複雑な検索条件でのツイート検索、アカウント情報収集、パーソナライズされたDM作成を自動化し、Twitter上での効率的なアウトリーチ活動を実現します。

## 🛠️ 使用技術

- **Python 3.8+**: コアとなるプログラミング言語
- **Playwright**: Seleniumより高機能なブラウザ自動操作ライブラリ
- **Pandas**: 高速なデータ処理と分析
- **Loguru**: 構造化されたログ記録
- **Pathlib**: クロスプラットフォームのファイルパス操作
- **Rich**: リッチなコンソール出力

## 🔄 処理の流れ

1. **キーワード定義**: CSVファイルで複合的な検索条件を設定
2. **自動ツイート検索**: 設定したキーワードでTwitter検索を実行
3. **アカウント抽出**: 検索結果からユニークなアカウントを抽出
4. **プロフィール情報取得**: 各アカウントの詳細情報を収集
5. **フィルタリング**: フォロワー数などの条件でアカウントを選別
6. **DMテンプレート生成**: カスタマイズされたDMを自動生成
7. **手動確認・送信**: 生成されたDMを確認し手動送信

## ✨ 特徴・工夫した点

- **非同期処理の実装**: Playwrightの非同期APIを活用し、複数アカウントの情報を効率的に処理
- **スマートなレート制限回避**: 動的な待機時間設定によるTwitterのレート制限対策
- **高度なフィルタリングロジック**: フォロワー数、アカウント年齢、投稿頻度による多段階フィルタリング
- **堅牢なエラーハンドリング**: 接続エラーやCloudflareチャレンジに対する自動リカバリー機能
- **構造化されたログシステム**: 日付ごとに整理された詳細なログで全処理を追跡可能
- **柔軟なカスタマイズ**: 設定ファイルベースの簡単なパラメータ調整

## 🔍 主な機能

- **キーワード検索**: 複雑なAND/OR検索条件でTwitter上のツイート収集
- **プロフィール抽出**: ユーザー名、URL、紹介文、フォロワー数を収集
- **DMテンプレート生成**: 収集したアカウント向けにカスタマイズされたDMを自動生成
- **手動DM操作支援**: DMの送信画面に自動遷移して手動操作をサポート
- **詳細ログ記録**: 日付ごとのフォルダ分けされた詳細なログで全処理を追跡

## 🖥️ システム要件

- Python 3.8以上
- Windowsまたは類似環境

## 🚀 インストール方法

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/twitter_scraper.git
cd twitter_scraper

# 依存パッケージをインストール
pip install -r requirements.txt

# Playwrightブラウザをインストール
python -m playwright install chromium
```

## 📝 使用方法

### 1. 検索キーワードの設定

`config/keywords.csv` ファイルを以下の形式で作成します：

* **A列**: キーワード1
* **B列**: キーワード2
* **C列**: キーワード3（オプション）
* **D列**: 演算子（"AND"または"OR"）
* **E列**: メモ（オプション）

例:
```csv
キーワード1,キーワード2,キーワード3,演算子,メモ
東京,ラーメン,,AND,東京ラーメン店情報
大阪,ラーメン,,AND,大阪ラーメン店情報
銀座,グルメ,,OR,高級店情報
六本木,バー,,OR,夜の飲食店
```

* **AND検索**: スペースで区切られたキーワードとして検索（例: "東京 ラーメン"）
* **OR検索**: ORで区切られたキーワードとして検索（例: "銀座 OR グルメ"）

### 2. DMテンプレートの設定

`dm/dm_template.txt` ファイルを編集して、送信したいDMのテンプレートを設定します。以下のプレースホルダーを使用できます：

* `<<username>>`: 対象ユーザーのTwitterユーザー名
* `<<keyword>>`: 検索に使用したキーワード
* `<<campaign_url>>`: キャンペーンURL（ユーザー名付きのリファラルリンクが自動生成されます）

### 3. 実行

すべての処理を順番に実行するには、`launcher/run_all.bat`を実行します：

```bash
cd launcher
run_all.bat
```

または、個別のスクリプトを実行することもできます：

```bash
# キーワード検索のみ実行
python scrape/search_tweets.py

# プロフィール抽出のみ実行
python scrape/fetch_profiles.py

# DMテンプレート生成のみ実行
python dm/generate_dm_template.py

# DM送信画面起動のみ実行
python dm/dm_interactive_launcher.py
```

### 4. 出力ファイル

* **検索結果**: `result/` ディレクトリに `[キーワード]_[日付].csv` 形式で保存
* **フィルタリングされたアカウント**: `input/filtered_accounts.csv` に保存
* **生成されたDM**: `dm/generated/` ディレクトリに各ユーザー向けファイルとして保存

### 5. ログ

すべてのログは `log/[日付]/[日付].log` に記録されます。

## 📂 ファイル構成

```
twitter_scraper/
├── config/            # 設定ファイル
│   └── keywords.csv   # 検索キーワード定義
├── input/             # 入力データ
│   └── accounts.csv   # アカウント情報
├── result/            # 検索結果
├── log/               # ログファイル
├── dm/                # DM関連モジュール
├── scrape/            # スクレイピングモジュール
├── utils/             # ユーティリティ関数
└── launcher/          # 実行スクリプト
```

## 📚 ライブラリと選定理由

| カテゴリ | ライブラリ | 選定理由 |
|---------|-----------|---------|
| 自動操作 | Playwright | Seleniumの上位互換、非同期処理、Cloudflare対策、UI待機機能が優れている |
| ログ記録 | Loguru | 簡潔なAPI、行番号・ファイル名の自動記録、カラー出力、ファイル自動ローテーション |
| データ処理 | Pandas | CSV処理の高速化、集計、欠損値処理の充実した機能 |
| ファイル操作 | Pathlib | OS互換性の高いパス操作、直感的なAPI、Windows環境でも安全 |
| UI表示 | Rich | コンソールでの色分け・表出力 |

## ⚙️ カスタマイズ

### 最小フォロワー数の変更

`scrape/fetch_profiles.py` ファイル内の `min_followers` パラメータを変更します：

```python
scraper = TwitterProfileScraper(min_followers=5000)  # 5000フォロワー以上に変更
```

### キャンペーンURLの変更

`dm/generate_dm_template.py` ファイル内の `campaign_url` 変数を変更します：

```python
self.campaign_url = "https://your-website.com/your-campaign/"
```

## ⚠️ 注意事項

* このツールはTwitter（X）の利用規約の範囲内で使用してください
* DMの自動送信は行わず、手動確認・送信を前提としています
* 実行時にはブラウザが起動し、最初の60秒間で手動ログインが必要です