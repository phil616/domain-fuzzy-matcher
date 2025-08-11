#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业域名模糊匹配系统 - 演示程序

展示系统的各种功能和使用场景。

Author: @phil616
Date: 2025-8-11
License: MIT
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain_matcher import DomainMatcher
import json


def demo_basic_usage():
    """演示基本使用方法"""
    print("=== 基本使用演示 ===")
    
    # 创建匹配器实例
    matcher = DomainMatcher()
    
    # 添加企业标准域名
    standard_domains = [
        'web', 'api', 'chat', 'admin', 'mail', 'blog', 'shop', 'news',
        'forum', 'wiki', 'docs', 'help', 'support', 'login', 'register',
        'dashboard', 'monitor', 'backup', 'cdn', 'static'
    ]
    
    matcher.add_domains(standard_domains)
    print(f"已添加 {len(standard_domains)} 个标准域名")
    
    # 测试各种拼写错误
    test_cases = [
        'wen',      # web的拼写错误（键盘相邻）
        'pai',      # api的拼写错误（字母顺序）
        'caht',     # chat的拼写错误（字母交换）
        'admon',    # admin的拼写错误（字母替换）
        'mial',     # mail的拼写错误（字母交换）
        'blgo',     # blog的拼写错误
        'shpo',     # shop的拼写错误
        'nwes',     # news的拼写错误
        'forun',    # forum的拼写错误
        'weki',     # wiki的拼写错误
    ]
    
    print("\n拼写错误匹配测试:")
    for typo in test_cases:
        matches = matcher.match(typo, threshold=0.3, max_results=3)
        print(f"\n输入: '{typo}'")
        if matches:
            for i, (domain, score) in enumerate(matches, 1):
                print(f"  {i}. {domain} ({score*100:.1f}%)")
            
            # 检查是否应该自动重定向
            redirect = matcher.should_redirect(typo, 0.8)
            if redirect:
                print(f"  -> 建议自动重定向到: {redirect}")
        else:
            print("  -> 无匹配结果")


def demo_detailed_analysis():
    """演示详细分析功能"""
    print("\n\n=== 详细分析演示 ===")
    
    matcher = DomainMatcher()
    matcher.add_domains(['web', 'api', 'chat', 'admin', 'mail'])
    
    # 分析一个拼写错误
    analysis = matcher.analyze_input('wen')
    
    print("\n详细分析结果:")
    print(json.dumps(analysis, ensure_ascii=False, indent=2))


def demo_weight_adjustment():
    """演示权重调整功能"""
    print("\n\n=== 权重调整演示 ===")
    
    # 创建不同权重配置的匹配器
    configs = [
        {
            'name': '平衡配置',
            'edit_weight': 0.4,
            'keyboard_weight': 0.4,
            'phonetic_weight': 0.2
        },
        {
            'name': '键盘优先配置',
            'edit_weight': 0.2,
            'keyboard_weight': 0.6,
            'phonetic_weight': 0.2
        },
        {
            'name': '发音优先配置',
            'edit_weight': 0.3,
            'keyboard_weight': 0.2,
            'phonetic_weight': 0.5
        }
    ]
    
    test_input = 'wen'
    standard_domains = ['web', 'api', 'chat', 'admin']
    
    for config in configs:
        print(f"\n{config['name']}:")
        matcher = DomainMatcher(
            edit_weight=config['edit_weight'],
            keyboard_weight=config['keyboard_weight'],
            phonetic_weight=config['phonetic_weight']
        )
        matcher.add_domains(standard_domains)
        
        matches = matcher.match(test_input, threshold=0.1, max_results=3)
        for domain, score in matches:
            print(f"  {domain}: {score*100:.1f}%")


def demo_batch_processing():
    """演示批量处理功能"""
    print("\n\n=== 批量处理演示 ===")
    
    matcher = DomainMatcher()
    matcher.add_domains(['web', 'api', 'chat', 'admin', 'mail', 'blog', 'shop'])
    
    # 批量处理多个拼写错误
    batch_inputs = ['wen', 'pai', 'caht', 'admon', 'mial', 'blgo', 'shpo']
    
    results = matcher.batch_match(batch_inputs, threshold=0.3)
    
    print("\n批量处理结果:")
    for input_domain, matches in results.items():
        print(f"\n{input_domain}:")
        if matches:
            for domain, score in matches[:2]:  # 只显示前2个结果
                print(f"  -> {domain} ({score*100:.1f}%)")
        else:
            print("  -> 无匹配")


def demo_real_world_scenario():
    """演示真实世界场景"""
    print("\n\n=== 真实场景演示 ===")
    
    # 模拟一个大型企业的域名配置
    enterprise_domains = [
        # 核心服务
        'www', 'api', 'admin', 'dashboard',
        # 用户服务
        'login', 'register', 'profile', 'account',
        # 内容服务
        'blog', 'news', 'wiki', 'docs', 'help',
        # 商务服务
        'shop', 'cart', 'payment', 'order',
        # 通信服务
        'mail', 'chat', 'forum', 'support',
        # 技术服务
        'cdn', 'static', 'upload', 'download',
        # 监控服务
        'monitor', 'status', 'health', 'metrics'
    ]
    
    matcher = DomainMatcher()
    matcher.add_domains(enterprise_domains)
    
    print(f"企业域名配置: {len(enterprise_domains)} 个域名")
    
    # 模拟用户常见的输入错误
    user_errors = [
        ('ww', 'www'),           # 缺少字符
        ('pai', 'api'),          # 字母顺序错误
        ('adimn', 'admin'),      # 字母交换
        ('dashbord', 'dashboard'), # 拼写错误
        ('logni', 'login'),      # 字母交换
        ('regiter', 'register'), # 缺少字符
        ('blgo', 'blog'),        # 字母交换
        ('shpo', 'shop'),        # 字母交换
        ('mial', 'mail'),        # 字母交换
        ('suport', 'support'),   # 缺少字符
    ]
    
    print("\n用户输入错误处理:")
    correct_predictions = 0
    
    for user_input, expected in user_errors:
        best_match = matcher.get_best_match(user_input, threshold=0.3)
        
        print(f"\n用户输入: '{user_input}' (期望: '{expected}')")
        
        if best_match:
            predicted, confidence = best_match
            print(f"系统预测: '{predicted}' (置信度: {confidence*100:.1f}%)")
            
            if predicted == expected:
                correct_predictions += 1
                print("✓ 预测正确")
            else:
                print("✗ 预测错误")
            
            # 检查重定向建议
            redirect = matcher.should_redirect(user_input, 0.8)
            if redirect:
                print(f"建议: 自动重定向到 '{redirect}'")
            elif confidence >= 0.6:
                print(f"建议: 询问用户是否想访问 '{predicted}'")
        else:
            print("系统预测: 无匹配结果")
            print("✗ 预测失败")
    
    accuracy = correct_predictions / len(user_errors) * 100
    print(f"\n预测准确率: {accuracy:.1f}% ({correct_predictions}/{len(user_errors)})")


def demo_performance_comparison():
    """演示性能对比"""
    print("\n\n=== 算法性能对比 ===")
    
    import time
    
    # 创建不同配置的匹配器
    matchers = {
        'Levenshtein': DomainMatcher(use_jaro_winkler=False),
        'Jaro-Winkler': DomainMatcher(use_jaro_winkler=True),
    }
    
    domains = ['web', 'api', 'chat', 'admin', 'mail'] * 10  # 扩大域名列表
    test_inputs = ['wen', 'pai', 'caht', 'admon', 'mial'] * 20  # 扩大测试输入
    
    for name, matcher in matchers.items():
        matcher.add_domains(domains)
        
        start_time = time.time()
        
        for test_input in test_inputs:
            matcher.match(test_input, threshold=0.3)
        
        end_time = time.time()
        elapsed = (end_time - start_time) * 1000  # 转换为毫秒
        
        print(f"{name}: {elapsed:.2f}ms ({len(test_inputs)} 次查询)")
        print(f"  平均每次查询: {elapsed/len(test_inputs):.2f}ms")


def main():
    """主演示函数"""
    print("企业域名模糊匹配系统 - 功能演示")
    print("=" * 50)
    
    try:
        demo_basic_usage()
        demo_detailed_analysis()
        demo_weight_adjustment()
        demo_batch_processing()
        demo_real_world_scenario()
        demo_performance_comparison()
        
        print("\n\n=== 演示完成 ===")
        print("\n系统特性总结:")
        print("1. 多算法融合: 编辑距离 + 键盘物理距离 + 发音相似性")
        print("2. 可配置权重: 根据业务需求调整各算法权重")
        print("3. 智能阈值: 支持匹配阈值和重定向阈值")
        print("4. 批量处理: 支持大规模域名匹配")
        print("5. 详细分析: 提供匹配过程的详细信息")
        print("6. 高性能: 缓存机制和优化算法")
        
    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()