#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""企业域名模糊匹配系统主程序

提供命令行接口和基本的使用示例。

Author: @phil616
Date: 2025-8-11
License: MIT
"""

import argparse
import json
import sys
from typing import List, Dict, Any
from domain_matcher import DomainMatcher


def load_domains_from_file(file_path: str) -> List[str]:
    """从文件加载标准域名列表
    
    :param file_path: 域名文件路径
    :type file_path: str
    :return: 域名列表
    :rtype: List[str]
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            domains = [line.strip() for line in f if line.strip()]
        return domains
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
        return []
    except Exception as e:
        print(f"错误: 读取文件时出现异常 {e}")
        return []


def save_results_to_file(results: Dict[str, Any], file_path: str) -> bool:
    """将结果保存到JSON文件
    
    :param results: 匹配结果
    :type results: Dict[str, Any]
    :param file_path: 输出文件路径
    :type file_path: str
    :return: 是否保存成功
    :rtype: bool
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"错误: 保存文件时出现异常 {e}")
        return False


def interactive_mode(matcher: DomainMatcher) -> None:
    """交互式模式
    
    :param matcher: 域名匹配器实例
    :type matcher: DomainMatcher
    """
    print("\n=== 企业域名模糊匹配系统 - 交互模式 ===")
    print("输入 'help' 查看帮助，输入 'quit' 退出")
    print(f"当前已加载 {len(matcher.get_domains())} 个标准域名")
    
    while True:
        try:
            user_input = input("\n请输入域名 > ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break
            
            if user_input.lower() == 'help':
                print("""
可用命令:
  help          - 显示此帮助信息
  quit/exit/q   - 退出程序
  stats         - 显示统计信息
  domains       - 显示所有标准域名
  analyze <域名> - 详细分析指定域名
  
直接输入域名进行匹配查询
""")
                continue
            
            if user_input.lower() == 'stats':
                stats = matcher.get_statistics()
                print(f"\n统计信息:")
                print(f"  标准域名数量: {stats['total_domains']}")
                print(f"  缓存大小: {stats['cache_size']}")
                print(f"  算法权重:")
                print(f"    编辑距离: {stats['weights']['edit_weight']:.2f}")
                print(f"    键盘距离: {stats['weights']['keyboard_weight']:.2f}")
                print(f"    发音相似: {stats['weights']['phonetic_weight']:.2f}")
                print(f"    长度惩罚: {stats['weights']['length_penalty_weight']:.2f}")
                continue
            
            if user_input.lower() == 'domains':
                domains = matcher.get_domains()
                print(f"\n标准域名列表 ({len(domains)} 个):")
                for i, domain in enumerate(domains, 1):
                    print(f"  {i:2d}. {domain}")
                continue
            
            if user_input.lower().startswith('analyze '):
                domain_to_analyze = user_input[8:].strip()
                if domain_to_analyze:
                    analysis = matcher.analyze_input(domain_to_analyze)
                    print(f"\n详细分析结果:")
                    print(json.dumps(analysis, ensure_ascii=False, indent=2))
                else:
                    print("请指定要分析的域名")
                continue
            
            # 执行匹配
            matches = matcher.match(user_input, threshold=0.3, max_results=5)
            
            if not matches:
                print(f"\n未找到匹配的域名 (输入: {user_input})")
                continue
            
            print(f"\n匹配结果 (输入: {user_input}):")
            for i, (domain, score) in enumerate(matches, 1):
                percentage = score * 100
                print(f"  {i}. {domain} ({percentage:.1f}%)")
            
            # 检查是否应该自动重定向
            redirect_target = matcher.should_redirect(user_input, 0.8)
            if redirect_target:
                print(f"\n建议: 自动重定向到 '{redirect_target}'")
            elif matches[0][1] >= 0.6:
                print(f"\n建议: 您是否想访问 '{matches[0][0]}'?")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n错误: {e}")


def batch_mode(matcher: DomainMatcher, input_domains: List[str], 
               threshold: float, output_file: str = None) -> None:
    """批量处理模式
    
    :param matcher: 域名匹配器实例
    :type matcher: DomainMatcher
    :param input_domains: 输入域名列表
    :type input_domains: List[str]
    :param threshold: 匹配阈值
    :type threshold: float
    :param output_file: 输出文件路径
    :type output_file: str
    """
    print(f"\n=== 批量处理模式 ===")
    print(f"处理 {len(input_domains)} 个域名，阈值: {threshold}")
    
    results = {
        'settings': {
            'threshold': threshold,
            'total_inputs': len(input_domains),
            'standard_domains': matcher.get_domains()
        },
        'results': {}
    }
    
    for domain in input_domains:
        matches = matcher.match(domain, threshold=threshold)
        redirect_target = matcher.should_redirect(domain, 0.8)
        
        results['results'][domain] = {
            'matches': [(d, float(s)) for d, s in matches],
            'best_match': matches[0] if matches else None,
            'should_redirect': redirect_target is not None,
            'redirect_target': redirect_target
        }
        
        # 控制台输出
        print(f"\n{domain}:")
        if matches:
            for d, s in matches[:3]:  # 只显示前3个结果
                print(f"  -> {d} ({s*100:.1f}%)")
            if redirect_target:
                print(f"  [自动重定向到: {redirect_target}]")
        else:
            print(f"  -> 无匹配结果")
    
    # 保存结果
    if output_file:
        if save_results_to_file(results, output_file):
            print(f"\n结果已保存到: {output_file}")
        else:
            print(f"\n保存结果失败")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='企业域名模糊匹配系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py -d domains.txt -i                    # 交互模式
  python main.py -d domains.txt -m web api chat      # 匹配指定域名
  python main.py -d domains.txt -f input.txt -o result.json  # 批量处理
  
域名文件格式 (每行一个域名):
  web
  api
  chat
  admin
  mail
"""
    )
    
    parser.add_argument('-d', '--domains', required=True,
                       help='标准域名文件路径')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='启动交互模式')
    parser.add_argument('-m', '--match', nargs='+',
                       help='匹配指定的域名列表')
    parser.add_argument('-f', '--file',
                       help='从文件读取要匹配的域名列表')
    parser.add_argument('-o', '--output',
                       help='输出结果到JSON文件')
    parser.add_argument('-t', '--threshold', type=float, default=0.6,
                       help='匹配阈值 (默认: 0.6)')
    parser.add_argument('--edit-weight', type=float, default=0.4,
                       help='编辑距离权重 (默认: 0.4)')
    parser.add_argument('--keyboard-weight', type=float, default=0.4,
                       help='键盘距离权重 (默认: 0.4)')
    parser.add_argument('--phonetic-weight', type=float, default=0.2,
                       help='发音相似度权重 (默认: 0.2)')
    parser.add_argument('--no-jaro-winkler', action='store_true',
                       help='不使用Jaro-Winkler算法')
    
    args = parser.parse_args()
    
    # 验证参数
    if not any([args.interactive, args.match, args.file]):
        print("错误: 必须指定 -i, -m 或 -f 参数之一")
        parser.print_help()
        sys.exit(1)
    
    # 加载标准域名
    standard_domains = load_domains_from_file(args.domains)
    if not standard_domains:
        print("错误: 无法加载标准域名列表")
        sys.exit(1)
    
    print(f"已加载 {len(standard_domains)} 个标准域名")
    
    # 初始化匹配器
    try:
        matcher = DomainMatcher(
            edit_weight=args.edit_weight,
            keyboard_weight=args.keyboard_weight,
            phonetic_weight=args.phonetic_weight,
            use_jaro_winkler=not args.no_jaro_winkler
        )
        matcher.add_domains(standard_domains)
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)
    
    # 执行相应模式
    if args.interactive:
        interactive_mode(matcher)
    elif args.match:
        batch_mode(matcher, args.match, args.threshold, args.output)
    elif args.file:
        input_domains = load_domains_from_file(args.file)
        if input_domains:
            batch_mode(matcher, input_domains, args.threshold, args.output)
        else:
            print("错误: 无法加载输入域名列表")
            sys.exit(1)


if __name__ == '__main__':
    main()