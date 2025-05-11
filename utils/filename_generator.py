#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

def generate_filename(keywords, operator, date_str=None):
    """
    キーワードと演算子からファイル名を生成する

    Args:
        keywords: キーワードのリスト
        operator: 演算子 ("AND" または "OR")
        date_str: 日付文字列（デフォルトは現在の日付）

    Returns:
        str: 生成されたファイル名
    """
    if not date_str:
        date_str = datetime.now().strftime("%Y%m%d")

    # キーワードが空の場合は「未指定」とする
    if not keywords:
        return f"未指定_{date_str}.csv"

    # 演算子に応じてキーワードを連結
    if operator.upper() == "AND":
        # ANDの場合は "+" で連結
        keyword_part = "+".join(keywords)
    elif operator.upper() == "OR":
        # ORの場合は "or" で連結
        keyword_part = "or".join(keywords)
    else:
        # 不明な演算子の場合はそのまま連結
        keyword_part = "_".join(keywords)

    # ファイル名として利用できない文字を置換
    keyword_part = keyword_part.replace("/", "_").replace("\\", "_").replace(":", "_")
    keyword_part = keyword_part.replace("*", "_").replace("?", "_").replace("\"", "_")
    keyword_part = keyword_part.replace("<", "_").replace(">", "_").replace("|", "_")

    return f"{keyword_part}_{date_str}.csv"