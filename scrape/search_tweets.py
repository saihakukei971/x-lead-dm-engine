#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
from typing import List, Dict, Any, Tuple

# 相対インポート対応
sys.path.append(str(Path(__file__).parent.parent))
from utils.keyword_parser import parse_keywords
from utils.logger_setup import setup_logger
from utils.filename_generator import generate_filename

# ロガー設定
logger = setup_logger(__file__)

class TwitterSearchScraper:
   """
   Twitterの検索結果から投稿者情報を抽出するスクレイパー
   """

   def __init__(self):
       """初期化処理"""
       self.results = []
       self.current_date = datetime.now().strftime("%Y%m%d")
       logger.info(f"TwitterSearchScraper initialized at {self.current_date}")

       # 結果保存用ディレクトリの作成
       self.result_dir = Path(__file__).parent.parent / "result"
       self.result_dir.mkdir(exist_ok=True)

   def start(self):
       """Playwrightを起動してスクレイピングを開始"""
       with sync_playwright() as p:
           browser = p.chromium.launch(headless=False)  # ヘッドありで実行（デバッグ用）
           context = browser.new_context(viewport={"width": 1280, "height": 800})
           page = context.new_page()

           # Twitterのログインページ
           page.goto("https://twitter.com/login")
           logger.info("Navigated to Twitter login page")

           # NOTE: ログイン処理は手動で行う想定
           logger.info("Waiting for manual login (60 seconds)")
           page.wait_for_timeout(60000)  # 1分間待機してログイン

           # ログイン確認
           if "twitter.com/home" in page.url:
               logger.info("Login successful")
               self.search_keywords(page)
           else:
               logger.error("Login failed or timeout")

           browser.close()

   def search_keywords(self, page):
       """キーワードリストで検索実行"""
       keywords_path = Path(__file__).parent.parent / "config" / "keywords.csv"
       logger.info(f"Loading keywords from {keywords_path}")

       try:
           # キーワード解析
           keywords_df = pd.read_csv(keywords_path)
           search_queries = parse_keywords(keywords_df)

           for query_info in search_queries:
               query = query_info["query"]
               operator = query_info["operator"]
               keywords = query_info["keywords"]

               logger.info(f"Searching for: {query} (operator: {operator})")

               # 検索URL生成
               encoded_query = query.replace(' ', '%20').replace('#', '%23')
               search_url = f"https://twitter.com/search?q={encoded_query}&src=typed_query&f=live"

               page.goto(search_url)
               logger.info(f"Navigated to search URL: {search_url}")
               page.wait_for_selector("article", timeout=30000)

               # スクロールして投稿を収集
               self.scroll_and_collect_tweets(page, query, operator, keywords)

               # 結果を保存
               filename = generate_filename(keywords, operator, self.current_date)
               self.save_results(filename, query)

               # APIリミット対策の待機
               logger.info(f"Waiting 10 seconds before next search...")
               page.wait_for_timeout(10000)

       except Exception as e:
           logger.exception(f"Error during keyword search: {str(e)}")

   def scroll_and_collect_tweets(self, page, query, operator, keywords):
       """ページをスクロールして投稿を収集"""
       tweet_count = 0
       previous_height = 0
       max_tweets = 100  # 最大収集数

       while tweet_count < max_tweets:
           # 新しい投稿を取得
           tweets = page.query_selector_all("article")

           for tweet in tweets[tweet_count:]:
               try:
                   # ユーザー名取得
                   username_el = tweet.query_selector('div[data-testid="User-Name"] a')
                   if not username_el:
                       continue

                   username = username_el.get_attribute("href").split("/")[-1]
                   profile_url = f"https://twitter.com/{username}"

                   # ツイートURL取得
                   tweet_url_el = tweet.query_selector('a[href*="/status/"]')
                   tweet_url = f"https://twitter.com{tweet_url_el.get_attribute('href')}" if tweet_url_el else ""

                   # ツイート内容取得
                   tweet_text_el = tweet.query_selector('div[data-testid="tweetText"]')
                   tweet_text = tweet_text_el.inner_text() if tweet_text_el else ""

                   # タイムスタンプ取得
                   time_el = tweet.query_selector("time")
                   timestamp = time_el.get_attribute("datetime") if time_el else ""

                   # 結果に追加
                   self.results.append({
                       "username": username,
                       "url": profile_url,
                       "bio": "",  # fetch_profiles.pyで後から取得
                       "followers": 0,  # fetch_profiles.pyで後から取得
                       "tweet_url": tweet_url,
                       "tweet_content": tweet_text,
                       "tweeted_at": timestamp,
                       "query": query
                   })

                   tweet_count += 1
                   if tweet_count % 10 == 0:
                       logger.info(f"Collected {tweet_count} tweets")

                   if tweet_count >= max_tweets:
                       break

               except Exception as e:
                   logger.warning(f"Error parsing tweet: {str(e)}")

           # スクロール
           current_height = page.evaluate("document.body.scrollHeight")
           if current_height == previous_height:
               break  # スクロールが止まったら終了

           page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
           page.wait_for_timeout(3000)  # スクロール後の読み込み待機
           previous_height = current_height

   def save_results(self, filename, query):
       """収集結果をCSVファイルに保存"""
       # このクエリに関連する結果をフィルタリング
       query_results = [r for r in self.results if r["query"] == query]

       if not query_results:
           logger.warning(f"No results found for query: {query}")
           return

       # 結果をDataFrameに変換
       df = pd.DataFrame(query_results)

       # CSVに保存
       output_path = self.result_dir / filename
       df.to_csv(output_path, index=False, encoding="utf-8")
       logger.info(f"Saved {len(query_results)} results to {output_path}")


if __name__ == "__main__":
   logger.info("Starting Twitter Search Scraper")
   scraper = TwitterSearchScraper()
   scraper.start()
   logger.info("Twitter Search Scraper finished")