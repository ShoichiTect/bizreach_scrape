# Bizreach Scraper

ビズリーチの求職者情報をスクレイピングするためのPythonプログラムです。

## プロジェクト構成

```
bizreach_scraper/
├── src/
│   ├── bizreach_scraper.py  # スクレイピングの主要クラス
│   ├── utils.py             # ユーティリティ関数
│   └── main.py              # CLI実行用エントリーポイント
├── tests/
│   ├── test_bizreach_scraper.py  # スクレイパーのテスト
│   ├── test_utils.py             # ユーティリティ関数のテスト
│   └── run_tests.py              # テスト実行スクリプト
├── data/                     # スクレイピング結果の出力先
└── README.md                 # このファイル
```

## 前提条件

- Python 3.8以上
- Google Chrome

## セットアップ

依存パッケージのインストール

```bash
pip install -r requirements.txt
```

これにより、必要なパッケージ（selenium, pandas, webdriver-manager）がインストールされます。ChromeDriverは自動的にダウンロードされるため、手動でインストールする必要はありません。

## 使用方法

### 1. URLリストファイルの作成

スクレイピングしたい求職者ページのURLを記載したファイルを作成してください。
以下の形式がサポートされています：

- **テキストファイル (.txt)**: URLを1行に1つずつ記載
- **JSONファイル (.json)**: URLの配列または `{"urls": [...]}` 形式

例：
```
https://www.bizreach.jp/company/candidates/12345
https://www.bizreach.jp/company/candidates/67890
```

### 2. スクレイパーの実行

```bash
python src/main.py -u your_username -p your_password -i url_list.txt
```

#### コマンドラインオプション

- `-u`, `--username`: ビズリーチのログインユーザー名/メールアドレス（必須）
- `-p`, `--password`: ビズリーチのログインパスワード（必須）
- `-i`, `--input`: URLリストファイルのパス（必須）
- `-d`, `--driver`: ChromeDriverのパス（省略可、省略すると自動ダウンロードされます）
- `-o`, `--output-dir`: 出力ディレクトリ（デフォルト: ./data）
- `-f`, `--format`: 出力形式 (csv, json, both)（デフォルト: both）
- `-w`, `--wait`: リクエスト間の待機時間（秒）（デフォルト: 3）

### 3. テストの実行

```bash
python tests/run_tests.py
```

## スクレイピングのカスタマイズ

実際のビズリーチのページ構造に合わせて、`bizreach_scraper.py` 内のセレクターを調整する必要があります。
以下のポイントを確認してください：

1. ログインページのフィールドとボタンのセレクター
2. 求職者ページの各要素のセレクター

## 注意事項

- ビズリーチの利用規約に従った使用を心がけてください。
- スクレイピングの頻度が高すぎるとアカウントがブロックされる可能性があります。
- 取得した個人情報の取り扱いには十分注意してください。
