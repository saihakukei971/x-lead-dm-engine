#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 相対インポート対応
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger_setup import setup_logger

# ロガー設定
logger = setup_logger(__file__)

class DMTemplateGenerator:
    """
    DMテンプレートを生成して置換する処理
    """

    def __init__(self):
        """初期化処理"""
        self.base_dir = Path(__file__).parent.parent
        self.dm_dir = self.base_dir / "dm"
        self.input_dir = self.base_dir / "input"
        self.result_dir = self.base_dir / "result"

        # テンプレートファイルとアカウントリスト
        self.template_file = self.dm_dir / "dm_template.txt"
        self.accounts_file = self.input_dir / "filtered_accounts.csv"

        # 生成したDMの保存先
        self.output_dir = self.dm_dir / "generated"
        self.output_dir.mkdir(exist_ok=True)

        # キャンペーンURL（実際のプロジェクトでは設定ファイルから読み込むなど）
        self.campaign_url = "https://example.com/campaign/"

        # 現在日時
        self.current_date = datetime.now().strftime("%Y%m%d")

        logger.info(f"DMTemplateGenerator initialized")

    def generate_templates(self):
        """テンプレートを生成して置換処理を行う"""
        # テンプレート読み込み
        if not self.template_file.exists():
            logger.error(f"Template file not found: {self.template_file}")
            return

        with open(self.template_file, "r", encoding="utf-8") as f:
            template_text = f.read()

        logger.info(f"Loaded template from {self.template_file}")

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

        # 結果ファイルからキーワード情報を取得
        keywords_by_username = self.get_keywords_by_username()

        # 各アカウントに対してテンプレート生成
        generated_count = 0

        for _, account in accounts_df.iterrows():
            username = account["username"]

            # キーワード取得（なければデフォルト値）
            keywords = keywords_by_username.get(username, ["一般的な情報"])
            keyword = ", ".join(keywords[:3])  # 最大3つまで

            # テンプレート置換
            dm_text = template_text.replace("<<username>>", username)
            dm_text = dm_text.replace("<<keyword>>", keyword)
            dm_text = dm_text.replace("<<campaign_url>>", f"{self.campaign_url}?ref={username}")

            # 保存
            output_file = self.output_dir / f"{username}_{self.current_date}.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(dm_text)

            generated_count += 1
            if generated_count % 10 == 0:
                logger.info(f"Generated {generated_count} DM templates")

        # 一括ファイルも生成
        all_dms_file = self.output_dir / f"all_dms_{self.current_date}.txt"
        with open(all_dms_file, "w", encoding="utf-8") as f:
            f.write(f"--- 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")
            f.write(f"--- 対象アカウント数: {generated_count} ---\n\n")

            for _, account in accounts_df.iterrows():
                username = account["username"]
                keywords = keywords_by_username.get(username, ["一般的な情報"])
                keyword = ", ".join(keywords[:3])

                dm_text = template_text.replace("<<username>>", username)
                dm_text = dm_text.replace("<<keyword>>", keyword)
                dm_text = dm_text.replace("<<campaign_url>>", f"{self.campaign_url}?ref={username}")

                f.write(f"=== @{username} ===\n\n")
                f.write(dm_text)
                f.write("\n\n-----------------------------------\n\n")

        logger.info(f"Generated {generated_count} individual DM templates")
        logger.info(f"Generated combined DM file: {all_dms_file}")

    def get_keywords_by_username(self):
        """結果ファイルからユーザー名ごとのキーワードリストを取得"""
        result_files = list(self.result_dir.glob("*.csv"))
        keywords_by_username = {}

        for file_path in result_files:
            try:
                # ファイル名からキーワードを抽出
                filename = file_path.stem  # 拡張子を除去
                parts = filename.split("_")
                if len(parts) >= 2:
                    keywords = []
                    for part in parts[:-1]:  # 日付部分を除く
                        if "or" in part:
                            # 'or'で区切られた場合、個別にキーワードとして抽出
                            keywords.extend([k.strip() for k in part.split("or")])
                        elif "+" in part:
                            # '+'で区切られた場合は、ANDの条件なのでそのまま1つのキーワードとして
                            keywords.append(part.replace("+", " AND "))
                        else:
                            keywords.append(part)

                # ファイルから投稿者を抽出
                df = pd.read_csv(file_path)
                if "username" in df.columns:
                    for username in df["username"].unique():
                        if username not in keywords_by_username:
                            keywords_by_username[username] = []
                        for kw in keywords:
                            if kw not in keywords_by_username[username]:
                                keywords_by_username[username].append(kw)

            except Exception as e:
                logger.warning(f"Error processing file {file_path.name}: {str(e)}")

        return keywords_by_username


if __name__ == "__main__":
    logger.info("Starting DM Template Generator")
    generator = DMTemplateGenerator()
    generator.generate_templates()
    logger.info("DM Template Generator finished")