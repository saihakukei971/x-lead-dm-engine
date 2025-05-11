#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import pandas as pd
from pathlib import Path
from playwright.sync_api import sync_playwright
from typing import List, Dict, Any, Tuple

# 相対インポート対応
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger_setup import setup_logger

# ロガー設定
logger = setup_logger(__file__)

class TwitterProfileScraper:
    """
    Twitterのプロフィール情報を抽出するスクレイパー
    """

    def __init__(self, min_followers=10000):
        """初期化処理"""
        self.min_followers = min_followers
        self.results = []
        logger.info(f"TwitterProfileScraper initialized with min_followers={min_followers}")

        # 入力・出力ディレクトリの設定
        self.base_dir = Path(__file__).parent.parent
        self.result_dir = self.base_dir / "result"
        self.input_dir = self.base_dir / "input"

        # 出力ファイル
        self.output_file = self.input_dir / "filtered_accounts.csv"

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
                self.fetch_profiles(page)
            else:
                logger.error("Login failed or timeout")

            browser.close()

    def fetch_profiles(self, page):
        """結果ファイルから抽出したユーザープロフィールを取得"""
        # 結果ディレクトリ内のCSVファイルを検索
        result_files = list(self.result_dir.glob("*.csv"))

        if not result_files:
            logger.error("No result files found. Run search_tweets.py first.")
            return

        # 収集済みアカウントの重複を避けるための集合
        processed_accounts = set()

        for file_path in result_files:
            logger.info(f"Processing file: {file_path.name}")

            try:
                df = pd.read_csv(file_path)

                # username, url列が存在するか確認
                if "username" not in df.columns or "url" not in df.columns:
                    logger.warning(f"Required columns missing in {file_path.name}")
                    continue

                # 各ユーザーのプロフィールを取得
                for _, row in df.iterrows():
                    username = row["username"]
                    profile_url = row["url"]

                    # 重複チェック
                    if username in processed_accounts:
                        logger.info(f"Skipping already processed account: {username}")
                        continue

                    processed_accounts.add(username)

                    try:
                        # プロフィールページにアクセス
                        page.goto(profile_url)
                        logger.info(f"Visiting profile: {profile_url}")
                        page.wait_for_selector('div[data-testid="primaryColumn"]', timeout=30000)

                        # フォロワー数取得
                        followers_el = page.query_selector('a[href$="/followers"] span span')
                        followers_text = followers_el.inner_text() if followers_el else "0"

                        # フォロワー数を数値に変換 (1.5K -> 1500, 1M -> 1000000)
                        followers = self.parse_follower_count(followers_text)

                        # Bio取得
                        bio_el = page.query_selector('div[data-testid="UserDescription"]')
                        bio = bio_el.inner_text() if bio_el else ""

                        # 最小フォロワー数チェック
                        if followers >= self.min_followers:
                            logger.info(f"@{username} | Followers: {followers} → Added")
                            self.results.append({
                                "username": username,
                                "url": profile_url,
                                "bio": bio,
                                "followers": followers
                            })
                        else:
                            logger.info(f"@{username} | Followers: {followers} → Skipped (below minimum)")

                        # API制限対策の待機
                        page.wait_for_timeout(3000)

                    except Exception as e:
                        logger.warning(f"Error fetching profile for {username}: {str(e)}")

            except Exception as e:
                logger.exception(f"Error processing file {file_path.name}: {str(e)}")

        # 結果を保存
        self.save_results()

    def parse_follower_count(self, count_text):
        """フォロワー数のテキスト表記を数値に変換"""
        count_text = count_text.replace(",", "")

        try:
            if "K" in count_text:
                return int(float(count_text.replace("K", "")) * 1000)
            elif "M" in count_text:
                return int(float(count_text.replace("M", "")) * 1000000)
            else:
                return int(count_text)
        except ValueError:
            logger.warning(f"Could not parse follower count: {count_text}")
            return 0

    def save_results(self):
        """収集結果をCSVファイルに保存"""
        if not self.results:
            logger.warning("No profiles matching criteria were found")
            return

        # 結果をDataFrameに変換
        df = pd.DataFrame(self.results)

        # フォロワー数で降順ソート
        df = df.sort_values("followers", ascending=False)

        # CSVに保存
        df.to_csv(self.output_file, index=False, encoding="utf-8")
        logger.info(f"Saved {len(self.results)} filtered accounts to {self.output_file}")


if __name__ == "__main__":
    logger.info("Starting Twitter Profile Scraper")
    scraper = TwitterProfileScraper(min_followers=10000)  # 最小フォロワー数10,000
    scraper.start()
    logger.info("Twitter Profile Scraper finished")