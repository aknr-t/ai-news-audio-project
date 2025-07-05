# AIニュース音声化プロジェクト計画書 (改訂版)

## 1. プロジェクト概要

本プロジェクトは、最新の人工知能に関するニュースを自動で収集し、そのURL一覧をユーザーにメールで通知することを目的とします。ユーザーは受信したURLをNotebookLMに手動で貼り付けることで、ニュースの要約や音声化を行います。

## 2. 主な機能

-   **AIニュースURLの自動収集:** 毎日指定時刻（例: 午前7:00）に、Gemini APIを利用して最新の人工知能に関するニュース記事のURLを自動で収集します。
-   **メール通知:** 収集したニュース記事のURL一覧を、指定のメールアドレスに送信します。

## 3. システム構成

本システムは、PythonスクリプトとGoogle Cloud Platform (GCP) のサービスを連携させて構築します。

```
+-----------------+      (1) Daily Trigger      +-----------------+
|                 | ------------------------> |                 |
|  Cloud Scheduler|                           | Cloud Functions |
|                 | <------------------------ | (Python Script) |
+-----------------+                           +-----------------+
                                                      |
                                                      | (2) Get AI News
                                                      v
                                              +-------------+
                                              |             |
                                              | Gemini API  |
                                              |             |
                                              +-------------+
                                                      |
                                                      | (3) Send Email
                                                      v
                                              +-------------+
                                              |             |
                                              | Email Service |
                                              | (e.g., SMTP) |
                                              +-------------+
```

### 処理フロー

1.  **毎日午前7:00:** Cloud Schedulerがトリガーとなり、Cloud Functions (Pythonスクリプト) を実行します。
2.  **ニュース収集:** PythonスクリプトはGemini APIを呼び出し、最新の人工知能に関するニュース記事のURLを検索・抽出します。
3.  **メール送信:** 収集したURL一覧を整形し、Pythonのメール送信機能（例: `smtplib`）を使用して、ユーザーのメールアドレスに送信します。

## 4. 技術スタック

-   **スクリプト言語:** **Python 3.12**
-   **AIモデル:** **Gemini API** (`gemini-2.5-pro` または `gemini-1.5-pro-latest` など、利用可能な最新のモデル)
-   **メール送信:** Python標準ライブラリ (`smtplib`) または外部メールサービスAPI
-   **クラウドインフラ (GCP):**
    -   スクリプト実行環境: **Cloud Functions** (サーバーレス)
    -   スケジュール実行: **Cloud Scheduler**

## 5. 開発ロードマップ

### フェーズ1: コア機能開発 (Pythonスクリプト)

-   [ ] Gemini APIを使用してAIニュースのURLを収集するPythonスクリプトの作成
-   [ ] 収集したURLを整形し、メール本文を作成する機能の実装
-   [ ] Pythonの `smtplib` を使用してメールを送信する機能の実装 (GmailなどのSMTPサーバーを利用)
-   [ ] ローカル環境でのスクリプトの動作確認

### フェーズ2: GCPへのデプロイと自動化

-   [ ] Cloud FunctionsへのPythonスクリプトのデプロイ
-   [ ] Cloud FunctionsがGemini APIとメール送信サービスにアクセスするためのIAM設定
-   [ ] Cloud Schedulerの設定 (毎日午前7:00にCloud Functionsをトリガー)
-   [ ] デプロイ後の動作確認とエラーハンドリング

## 6. ディレクトリ構成（案）

```
ai-news-audio-project/
├── news_collector/       # ニュース収集スクリプト
│   ├── main.py           # Cloud Functionsのエントリポイント
│   ├── requirements.txt  # 依存ライブラリ
│   └── config.py         # メールアドレスなどの設定 (環境変数で管理推奨)
├── PROJECT_PLAN.md       # このファイル
└── README.md
```