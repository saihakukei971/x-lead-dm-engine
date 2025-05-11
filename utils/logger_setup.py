#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

def setup_logger(calling_file=None):
    """
    Loguruを使用してロギングを設定する

    Args:
        calling_file: 呼び出し元のファイルパス

    Returns:
        logger: 設定済みのlogger
    """
    # クリア
    logger.remove()

    # 現在の日付を取得
    current_date = datetime.now().strftime("%Y%m%d")

    # 実行ファイルのルートディレクトリを取得
    if calling_file:
        try:
            module_path = Path(calling_file)
            root_dir = module_path.parent.parent
        except Exception:
            root_dir = Path.cwd()
    else:
        root_dir = Path.cwd()

    # ログディレクトリの作成
    log_dir = root_dir / "log" / current_date
    log_dir.mkdir(parents=True, exist_ok=True)

    # ログファイルのパス
    log_file = log_dir / f"{current_date}.log"

    # ロガーの設定
    logger.add(
        sys.stderr,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )

    logger.add(
        log_file,
        rotation="10 MB",  # ログファイルが10MBを超えたらローテーション
        retention="30 days",  # 30日間保存
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG"
    )

    # 呼び出し元のファイル名をログに記録
    if calling_file:
        module_name = Path(calling_file).name
        logger.info(f"Logger initialized for {module_name}")

    return logger