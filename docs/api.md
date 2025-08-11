# API 文档

## 核心类和方法

### DomainMatcher 类

主要的域名匹配器类，提供完整的模糊匹配功能。

#### 初始化

```python
from domain_matcher import DomainMatcher

matcher = DomainMatcher(
    edit_weight=0.4,        # 编辑距离权重
    keyboard_weight=0.4,    # 键盘距离权重
    phonetic_weight=0.2,    # 发音相似度权重
    length_penalty=0.1,     # 长度惩罚权重
    match_threshold=0.6,    # 匹配阈值
    use_jaro_winkler=False, # 是否使用Jaro-Winkler算法
    cache_size=1000         # 缓存大小
)
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `edit_weight` | float | 0.4 | 编辑距离算法权重 |
| `keyboard_weight` | float | 0.4 | 键盘距离算法权重 |
| `phonetic_weight` | float | 0.2 | 发音相似度算法权重 |
| `length_penalty` | float | 0.1 | 长度差异惩罚权重 |
| `match_threshold` | float | 0.6 | 最低匹配阈值 |
| `use_jaro_winkler` | bool | False | 是否启用Jaro-Winkler增强 |
| `cache_size` | int | 1000 | LRU缓存大小 |

#### 主要方法

##### add_domains(domains)

添加标准域名列表。

```python
domains = ['google.com', 'facebook.com', 'github.com']
matcher.add_domains(domains)
```

**参数：**
- `domains` (List[str]): 标准域名列表

**返回：**
- None

##### find_matches(input_domain, top_k=5)

查找匹配的域名。

```python
matches = matcher.find_matches('gogle.com', top_k=3)
```

**参数：**
- `input_domain` (str): 输入的域名
- `top_k` (int): 返回的最大匹配数量

**返回：**
- `List[Dict]`: 匹配结果列表

**返回格式：**
```python
[
    {
        'domain': 'google.com',
        'score': 0.85,
        'confidence': 'high',
        'details': {
            'edit_distance': 0.8,
            'keyboard_distance': 0.9,
            'phonetic_similarity': 0.7
        }
    }
]
```

##### get_best_match(input_domain)

获取最佳匹配结果。

```python
best_match = matcher.get_best_match('gogle.com')
```

**参数：**
- `input_domain` (str): 输入的域名

**返回：**
- `Dict` 或 `None`: 最佳匹配结果，如果没有匹配则返回None

##### should_redirect(input_domain, threshold=0.8)

判断是否应该自动重定向。

```python
should_redirect = matcher.should_redirect('gogle.com')
```

**参数：**
- `input_domain` (str): 输入的域名
- `threshold` (float): 重定向阈值

**返回：**
- `bool`: 是否应该重定向

##### analyze_input(input_domain)

分析输入域名的详细信息。

```python
analysis = matcher.analyze_input('gogle.com')
```

**返回格式：**
```python
{
    'original_input': 'gogle.com',
    'normalized_input': 'gogle.com',
    'matches': [
        {
            'domain': 'google.com',
            'score': 0.85,
            'confidence': 'high'
        }
    ],
    'best_match': {
        'domain': 'google.com',
        'score': 0.85,
        'confidence': 'high'
    },
    'analysis_details': {
        'input_length': 9,
        'possible_errors': ['character_substitution'],
        'error_positions': [2]
    }
}
```

##### get_statistics()

获取系统统计信息。

```python
stats = matcher.get_statistics()
```

**返回格式：**
```python
{
    'total_domains': 100,
    'cache_size': 50,
    'cache_hits': 1250,
    'cache_misses': 150,
    'total_queries': 1400,
    'average_response_time': 0.008,
    'algorithm_weights': {
        'edit_distance': 0.4,
        'keyboard_distance': 0.4,
        'phonetic_similarity': 0.2
    }
}
```

### 工具类和函数

#### EditDistance 类

编辑距离计算器。

```python
from domain_matcher.utils import EditDistance

edit_calc = EditDistance()
similarity = edit_calc.similarity('hello', 'helo')  # 0.8
```

#### KeyboardDistance 类

键盘物理距离计算器。

```python
from domain_matcher.keyboard import KeyboardDistance

keyboard_calc = KeyboardDistance()
similarity = keyboard_calc.similarity('qwerty', 'qeerty')  # 0.92
```

#### PhoneticSimilarity 类

发音相似度计算器。

```python
from domain_matcher.phonetic import PhoneticSimilarity

phonetic_calc = PhoneticSimilarity()
similarity = phonetic_calc.similarity('phone', 'fone')  # 0.85
```

## 命令行接口

### 基本用法

```bash
# 交互模式
python main.py --domains domains.txt -i

# 批量处理
python main.py --domains domains.txt --input input.txt --output results.txt

# 单个查询
python main.py --domains domains.txt --query "gogle.com"
```

### 参数说明

| 参数 | 短参数 | 类型 | 说明 |
|------|--------|------|------|
| `--domains` | `-d` | str | 标准域名文件路径 |
| `--input` | `-i` | str | 输入文件路径（批量模式） |
| `--output` | `-o` | str | 输出文件路径 |
| `--query` | `-q` | str | 单个查询域名 |
| `--interactive` | `-i` | flag | 启用交互模式 |
| `--threshold` | `-t` | float | 匹配阈值 |
| `--top-k` | `-k` | int | 返回结果数量 |
| `--config` | `-c` | str | 配置文件路径 |

### 配置文件格式

```json
{
    "algorithm_weights": {
        "edit_distance": 0.4,
        "keyboard_distance": 0.4,
        "phonetic_similarity": 0.2,
        "length_penalty": 0.1
    },
    "thresholds": {
        "match_threshold": 0.6,
        "redirect_threshold": 0.8,
        "confidence_threshold": 0.9
    },
    "performance": {
        "cache_size": 1000,
        "use_jaro_winkler": false,
        "parallel_processing": true
    }
}
```
