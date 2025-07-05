import os
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# Gemini APIの設定
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.5-pro') # または gemini-1.5-pro-latest

def get_ai_news_urls(query: str) -> list[str]:
    """
    Gemini APIを使用して、指定されたクエリに関するAIニュースのURLを収集します。
    """
    prompt = f"""
    最新の人工知能に関するニュース記事のURLを5つ教えてください。
    各URLは新しい行に記述し、それ以外の情報は含めないでください。
    例：
    https://example.com/news/ai-breakthrough
    https://another.example.org/article/latest-ai-research

    クエリ: {query}
    """
    response = gemini_model.generate_content(prompt)
    urls = [url.strip() for url in response.text.split('\n') if url.strip().startswith("http")]
    return urls

def main(request):
    """
    Cloud Functionsのエントリポイント。
    AIニュースのURLを収集し、メールで送信します。
    """
    query = "最新の人工知能"
    news_urls = get_ai_news_urls(query)

    # ここにメール送信ロジックを追加
    # 現時点ではURLをログに出力
    print("Collected AI News URLs:")
    for url in news_urls:
        print(url)

    return "News collection and email process initiated."

if __name__ == '__main__':
    # ローカルテスト用
    # 環境変数 GEMINI_API_KEY を設定してください
    # export GEMINI_API_KEY='YOUR_API_KEY'
    
    class MockRequest:
        def __init__(self):
            self.args = {}
            self.json = {}

    main(MockRequest())
