import os
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import feedparser # feedparserモジュールを追加

import warnings
import urllib3.exceptions
warnings.filterwarnings("ignore", category=urllib3.exceptions.NotOpenSSLWarning)

# Gemini APIの設定
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.5-pro') # または gemini-1.5-pro-latest

def is_relevant_by_gemini(title: str, summary: str) -> bool:
    """
    Gemini APIを使用して、ニュース記事がAI関連のトピックに合致するかを判断します。
    """
    prompt = f"""
    以下のニュース記事が、人工知能（AI）または以下の企業（OpenAI, NTTデータ, ServiceNow, Salesforce, Gemini, Claude）に関連する内容であれば「True」を、そうでなければ「False」を返してください。

    記事タイトル: {title}
    記事要約: {summary}

    判断結果: """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip().lower() == "true"
    except Exception as e:
        print(f"Error calling Gemini for relevance check: {e}")
        return False # エラー時は関連なしと判断

def get_filtered_news_from_rss() -> list[dict]:
    """
    RSSフィードからAIニュースのタイトル、URL、公開日を収集し、Geminiでフィルタリングします。
    """
    rss_feeds = [
        "https://techcrunch.com/feed/",
        "https://www.wired.com/feed/rss",
        "https://feeds2.feedburner.com/businessinsider",
        "http://feeds.bbci.co.uk/news/rss.xml?edition=int",
        "https://assets.wor.jp/rss/rdf/nikkei/technology.rdf",
        "https://assets.wor.jp/rss/rdf/yomiuri/science.rdf"
    ]

    news_items = []
    two_days_ago = datetime.datetime.now() - datetime.timedelta(days=2)

    for feed_url in rss_feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                published_time = None
                if hasattr(entry, 'published_parsed'):
                    published_time = datetime.datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed'):
                    published_time = datetime.datetime(*entry.updated_parsed[:6])

                if published_time and published_time > two_days_ago:
                    title = entry.title if hasattr(entry, 'title') else "No Title"
                    link = entry.link if hasattr(entry, 'link') else "No Link"
                    summary = entry.summary if hasattr(entry, 'summary') else ""
                    
                    # Geminiでフィルタリング
                    if is_relevant_by_gemini(title, summary):
                        news_items.append({"title": title, "url": link, "published": published_time})
        except Exception as e:
            print(f"Error processing RSS feed {feed_url}: {e}")

    return news_items

def main(request):
    """
    Cloud Functionsのエントリポイント。
    AIニュースのURLを収集し、メールで送信します。
    """
    print("--- AIニュース収集処理を開始します ---")
    print(f"[Step 1/2] RSSフィードからニュースを収集し、Geminiでフィルタリングします。")
    news_items = get_filtered_news_from_rss()

    print(f"[Step 2/2] 収集したニュースアイテム数: {len(news_items)}")
    print("[Step 3/3] メールを送信します。")
    send_email(news_items)

    print("--- AIニュース収集処理が完了しました ---")
    return "News collection and email process initiated."

def send_email(news_items: list[dict]):
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

    body_content = "最新のAIニュースです：\n\n"
    if news_items:
        for item in news_items:
            body_content += f"タイトル: {item['title']}\nURL: {item['url']}\n公開日: {item['published'].strftime('%Y-%m-%d %H:%M')}\n\n"
    else:
        body_content += "該当するニュースは見つかりませんでした。\n\n"

    message.attach(MIMEText(body_content, "plain"))

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
