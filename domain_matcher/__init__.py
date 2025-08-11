#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""企业域名模糊匹配系统

本模块提供了一个智能的域名模糊匹配系统，能够根据用户的错误输入
找到最相似的正确域名。系统考虑了键盘物理位置、发音相似性等因素。

Author: @phil616
Date: 2025-8-11
License: MIT
"""

from .core import DomainMatcher
from .keyboard import KeyboardDistance
from .phonetic import PhoneticSimilarity
from .utils import normalize_domain

__version__ = "1.0.0"
__author__ = "Domain Fuzzy Team"

__all__ = [
    "DomainMatcher",
    "KeyboardDistance",
    "PhoneticSimilarity",
    "normalize_domain",
]