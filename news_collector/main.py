import warnings
import urllib3.exceptions
warnings.filterwarnings("ignore", category=urllib3.exceptions.NotOpenSSLWarning)

import os
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

# Gemini APIの設定
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.5-pro') # または gemini-1.5-pro-latest

def get_ai_news_urls(query: str) -> list[str]:
    """
    Gemini APIを使用して、指定されたクエリに関するAIニュースのURLを収集します。
    """
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    prompt = f"""
    過去48時間以内に公開された、
    最新の人工知能に関するニュース記事のURLを5つ教えてください。
    
    以下の条件を厳守してください。
    - 各URLは新しい行に記述し、それ以外の情報は含めないでください。
    - URLは必ず有効なもので、直接ニュース記事のページにリンクしていること。
    - リンク切れでないことを確認してください。
    - 信頼できるニュースソース（例: TechCrunch, The Verge, WIRED, Nature, Science, Google AI Blogなど）を優先してください。
    - ニュース記事の要約ページやトップページへのリンクではなく、記事本体への直接リンクにしてください。
    - 記事の公開日が過去48時間以内であることを確認してください。
    
    例：
    https://example.com/news/ai-breakthrough-article-full-text-2025-07-06
    https://another.example.org/article/latest-ai-research-detail-2025-07-06

    クエリ: {query}
    """
    response = gemini_model.generate_content(prompt)
    print(f"Gemini raw response: {response.text}")
    urls = [url.strip() for url in response.text.split('\n') if url.strip().startswith("http")]
    return urls

def main(request):
    """
    Cloud Functionsのエントリポイント。
    AIニュースのURLを収集し、メールで送信します。
    """
    print("--- AIニュース収集処理を開始します ---")
    query = "最新の人工知能 OpenAI NTTデータ ServiceNow Salesforce Gemini Claude"
    print(f"[Step 1/3] Gemini APIからニュースURLを収集します。クエリ: {query}")
    news_urls = get_ai_news_urls(query)

    print(f"[Step 2/3] 収集したURL: {news_urls}")
    print("[Step 3/3] メールを送信します。")
    send_email(news_urls)

    print("--- AIニュース収集処理が完了しました ---")
    return "News collection and email process initiated."

def send_email(news_urls: list[str]):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", 587)) # デフォルトは587 (TLS)

    if not all([sender_email, sender_password, receiver_email, smtp_server]):
        print("Error: Email environment variables are not set.")
        return

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    message["Subject"] = f"最新のAIニュース ({today_str})"

    body = "最新のAIニュースのURLです：\n\n" + "\n".join(news_urls)
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # TLSを有効にする
            server.login(sender_email, sender_password)
            server.send_message(message)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == '__main__':
    # ローカルテスト用
    # 環境変数 GEMINI_API_KEY, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL, SMTP_SERVER, SMTP_PORT を設定してください
    # 例:
    # export GEMINI_API_KEY='YOUR_API_KEY'
    # export SENDER_EMAIL='your_email@example.com'
    # export SENDER_PASSWORD='your_app_password'
    # export RECEIVER_EMAIL='recipient_email@example.com'
    # export SMTP_SERVER='smtp.gmail.com'
    # export SMTP_PORT=587
    
    class MockRequest:
        def __init__(self):
            self.args = {}
            self.json = {}

    main(MockRequest())
