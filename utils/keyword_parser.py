#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from typing import List, Dict, Any

def parse_keywords(keywords_df):
    """
    キーワードCSVファイルを解析して検索クエリリストを返す

    Args:
        keywords_df: キーワードが含まれるDataFrame

    Returns:
        List[Dict]: 検索クエリ情報のリスト
    """
    search_queries = []

    # 列名が正確に存在するか確認
    required_columns = ["キーワード1", "キーワード2", "演算子"]

    # 列名の確認と正規化
    column_mapping = {}
    df_columns = keywords_df.columns.tolist()

    for req_col in required_columns:
        if req_col in df_columns:
            column_mapping[req_col] = req_col
        else:
            # 列名が異なる場合は位置で判断（A列, B列, D列など）
            if req_col == "キーワード1" and len(df_columns) > 0:
                column_mapping[req_col] = df_columns[0]
            elif req_col == "キーワード2" and len(df_columns) > 1:
                column_mapping[req_col] = df_columns[1]
            elif req_col == "演算子" and len(df_columns) > 3:
                column_mapping[req_col] = df_columns[3]

    # 列が見つからない場合は空のリストを返す
    if len(column_mapping) < 3:
        return []

    # NaN値を空文字列に変換
    df = keywords_df.fillna("")

    for _, row in df.iterrows():
        kw1 = str(row[column_mapping["キーワード1"]]).strip()
        kw2 = str(row[column_mapping["キーワード2"]]).strip()
        operator = str(row[column_mapping["演算子"]]).strip().upper()

        # キーワード1が空の場合はスキップ
        if not kw1:
            continue

        # 検索クエリ構築
        keywords = []
        if kw1:
            keywords.append(kw1)
        if kw2:
            keywords.append(kw2)

        # キーワード3があれば追加（省略可能）
        kw3_col = "キーワード3"
        if kw3_col in df.columns or (len(df_columns) > 2 and df_columns[2]):
            kw3_col = kw3_col if kw3_col in df.columns else df_columns[2]
            kw3 = str(row[kw3_col]).strip()
            if kw3:
                keywords.append(kw3)

        # クエリ構築
        if operator == "AND" or operator == "":
            # ANDの場合はスペースで連結
            query = " ".join(keywords)
        elif operator == "OR":
            # ORの場合は "OR" 演算子を使用
            query = " OR ".join(keywords)
        else:
            # 不明な演算子の場合はANDとして扱う
            query = " ".join(keywords)
            operator = "AND"

        # 検索
        # 検索クエリ情報を追加
        search_queries.append({
            "query": query,
            "operator": operator,
            "keywords": keywords
        })

    return search_queries