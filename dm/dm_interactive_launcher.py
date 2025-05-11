#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

# 相対インポート対応
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger_setup import setup_logger

# ロガー設定
logger = setup_logger(__file__)

class DMInteractiveLauncher:
    """
    DMの送信画面に自動遷移し、手動操作を待機するランチャー
    """

    def __init__(self):
        """初期化処理"""
        self.base_dir = Path(__file__).parent.parent
        self.input_dir = self.base_dir / "input"
        self.dm_dir = self.base_dir / "dm"

        # アカウントリストとDM生成ディレクトリ
        self.accounts_file = self.input_dir / "filtered_accounts.csv"
        self.dm_gen_dir = self.dm_dir / "generated"

        # 現在日時
        self.current_date = datetime.now().strftime("%Y%m%d")

        logger.info(f"DMInteractiveLauncher initialized")

    def launch(self):
        """Playwrightを起動してDM画面に遷移"""
        # アカウントリスト読み込み
        if not self.accounts_file.exists():
            logger.error(f"Accounts file not found: {self.accounts_file}. Run fetch_profiles.py first.")
            return

        try:
            accounts_df = pd.read_csv(self.accounts_file)
            logger.info(f"Loaded {len(accounts_df)} accounts from {self.accounts_file}")
        except Exception as e:
            logger.exception(f"Error loading accounts file: {str(e)}")
            return

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # ヘッドありで実行
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
                self.process_dm_targets(page, accounts_df)
            else:
                logger.error("Login failed or timeout")

            # 最後はブラウザを開いたままにする（手動操作のため）
            input("Press Enter to close browser when finished...")
            browser.close()

    def process_dm_targets(self, page, accounts_df):
        """DMターゲットごとの処理"""
        for i, account in accounts_df.iterrows():
            username = account["username"]
            profile_url = account["url"]

            # DMテンプレートファイルの確認
            dm_file = self.dm_gen_dir / f"{username}_{self.current_date}.txt"
            if dm_file.exists():
                with open(dm_file, "r", encoding="utf-8") as f:
                    dm_content = f.read()

                logger.info(f"Processing DM for @{username}")

                try:
                    # プロフィールページに遷移
                    page.goto(profile_url)
                    logger.info(f"Navigated to profile: {profile_url}")

                    # DMボタンを探す
                    page.wait_for_selector('div[data-testid="primaryColumn"]', timeout=30000)

                    # DMボタンをクリック
                    dm_button = page.query_selector('a[href$="/message"] span span')
                    if dm_button:
                        dm_button.click()
                        logger.info(f"Clicked DM button for @{username}")

                        # DM画面の読み込みを待機
                        page.wait_for_selector('div[data-testid="DMDrawer"]', timeout=30000)

                        # DMテンプレートの内容を表示
                        print("\n" + "="*50)
                        print(f"DM Template for @{username}:")
                        print("-"*50)
                        print(dm_content)
                        print("="*50 + "\n")

                        # 手動操作を待機
                        input(f"Ready to send DM to @{username}. Copy the content, paste it to the message box, and send.\nPress Enter when done or to skip...")

                        # DMを閉じる
                        close_button = page.query_selector('div[data-testid="DMDrawer"] div[role="button"]')
                        if close_button:
                            close_button.click()
                            page.wait_for_timeout(2000)
                    else:
                        logger.warning(f"DM button not found for @{username}")

                except Exception as e:
                    logger.warning(f"Error processing DM for @{username}: {str(e)}")
            else:
                logger.warning(f"DM template not found for @{username}: {dm_file}")


if __name__ == "__main__":
    logger.info("Starting DM Interactive Launcher")
    launcher = DMInteractiveLauncher()
    launcher.launch()
    logger.info("DM Interactive Launcher finished")