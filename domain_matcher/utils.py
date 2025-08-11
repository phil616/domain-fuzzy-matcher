#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""工具函数模块

提供域名标准化、相似度计算等辅助功能。

Author: @phil616
Date: 2025-8-11
License: MIT
"""

import re
from typing import List, Tuple, Optional
import math


def normalize_domain(domain: str) -> str:
    """标准化域名字符串
    
    移除特殊字符，转换为小写，只保留字母数字和连字符。
    
    :param domain: 原始域名
    :type domain: str
    :return: 标准化后的域名
    :rtype: str
    """
    if not domain:
        return ""
    
    # 转换为小写
    domain = domain.lower().strip()
    
    # 移除协议前缀
    domain = re.sub(r'^https?://', '', domain)
    
    # 移除www前缀
    domain = re.sub(r'^www\.', '', domain)
    
    # 只保留字母、数字和连字符
    domain = re.sub(r'[^a-z0-9-]', '', domain)
    
    # 移除开头和结尾的连字符
    domain = domain.strip('-')
    
    return domain


def extract_subdomain(full_domain: str, level: int = 1) -> str:
    """提取指定级别的子域名
    
    :param full_domain: 完整域名，如 'api.service.example.com'
    :type full_domain: str
    :param level: 要提取的级别 (1=最左边的子域名)
    :type level: int
    :return: 提取的子域名部分
    :rtype: str
    """
    if not full_domain:
        return ""
    
    # 标准化域名
    domain = normalize_domain(full_domain)
    
    # 按点分割
    parts = domain.split('.')
    
    if level <= 0 or level > len(parts):
        return ""
    
    return parts[level - 1]


def levenshtein_distance(s1: str, s2: str) -> int:
    """计算两个字符串的Levenshtein编辑距离
    
    :param s1: 第一个字符串
    :type s1: str
    :param s2: 第二个字符串
    :type s2: str
    :return: 编辑距离
    :rtype: int
    """
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)
    
    if s1 == s2:
        return 0
    
    len1, len2 = len(s1), len(s2)
    
    # 创建距离矩阵
    matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    
    # 初始化第一行和第一列
    for i in range(len1 + 1):
        matrix[i][0] = i
    for j in range(len2 + 1):
        matrix[0][j] = j
    
    # 填充矩阵
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if s1[i-1] == s2[j-1]:
                cost = 0
            else:
                cost = 1
            
            matrix[i][j] = min(
                matrix[i-1][j] + 1,      # 删除
                matrix[i][j-1] + 1,      # 插入
                matrix[i-1][j-1] + cost  # 替换
            )
    
    return matrix[len1][len2]


def levenshtein_similarity(s1: str, s2: str) -> float:
    """计算基于Levenshtein距离的相似度
    
    相似度 = 1 - (编辑距离 / 最大长度)
    
    :param s1: 第一个字符串
    :type s1: str
    :param s2: 第二个字符串
    :type s2: str
    :return: 相似度 (0-1之间)
    :rtype: float
    """
    if not s1 and not s2:
        return 1.0
    
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    
    if max_len == 0:
        return 1.0
    
    return max(0.0, 1.0 - (distance / max_len))


def jaro_winkler_similarity(s1: str, s2: str) -> float:
    """计算Jaro-Winkler相似度
    
    Jaro-Winkler算法对字符串开头的匹配给予更高权重。
    
    :param s1: 第一个字符串
    :type s1: str
    :param s2: 第二个字符串
    :type s2: str
    :return: Jaro-Winkler相似度 (0-1之间)
    :rtype: float
    """
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0
    
    len1, len2 = len(s1), len(s2)
    
    # 计算匹配窗口大小
    match_window = max(len1, len2) // 2 - 1
    if match_window < 0:
        match_window = 0
    
    # 标记匹配的字符
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    
    matches = 0
    transpositions = 0
    
    # 找到匹配的字符
    for i in range(len1):
        start = max(0, i - match_window)
        end = min(i + match_window + 1, len2)
        
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break
    
    if matches == 0:
        return 0.0
    
    # 计算转置次数
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        
        while not s2_matches[k]:
            k += 1
        
        if s1[i] != s2[k]:
            transpositions += 1
        
        k += 1
    
    # 计算Jaro相似度
    jaro = (matches / len1 + matches / len2 + (matches - transpositions / 2) / matches) / 3
    
    # 计算公共前缀长度（最多4个字符）
    prefix_len = 0
    for i in range(min(len1, len2, 4)):
        if s1[i] == s2[i]:
            prefix_len += 1
        else:
            break
    
    # 计算Jaro-Winkler相似度
    return jaro + (0.1 * prefix_len * (1 - jaro))


def calculate_length_penalty(s1: str, s2: str, max_penalty: float = 0.3) -> float:
    """计算长度差异惩罚
    
    长度差异越大，惩罚越大。
    
    :param s1: 第一个字符串
    :type s1: str
    :param s2: 第二个字符串
    :type s2: str
    :param max_penalty: 最大惩罚值
    :type max_penalty: float
    :return: 长度惩罚 (0到max_penalty之间)
    :rtype: float
    """
    if not s1 or not s2:
        return max_penalty
    
    len1, len2 = len(s1), len(s2)
    max_len = max(len1, len2)
    
    if max_len == 0:
        return 0.0
    
    length_diff = abs(len1 - len2)
    penalty_ratio = min(1.0, length_diff / max_len)
    
    return penalty_ratio * max_penalty


def normalize_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """将分数标准化到指定范围
    
    :param score: 原始分数
    :type score: float
    :param min_val: 最小值
    :type min_val: float
    :param max_val: 最大值
    :type max_val: float
    :return: 标准化后的分数
    :rtype: float
    """
    return max(min_val, min(max_val, score))


def generate_typo_variants(word: str, max_variants: int = 10) -> List[str]:
    """生成单词的常见拼写错误变体
    
    :param word: 原始单词
    :type word: str
    :param max_variants: 最大变体数量
    :type max_variants: int
    :return: 拼写错误变体列表
    :rtype: List[str]
    """
    if not word:
        return []
    
    variants = set()
    word = word.lower()
    
    # 1. 字符删除
    for i in range(len(word)):
        variant = word[:i] + word[i+1:]
        if variant and variant != word:
            variants.add(variant)
    
    # 2. 字符插入（插入相邻键盘字符）
    keyboard_neighbors = {
        'a': 'sq', 'b': 'vghn', 'c': 'xdfv', 'd': 'erfcxs', 'e': 'wsdr',
        'f': 'rtgvcd', 'g': 'tyhbvf', 'h': 'yujnbg', 'i': 'ujko', 'j': 'uikmnh',
        'k': 'ijolmj', 'l': 'okp', 'm': 'njk', 'n': 'bhjm', 'o': 'iklp',
        'p': 'ol', 'q': 'wa', 'r': 'edft', 's': 'awedxz', 't': 'rfgy',
        'u': 'yhij', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc', 'y': 'tghu',
        'z': 'asx'
    }
    
    for i in range(len(word) + 1):
        if i < len(word) and word[i] in keyboard_neighbors:
            for neighbor in keyboard_neighbors[word[i]]:
                variant = word[:i] + neighbor + word[i:]
                if variant != word:
                    variants.add(variant)
    
    # 3. 字符替换
    for i in range(len(word)):
        if word[i] in keyboard_neighbors:
            for neighbor in keyboard_neighbors[word[i]]:
                variant = word[:i] + neighbor + word[i+1:]
                if variant != word:
                    variants.add(variant)
    
    # 4. 相邻字符交换
    for i in range(len(word) - 1):
        variant = word[:i] + word[i+1] + word[i] + word[i+2:]
        if variant != word:
            variants.add(variant)
    
    # 限制返回数量
    return list(variants)[:max_variants]


def calculate_confidence_interval(scores: List[float], confidence: float = 0.95) -> Tuple[float, float]:
    """计算分数列表的置信区间
    
    :param scores: 分数列表
    :type scores: List[float]
    :param confidence: 置信水平
    :type confidence: float
    :return: 置信区间 (下界, 上界)
    :rtype: Tuple[float, float]
    """
    if not scores:
        return (0.0, 0.0)
    
    scores = sorted(scores)
    n = len(scores)
    
    if n == 1:
        return (scores[0], scores[0])
    
    # 计算均值和标准差
    mean = sum(scores) / n
    variance = sum((x - mean) ** 2 for x in scores) / (n - 1)
    std_dev = math.sqrt(variance)
    
    # 计算置信区间
    alpha = 1 - confidence
    z_score = 1.96  # 95%置信水平的z分数
    
    margin_of_error = z_score * (std_dev / math.sqrt(n))
    
    lower_bound = max(0.0, mean - margin_of_error)
    upper_bound = min(1.0, mean + margin_of_error)
    
    return (lower_bound, upper_bound)