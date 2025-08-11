#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""键盘物理距离计算模块

基于QWERTY键盘布局计算字符间的物理距离，
用于识别由于键盘相邻按键误触导致的拼写错误。

Author: @phil616
Date: 2025-8-11
License: MIT
"""

import math
from typing import Dict, Tuple


class KeyboardDistance:
    """键盘物理距离计算器
    
    基于标准QWERTY键盘布局计算字符间的物理距离。
    距离越小表示用户越容易误按。
    """
    
    def __init__(self):
        """初始化键盘布局坐标系统"""
        # QWERTY键盘布局坐标 (行, 列)
        self.keyboard_layout: Dict[str, Tuple[int, int]] = {
            # 第一行数字键
            '1': (0, 0), '2': (0, 1), '3': (0, 2), '4': (0, 3), '5': (0, 4),
            '6': (0, 5), '7': (0, 6), '8': (0, 7), '9': (0, 8), '0': (0, 9),
            
            # 第二行字母键
            'q': (1, 0), 'w': (1, 1), 'e': (1, 2), 'r': (1, 3), 't': (1, 4),
            'y': (1, 5), 'u': (1, 6), 'i': (1, 7), 'o': (1, 8), 'p': (1, 9),
            
            # 第三行字母键
            'a': (2, 0), 's': (2, 1), 'd': (2, 2), 'f': (2, 3), 'g': (2, 4),
            'h': (2, 5), 'j': (2, 6), 'k': (2, 7), 'l': (2, 8),
            
            # 第四行字母键
            'z': (3, 0), 'x': (3, 1), 'c': (3, 2), 'v': (3, 3), 'b': (3, 4),
            'n': (3, 5), 'm': (3, 6),
        }
        
        # 预计算所有字符对的距离
        self._distance_cache: Dict[Tuple[str, str], float] = {}
        self._precompute_distances()
    
    def _precompute_distances(self) -> None:
        """预计算所有字符对的欧几里得距离"""
        chars = list(self.keyboard_layout.keys())
        for i, char1 in enumerate(chars):
            for char2 in chars[i:]:
                distance = self._calculate_euclidean_distance(char1, char2)
                self._distance_cache[(char1, char2)] = distance
                self._distance_cache[(char2, char1)] = distance
    
    def _calculate_euclidean_distance(self, char1: str, char2: str) -> float:
        """计算两个字符在键盘上的欧几里得距离
        
        :param char1: 第一个字符
        :type char1: str
        :param char2: 第二个字符
        :type char2: str
        :return: 欧几里得距离
        :rtype: float
        """
        if char1 == char2:
            return 0.0
        
        pos1 = self.keyboard_layout.get(char1.lower())
        pos2 = self.keyboard_layout.get(char2.lower())
        
        if pos1 is None or pos2 is None:
            # 如果字符不在键盘布局中，返回最大距离
            return 10.0
        
        # 计算欧几里得距离
        row_diff = pos1[0] - pos2[0]
        col_diff = pos1[1] - pos2[1]
        return math.sqrt(row_diff ** 2 + col_diff ** 2)
    
    def get_distance(self, char1: str, char2: str) -> float:
        """获取两个字符间的键盘物理距离
        
        :param char1: 第一个字符
        :type char1: str
        :param char2: 第二个字符
        :type char2: str
        :return: 物理距离 (0-10之间)
        :rtype: float
        """
        key = (char1.lower(), char2.lower())
        return self._distance_cache.get(key, 10.0)
    
    def get_similarity(self, char1: str, char2: str) -> float:
        """获取两个字符间的键盘相似度
        
        相似度 = 1 - (距离 / 最大距离)
        
        :param char1: 第一个字符
        :type char1: str
        :param char2: 第二个字符
        :type char2: str
        :return: 相似度 (0-1之间)
        :rtype: float
        """
        distance = self.get_distance(char1, char2)
        max_distance = 10.0  # 键盘上的最大可能距离
        return max(0.0, 1.0 - (distance / max_distance))
    
    def get_string_similarity(self, str1: str, str2: str) -> float:
        """计算两个字符串的键盘相似度
        
        使用动态规划算法，类似于编辑距离，但使用键盘相似度作为权重。
        
        :param str1: 第一个字符串
        :type str1: str
        :param str2: 第二个字符串
        :type str2: str
        :return: 字符串相似度 (0-1之间)
        :rtype: float
        """
        if not str1 or not str2:
            return 0.0
        
        if str1 == str2:
            return 1.0
        
        len1, len2 = len(str1), len(str2)
        
        # 动态规划矩阵
        dp = [[0.0 for _ in range(len2 + 1)] for _ in range(len1 + 1)]
        
        # 初始化边界条件
        for i in range(len1 + 1):
            dp[i][0] = 0.0
        for j in range(len2 + 1):
            dp[0][j] = 0.0
        
        # 填充动态规划矩阵
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if str1[i-1] == str2[j-1]:
                    # 字符相同，继承对角线值并加1
                    dp[i][j] = dp[i-1][j-1] + 1.0
                else:
                    # 字符不同，考虑键盘相似度
                    char_similarity = self.get_similarity(str1[i-1], str2[j-1])
                    dp[i][j] = max(
                        dp[i-1][j],      # 删除str1[i-1]
                        dp[i][j-1],      # 插入str2[j-1]
                        dp[i-1][j-1] + char_similarity  # 替换
                    )
        
        # 归一化到0-1之间
        max_len = max(len1, len2)
        return dp[len1][len2] / max_len if max_len > 0 else 0.0
    
    def get_adjacent_chars(self, char: str, max_distance: float = 1.5) -> list:
        """获取指定字符的相邻字符列表
        
        :param char: 目标字符
        :type char: str
        :param max_distance: 最大距离阈值
        :type max_distance: float
        :return: 相邻字符列表，按距离排序
        :rtype: list
        """
        adjacent = []
        char_lower = char.lower()
        
        for other_char in self.keyboard_layout.keys():
            if other_char != char_lower:
                distance = self.get_distance(char_lower, other_char)
                if distance <= max_distance:
                    adjacent.append((other_char, distance))
        
        # 按距离排序
        adjacent.sort(key=lambda x: x[1])
        return [char for char, _ in adjacent]