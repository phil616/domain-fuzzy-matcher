#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核心域名模糊匹配算法模块

实现了基于多种相似度算法的域名模糊匹配功能，包括：
- 编辑距离（Levenshtein Distance）
- 键盘物理距离
- 发音相似性
- 综合评分算法

Author: @phil616
Date: 2025-8-11
License: MIT
"""

from typing import List, Tuple, Dict, Optional
import math
from .keyboard import KeyboardDistance
from .phonetic import PhoneticSimilarity
from .utils import (
    normalize_domain, levenshtein_similarity, jaro_winkler_similarity,
    calculate_length_penalty, normalize_score
)


class DomainMatcher:
    """企业域名模糊匹配器
    
    集成多种相似度算法，为用户输入的错误域名找到最佳匹配。
    
    算法原理:
    最终得分 = α × 编辑距离得分 + β × 键盘距离得分 + γ × 发音相似度得分 - δ × 长度惩罚
    
    其中:
    - α: 编辑距离权重 (默认0.4)
    - β: 键盘距离权重 (默认0.4) 
    - γ: 发音相似度权重 (默认0.2)
    - δ: 长度惩罚权重 (默认0.1)
    """
    
    def __init__(self, 
                 edit_weight: float = 0.4,
                 keyboard_weight: float = 0.4,
                 phonetic_weight: float = 0.2,
                 length_penalty_weight: float = 0.1,
                 use_jaro_winkler: bool = True):
        """初始化域名匹配器
        
        :param edit_weight: 编辑距离权重
        :type edit_weight: float
        :param keyboard_weight: 键盘距离权重
        :type keyboard_weight: float
        :param phonetic_weight: 发音相似度权重
        :type phonetic_weight: float
        :param length_penalty_weight: 长度惩罚权重
        :type length_penalty_weight: float
        :param use_jaro_winkler: 是否使用Jaro-Winkler算法替代简单编辑距离
        :type use_jaro_winkler: bool
        """
        # 权重参数
        self.edit_weight = edit_weight
        self.keyboard_weight = keyboard_weight
        self.phonetic_weight = phonetic_weight
        self.length_penalty_weight = length_penalty_weight
        self.use_jaro_winkler = use_jaro_winkler
        
        # 验证权重总和
        total_weight = edit_weight + keyboard_weight + phonetic_weight
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"权重总和应该为1.0，当前为{total_weight}")
        
        # 初始化子模块
        self.keyboard_calc = KeyboardDistance()
        self.phonetic_calc = PhoneticSimilarity()
        
        # 标准域名列表
        self.standard_domains: List[str] = []
        
        # 缓存计算结果
        self._similarity_cache: Dict[Tuple[str, str], float] = {}
    
    def add_domains(self, domains: List[str]) -> None:
        """添加标准域名列表
        
        :param domains: 标准域名列表
        :type domains: List[str]
        """
        for domain in domains:
            normalized = normalize_domain(domain)
            if normalized and normalized not in self.standard_domains:
                self.standard_domains.append(normalized)
        
        # 清空缓存
        self._similarity_cache.clear()
    
    def remove_domain(self, domain: str) -> bool:
        """移除指定的标准域名
        
        :param domain: 要移除的域名
        :type domain: str
        :return: 是否成功移除
        :rtype: bool
        """
        normalized = normalize_domain(domain)
        if normalized in self.standard_domains:
            self.standard_domains.remove(normalized)
            self._similarity_cache.clear()
            return True
        return False
    
    def clear_domains(self) -> None:
        """清空所有标准域名"""
        self.standard_domains.clear()
        self._similarity_cache.clear()
    
    def get_domains(self) -> List[str]:
        """获取当前的标准域名列表
        
        :return: 标准域名列表
        :rtype: List[str]
        """
        return self.standard_domains.copy()
    
    def calculate_similarity(self, input_domain: str, target_domain: str) -> float:
        """计算两个域名之间的综合相似度
        
        :param input_domain: 用户输入的域名
        :type input_domain: str
        :param target_domain: 目标标准域名
        :type target_domain: str
        :return: 综合相似度分数 (0-1之间)
        :rtype: float
        """
        # 标准化输入
        input_norm = normalize_domain(input_domain)
        target_norm = normalize_domain(target_domain)
        
        if not input_norm or not target_norm:
            return 0.0
        
        if input_norm == target_norm:
            return 1.0
        
        # 检查缓存
        cache_key = (input_norm, target_norm)
        if cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]
        
        # 1. 计算编辑距离相似度
        if self.use_jaro_winkler:
            edit_sim = jaro_winkler_similarity(input_norm, target_norm)
        else:
            edit_sim = levenshtein_similarity(input_norm, target_norm)
        
        # 2. 计算键盘物理距离相似度
        keyboard_sim = self.keyboard_calc.get_string_similarity(input_norm, target_norm)
        
        # 3. 计算发音相似度
        phonetic_sim = self.phonetic_calc.get_string_similarity(input_norm, target_norm)
        
        # 4. 计算长度惩罚
        length_penalty = calculate_length_penalty(input_norm, target_norm)
        
        # 5. 综合计算最终得分
        final_score = (
            self.edit_weight * edit_sim +
            self.keyboard_weight * keyboard_sim +
            self.phonetic_weight * phonetic_sim -
            self.length_penalty_weight * length_penalty
        )
        
        # 标准化到0-1范围
        final_score = normalize_score(final_score, 0.0, 1.0)
        
        # 缓存结果
        self._similarity_cache[cache_key] = final_score
        
        return final_score
    
    def match(self, input_domain: str, 
              threshold: float = 0.6, 
              max_results: int = 10) -> List[Tuple[str, float]]:
        """对输入域名进行模糊匹配
        
        :param input_domain: 用户输入的域名
        :type input_domain: str
        :param threshold: 匹配阈值，低于此值的结果将被过滤
        :type threshold: float
        :param max_results: 最大返回结果数量
        :type max_results: int
        :return: 匹配结果列表，每个元素为(域名, 相似度)的元组
        :rtype: List[Tuple[str, float]]
        """
        if not input_domain or not self.standard_domains:
            return []
        
        input_norm = normalize_domain(input_domain)
        if not input_norm:
            return []
        
        # 计算与所有标准域名的相似度
        results = []
        for target_domain in self.standard_domains:
            similarity = self.calculate_similarity(input_norm, target_domain)
            if similarity >= threshold:
                results.append((target_domain, similarity))
        
        # 按相似度降序排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        # 限制返回数量
        return results[:max_results]
    
    def get_best_match(self, input_domain: str, 
                       threshold: float = 0.6) -> Optional[Tuple[str, float]]:
        """获取最佳匹配结果
        
        :param input_domain: 用户输入的域名
        :type input_domain: str
        :param threshold: 匹配阈值
        :type threshold: float
        :return: 最佳匹配结果，格式为(域名, 相似度)，如果没有匹配则返回None
        :rtype: Optional[Tuple[str, float]]
        """
        matches = self.match(input_domain, threshold, max_results=1)
        return matches[0] if matches else None
    
    def should_redirect(self, input_domain: str, 
                       redirect_threshold: float = 0.8) -> Optional[str]:
        """判断是否应该自动重定向
        
        当最佳匹配的相似度超过重定向阈值时，返回重定向目标。
        
        :param input_domain: 用户输入的域名
        :type input_domain: str
        :param redirect_threshold: 自动重定向阈值
        :type redirect_threshold: float
        :return: 重定向目标域名，如果不应该重定向则返回None
        :rtype: Optional[str]
        """
        best_match = self.get_best_match(input_domain, threshold=0.0)
        
        if best_match and best_match[1] >= redirect_threshold:
            return best_match[0]
        
        return None
    
    def analyze_input(self, input_domain: str) -> Dict[str, any]:
        """分析用户输入，提供详细的匹配信息
        
        :param input_domain: 用户输入的域名
        :type input_domain: str
        :return: 分析结果字典
        :rtype: Dict[str, any]
        """
        input_norm = normalize_domain(input_domain)
        
        analysis = {
            'original_input': input_domain,
            'normalized_input': input_norm,
            'input_length': len(input_norm),
            'matches': [],
            'best_match': None,
            'should_redirect': False,
            'redirect_target': None,
            'analysis_details': {
                'keyboard_analysis': {},
                'phonetic_analysis': {},
                'potential_typos': []
            }
        }
        
        if not input_norm:
            return analysis
        
        # 获取匹配结果
        matches = self.match(input_norm, threshold=0.1, max_results=10)
        analysis['matches'] = matches
        
        if matches:
            analysis['best_match'] = matches[0]
            
            # 判断是否应该重定向
            redirect_target = self.should_redirect(input_norm)
            if redirect_target:
                analysis['should_redirect'] = True
                analysis['redirect_target'] = redirect_target
        
        # 详细分析
        if matches:
            best_target = matches[0][0]
            
            # 键盘分析
            keyboard_sim = self.keyboard_calc.get_string_similarity(input_norm, best_target)
            analysis['analysis_details']['keyboard_analysis'] = {
                'similarity': keyboard_sim,
                'adjacent_chars': []
            }
            
            # 发音分析
            phonetic_sim = self.phonetic_calc.get_string_similarity(input_norm, best_target)
            phonetic_pattern = self.phonetic_calc.analyze_phonetic_pattern(input_norm)
            analysis['analysis_details']['phonetic_analysis'] = {
                'similarity': phonetic_sim,
                'pattern': phonetic_pattern
            }
        
        return analysis
    
    def batch_match(self, input_domains: List[str], 
                   threshold: float = 0.6) -> Dict[str, List[Tuple[str, float]]]:
        """批量匹配多个域名
        
        :param input_domains: 用户输入的域名列表
        :type input_domains: List[str]
        :param threshold: 匹配阈值
        :type threshold: float
        :return: 批量匹配结果字典
        :rtype: Dict[str, List[Tuple[str, float]]]
        """
        results = {}
        for domain in input_domains:
            results[domain] = self.match(domain, threshold)
        return results
    
    def update_weights(self, edit_weight: Optional[float] = None,
                      keyboard_weight: Optional[float] = None,
                      phonetic_weight: Optional[float] = None,
                      length_penalty_weight: Optional[float] = None) -> None:
        """更新算法权重参数
        
        :param edit_weight: 编辑距离权重
        :type edit_weight: Optional[float]
        :param keyboard_weight: 键盘距离权重
        :type keyboard_weight: Optional[float]
        :param phonetic_weight: 发音相似度权重
        :type phonetic_weight: Optional[float]
        :param length_penalty_weight: 长度惩罚权重
        :type length_penalty_weight: Optional[float]
        """
        if edit_weight is not None:
            self.edit_weight = edit_weight
        if keyboard_weight is not None:
            self.keyboard_weight = keyboard_weight
        if phonetic_weight is not None:
            self.phonetic_weight = phonetic_weight
        if length_penalty_weight is not None:
            self.length_penalty_weight = length_penalty_weight
        
        # 验证权重总和
        total_weight = self.edit_weight + self.keyboard_weight + self.phonetic_weight
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"权重总和应该为1.0，当前为{total_weight}")
        
        # 清空缓存
        self._similarity_cache.clear()
    
    def get_statistics(self) -> Dict[str, any]:
        """获取匹配器统计信息
        
        :return: 统计信息字典
        :rtype: Dict[str, any]
        """
        return {
            'total_domains': len(self.standard_domains),
            'cache_size': len(self._similarity_cache),
            'weights': {
                'edit_weight': self.edit_weight,
                'keyboard_weight': self.keyboard_weight,
                'phonetic_weight': self.phonetic_weight,
                'length_penalty_weight': self.length_penalty_weight
            },
            'use_jaro_winkler': self.use_jaro_winkler,
            'domains': self.standard_domains.copy()
        }