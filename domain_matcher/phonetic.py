#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发音相似性计算模块

基于中文发音习惯计算字母发音相似度，
用于识别由于发音相似导致的拼写错误。

Author: @phil616
Date: 2025-8-11
License: MIT
"""

from typing import Dict, Set, Tuple
import re


class PhoneticSimilarity:
    """发音相似性计算器
    
    基于中文发音习惯和英文字母的音素相似性计算字符间的发音相似度。
    """
    
    def __init__(self):
        """初始化发音相似性映射表"""
        # 英文字母的音素分类
        self.phoneme_groups: Dict[str, Set[str]] = {
            'plosive': {'p', 'b', 't', 'd', 'k', 'g'},      # 爆破音
            'fricative': {'f', 'v', 's', 'z', 'h'},        # 摩擦音
            'nasal': {'m', 'n'},                            # 鼻音
            'liquid': {'l', 'r'},                           # 流音
            'glide': {'w', 'y'},                            # 滑音
            'vowel': {'a', 'e', 'i', 'o', 'u'},            # 元音
        }
        
        # 基于中文发音习惯的相似字母组
        self.similar_groups: list = [
            # 容易混淆的辅音
            {'b', 'p'},          # 爆破音
            {'d', 't'},          # 爆破音
            {'g', 'k'},          # 爆破音
            {'v', 'w'},          # 唇音
            {'f', 'v'},          # 摩擦音
            {'s', 'z'},          # 摩擦音
            {'c', 's'},          # 摩擦音
            {'j', 'g'},          # 软音
            {'l', 'r'},          # 流音
            {'m', 'n'},          # 鼻音
            
            # 容易混淆的元音
            {'a', 'e'},          # 开口音
            {'i', 'e'},          # 前元音
            {'o', 'u'},          # 后元音
            {'u', 'v'},          # 在中文中u和v发音相似
            
            # 数字发音相似
            {'2', 'to'},         # two
            {'4', 'for'},        # four
            {'8', 'ate'},        # eight
        ]
        
        # 构建相似度映射表
        self.similarity_map: Dict[Tuple[str, str], float] = {}
        self._build_similarity_map()
    
    def _build_similarity_map(self) -> None:
        """构建字符相似度映射表"""
        # 初始化所有字符对的相似度为0
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        for char1 in chars:
            for char2 in chars:
                if char1 == char2:
                    self.similarity_map[(char1, char2)] = 1.0
                else:
                    self.similarity_map[(char1, char2)] = 0.0
        
        # 设置相似组内的相似度
        for group in self.similar_groups:
            group_list = list(group)
            for i, char1 in enumerate(group_list):
                for char2 in group_list[i+1:]:
                    # 同组内字符相似度设为0.8
                    self.similarity_map[(char1, char2)] = 0.8
                    self.similarity_map[(char2, char1)] = 0.8
        
        # 设置同音素类别的中等相似度
        for phoneme_type, chars_set in self.phoneme_groups.items():
            chars_list = list(chars_set)
            for i, char1 in enumerate(chars_list):
                for char2 in chars_list[i+1:]:
                    # 如果还没有更高的相似度，设置为0.4
                    current_sim = self.similarity_map.get((char1, char2), 0.0)
                    if current_sim < 0.4:
                        self.similarity_map[(char1, char2)] = 0.4
                        self.similarity_map[(char2, char1)] = 0.4
    
    def get_similarity(self, char1: str, char2: str) -> float:
        """获取两个字符的发音相似度
        
        :param char1: 第一个字符
        :type char1: str
        :param char2: 第二个字符
        :type char2: str
        :return: 发音相似度 (0-1之间)
        :rtype: float
        """
        if not char1 or not char2:
            return 0.0
        
        key = (char1.lower(), char2.lower())
        return self.similarity_map.get(key, 0.0)
    
    def get_string_similarity(self, str1: str, str2: str) -> float:
        """计算两个字符串的发音相似度
        
        使用动态规划算法，考虑字符的发音相似性。
        
        :param str1: 第一个字符串
        :type str1: str
        :param str2: 第二个字符串
        :type str2: str
        :return: 字符串发音相似度 (0-1之间)
        :rtype: float
        """
        if not str1 or not str2:
            return 0.0
        
        if str1.lower() == str2.lower():
            return 1.0
        
        str1, str2 = str1.lower(), str2.lower()
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
                char1, char2 = str1[i-1], str2[j-1]
                
                if char1 == char2:
                    # 字符完全相同
                    dp[i][j] = dp[i-1][j-1] + 1.0
                else:
                    # 考虑发音相似度
                    phonetic_sim = self.get_similarity(char1, char2)
                    dp[i][j] = max(
                        dp[i-1][j],                    # 删除str1[i-1]
                        dp[i][j-1],                    # 插入str2[j-1]
                        dp[i-1][j-1] + phonetic_sim   # 替换，加权发音相似度
                    )
        
        # 归一化到0-1之间
        max_len = max(len1, len2)
        return dp[len1][len2] / max_len if max_len > 0 else 0.0
    
    def get_phonetically_similar_chars(self, char: str, min_similarity: float = 0.4) -> list:
        """获取与指定字符发音相似的字符列表
        
        :param char: 目标字符
        :type char: str
        :param min_similarity: 最小相似度阈值
        :type min_similarity: float
        :return: 相似字符列表，按相似度降序排列
        :rtype: list
        """
        similar_chars = []
        char_lower = char.lower()
        
        for other_char in 'abcdefghijklmnopqrstuvwxyz0123456789':
            if other_char != char_lower:
                similarity = self.get_similarity(char_lower, other_char)
                if similarity >= min_similarity:
                    similar_chars.append((other_char, similarity))
        
        # 按相似度降序排列
        similar_chars.sort(key=lambda x: x[1], reverse=True)
        return [char for char, _ in similar_chars]
    
    def analyze_phonetic_pattern(self, word: str) -> Dict[str, any]:
        """分析单词的发音模式
        
        :param word: 要分析的单词
        :type word: str
        :return: 发音模式分析结果
        :rtype: Dict[str, any]
        """
        word = word.lower()
        analysis = {
            'length': len(word),
            'vowels': [],
            'consonants': [],
            'phoneme_distribution': {},
            'potential_confusions': []
        }
        
        # 分析元音和辅音
        vowels = set('aeiou')
        for i, char in enumerate(word):
            if char in vowels:
                analysis['vowels'].append((char, i))
            elif char.isalpha():
                analysis['consonants'].append((char, i))
        
        # 统计音素分布
        for phoneme_type, chars_set in self.phoneme_groups.items():
            count = sum(1 for char in word if char in chars_set)
            if count > 0:
                analysis['phoneme_distribution'][phoneme_type] = count
        
        # 找出潜在的混淆字符
        for i, char in enumerate(word):
            similar_chars = self.get_phonetically_similar_chars(char, 0.6)
            if similar_chars:
                analysis['potential_confusions'].append({
                    'position': i,
                    'original': char,
                    'similar': similar_chars[:3]  # 只取前3个最相似的
                })
        
        return analysis