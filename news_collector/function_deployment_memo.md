# Cloud Function 再デプロイ用メモ

このファイルは、課金停止のために一時的に削除された Cloud Function `get-ai-news-and-send-email` を再デプロイするための設定情報です。

## 設定情報

- **関数名 (Function Name):** `get-ai-news-and-send-email`
- **リージョン (Region):** `asia-northeast1`
- **環境 (Environment):** `第2世代 (GEN_2)`
- **トリガー (Trigger):** `HTTP`
- **ランタイム (Runtime):** `python312`
- **エントリーポイント (Entry Point):** `main`
- **ソースディレクトリ (Source Directory):** `news_collector`

## 環境変数 (Environment Variables)

再デプロイ時に、以下の環境変数を設定する必要があります。（値はGCPのSecret Managerやローカルの `.env` ファイルなどで管理してください）

- `GEMINI_API_KEY`
- `LOG_EXECUTION_ID`
- `RECEIVER_EMAIL`
- `SENDER_EMAIL`
- `SENDER_PASSWORD`
- `SMTP_PORT`
- `SMTP_SERVER`

## 再デプロイコマンド例

プロジェクトのルートディレクトリで、以下のコマンドを実行することで再デプロイできます。
環境変数の値は、実際の値に置き換えてください。

```bash
gcloud functions deploy get-ai-news-and-send-email \
  --gen2 \
  --region=asia-northeast1 \
  --runtime=python312 \
  --source=./news_collector \
  --entry-point=main \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars=GEMINI_API_KEY="YOUR_GEMINI_API_KEY",LOG_EXECUTION_ID="true",RECEIVER_EMAIL="RECIPIENT_EMAIL",SENDER_EMAIL="YOUR_GMAIL_ADDRESS",SENDER_PASSWORD="YOUR_APP_PASSWORD",SMTP_PORT="587",SMTP_SERVER="smtp.gmail.com"
```

**注意:** 上記コマンドの `--allow-unauthenticated` は、誰でも関数を呼び出せるようにする設定です。セキュリティ要件に応じて、適切な認証方法に変更してください。