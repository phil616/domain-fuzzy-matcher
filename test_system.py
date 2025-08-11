#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业域名模糊匹配系统 - 快速测试脚本

这个脚本演示了系统的核心功能，包括:
1. 基本的模糊匹配
2. 多种错误类型的处理
3. 置信度评估
4. 重定向决策

Author: @phil616
Date: 2025-8-11
License: MIT
"""

from domain_matcher import DomainMatcher

def main():
    """主测试函数"""
    print("=== 企业域名模糊匹配系统测试 ===")
    
    # 初始化匹配器
    matcher = DomainMatcher()
    
    # 添加标准域名
    standard_domains = [
        'web', 'api', 'chat', 'mail', 'blog', 'shop', 'admin',
        'login', 'register', 'dashboard', 'support', 'help'
    ]
    
    matcher.add_domains(standard_domains)
    
    print(f"已加载 {len(standard_domains)} 个标准域名")
    print(f"标准域名: {', '.join(standard_domains)}")
    print()
    
    # 测试用例
    test_cases = [
        ('wen', 'web'),      # 键盘相邻错误
        ('aoi', 'api'),      # 键盘相邻错误
        ('chta', 'chat'),    # 字母顺序错误
        ('mial', 'mail'),    # 字母顺序错误
        ('blgo', 'blog'),    # 字母遗漏
        ('shpo', 'shop'),    # 字母遗漏
        ('admni', 'admin'),  # 字母遗漏
        ('logni', 'login'),  # 字母顺序错误
        ('regiter', 'register'),  # 字母遗漏
        ('dashbord', 'dashboard'),  # 字母遗漏
    ]
    
    print("=== 模糊匹配测试 ===")
    correct_predictions = 0
    
    for fuzzy_input, expected in test_cases:
        print(f"\n输入: '{fuzzy_input}' (期望: '{expected}')")
        
        # 获取匹配结果
        matches = matcher.match(fuzzy_input, threshold=0.6)
        
        if matches:
            best_match, confidence = matches[0]
            print(f"最佳匹配: '{best_match}' (置信度: {confidence:.1f}%)")
            
            # 检查是否预测正确
            if best_match == expected:
                print("✓ 预测正确")
                correct_predictions += 1
            else:
                print("✗ 预测错误")
            
            # 重定向建议
            if matcher.should_redirect(fuzzy_input, redirect_threshold=0.8):
                print(f"建议: 自动重定向到 '{best_match}'")
            else:
                print("建议: 显示候选列表供用户选择")
            
            # 显示所有候选
            if len(matches) > 1:
                print("其他候选:")
                for domain, conf in matches[1:3]:  # 显示前3个候选
                    print(f"  - {domain} ({conf:.1f}%)")
        else:
            print("✗ 未找到匹配")
    
    # 统计结果
    accuracy = (correct_predictions / len(test_cases)) * 100
    print(f"\n=== 测试结果 ===")
    print(f"预测准确率: {accuracy:.1f}% ({correct_predictions}/{len(test_cases)})")
    
    # 详细分析示例
    print("\n=== 详细分析示例 ===")
    analysis = matcher.analyze_input('wen')
    print(f"原始输入: '{analysis['original_input']}'")
    print(f"标准化输入: '{analysis['normalized_input']}'")
    if analysis['best_match']:
        print(f"最佳匹配: {analysis['best_match'][0]} ({analysis['best_match'][1]*100:.1f}%)")
    print(f"匹配数量: {len(analysis['matches'])}")
    
    # 统计信息
    print("\n=== 系统统计 ===")
    stats = matcher.get_statistics()
    print(f"标准域名数量: {stats['total_domains']}")
    print(f"缓存大小: {stats['cache_size']}")
    print(f"算法权重: 编辑距离={stats['weights']['edit_weight']:.2f}, 键盘距离={stats['weights']['keyboard_weight']:.2f}, 发音相似={stats['weights']['phonetic_weight']:.2f}")
    
    print("\n=== 测试完成 ===")

if __name__ == '__main__':
    main()