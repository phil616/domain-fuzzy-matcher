# 单词域名模糊匹配

## 项目简介

本项目是一个单词模糊匹配系统，用于解决用户在输入单词时的拼写错误问题。当用户输入错误的单词时（如将 `web` 误输入为 `wen`），系统能够智能地匹配到正确的单词并提供重定向建议。

最开始是用于匹配不同的子域名来管理网关的内部基础设施，由Python实现，可参考文档实现nginx的编译模块提供给nginx使用。

## 功能特性

- **智能模糊匹配**: 基于多种相似度算法进行单词匹配
- **键盘物理距离**: 考虑键盘上字母的物理位置关系
- **发音相似性**: 考虑字母在中文发音中的相似性
- **可配置阈值**: 支持自定义匹配阈值
- **概率排序**: 返回按匹配概率排序的候选列表

## 算法原理

### 1. 编辑距离 (Levenshtein Distance)
基础的字符串相似度计算，计算将一个字符串转换为另一个字符串所需的最少编辑操作数。

### 2. 键盘物理距离
考虑QWERTY键盘布局中字母的物理位置，相邻的字母具有更高的混淆概率。

### 3. 发音相似性
基于中文拼音发音规律，某些字母组合在发音上相似（如 u/v, b/p 等）。

### 4. 综合评分算法
```
最终得分 = α × 编辑距离得分 + β × 键盘距离得分 + γ × 发音相似度得分
```

其中 α + β + γ = 1，可根据实际需求调整权重。

## 项目结构

```
domain-fuzzy/
├── README.md
├── requirements.txt
├── main.py
├── domain_matcher/
│   ├── __init__.py
│   ├── core.py          # 核心匹配算法
│   ├── keyboard.py      # 键盘距离计算
│   ├── phonetic.py      # 发音相似性计算
│   └── utils.py         # 工具函数
├── tests/
│   ├── __init__.py
│   └── test_matcher.py
└── examples/
    └── demo.py
```

## 安装和使用

### 安装依赖
```bash
pip install -r requirements.txt
```

### 基本使用
```python
from domain_matcher import DomainMatcher

# 初始化匹配器
matcher = DomainMatcher()

# 添加标准域名列表
standard_domains = ['web', 'api', 'chat', 'admin', 'mail']
matcher.add_domains(standard_domains)

# 进行模糊匹配
results = matcher.match('wen', threshold=0.6)
print(results)  # [('web', 0.94), ('wechat', 0.60), ...]
```

## 配置参数

- `threshold`: 匹配阈值，默认为 0.6
- `edit_weight`: 编辑距离权重，默认为 0.4
- `keyboard_weight`: 键盘距离权重，默认为 0.4
- `phonetic_weight`: 发音相似度权重，默认为 0.2

## 许可证

MIT License
