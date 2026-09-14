# -*- coding: utf-8 -*-
"""
论文查重程序
用法: python main.py [原文文件] [抄袭版论文] [答案文件]
算法: SimHash + 余弦相似度 加权融合
"""
import sys
import os
import re
import math
import hashlib
from collections import Counter

import jieba

# 预加载 jieba 词典（避免第一次调用慢）
jieba.initialize()


class FileError(Exception):
    """自定义文件异常，用于封装文件读写相关错误。"""


def read_file(path: str) -> str:
    """
    读取文件内容，支持 UTF-8 / GBK 编码。
    文件不存在或不可读时抛出 FileError。
    """
    if not os.path.exists(path):
        raise FileError(f"文件不存在: {path}")
    if not os.path.isfile(path):
        raise FileError(f"路径不是文件: {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 回退到 GBK（兼容 Windows 记事本默认编码）
        with open(path, 'r', encoding='gbk', errors='ignore') as f:
            return f.read()
    except IOError as e:
        raise FileError(f"读取文件失败: {path}, 原因: {e}") from e


def write_result(path: str, rate: float) -> None:
    """写出结果，保留两位小数"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"{rate:.2f}")
    except IOError as e:
        raise FileError(f"写入文件失败: {path}, 原因: {e}") from e


def preprocess(text: str) -> list:
    """
    文本预处理：
    1. 合并空白字符
    2. 去除标点（保留中文、字母、数字、空格）
    3. jieba 分词（关闭 HMM，切分更细）
    4. 转小写
    """
    if not text:
        return []
    text = re.sub(r'[\s\u3000]+', ' ', text)
    text = re.sub(r'[^\w\u4e00-\u9fff ]+', '', text)
    tokens = [
        w.strip().lower()
        for w in jieba.cut(text, HMM=False)
        if w.strip()
    ]
    return tokens


def _hash64(token: str) -> int:
    """对单个 token 生成 64 位哈希值"""
    h = hashlib.md5(token.encode('utf-8')).hexdigest()
    return int(h[:16], 16)


def compute_simhash(tokens: list, bits: int = 64) -> int:
    """
    计算 SimHash 指纹：
    - 对每个 token 生成 64 位哈希
    - 按词频加权，逐位累加
    - 大于 0 的位设为 1
    """
    if not tokens:
        return 0
    freq = Counter(tokens)
    v = [0] * bits
    for token, weight in freq.items():
        h = _hash64(token)
        for i in range(bits):
            bit = (h >> i) & 1
            if bit:
                v[i] += weight
            else:
                v[i] -= weight
    fingerprint = 0
    for i in range(bits):
        if v[i] > 0:
            fingerprint |= (1 << i)
    return fingerprint


def hamming_distance(h1: int, h2: int) -> int:
    """计算两个整数的汉明距离（二进制不同位的数量）"""
    x = h1 ^ h2
    count = 0
    while x:
        x &= (x - 1)
        count += 1
    return count


def cosine_similarity(tokens1: list, tokens2: list) -> float:
    """基于词频向量的余弦相似度，值域 [0, 1]"""
    if not tokens1 or not tokens2:
        return 0.0
    c1 = Counter(tokens1)
    c2 = Counter(tokens2)
    common = set(c1.keys()) & set(c2.keys())
    if not common:
        return 0.0
    dot = sum(c1[w] * c2[w] for w in common)
    norm1 = math.sqrt(sum(v * v for v in c1.values()))
    norm2 = math.sqrt(sum(v * v for v in c2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def calculate_similarity(orig_text: str, copy_text: str) -> float:
    """
    综合相似度：
    0.5 × SimHash 相似度 + 0.5 × 余弦相似度
    结果裁剪到 [0, 1]
    """
    tokens1 = preprocess(orig_text)
    tokens2 = preprocess(copy_text)

    # 边界处理
    if not tokens1 and not tokens2:
        return 1.0
    if not tokens1 or not tokens2:
        return 0.0

    # SimHash 相似度
    h1 = compute_simhash(tokens1)
    h2 = compute_simhash(tokens2)
    dist = hamming_distance(h1, h2)
    simhash_sim = 1.0 - dist / 64.0

    # 余弦相似度
    cos_sim = cosine_similarity(tokens1, tokens2)

    # 加权融合
    final = 0.5 * simhash_sim + 0.5 * cos_sim
    return max(0.0, min(1.0, final))


def main():
    """程序入口：解析命令行参数，计算相似度并写出结果。"""
    if len(sys.argv) != 4:
        print("用法: python main.py [原文文件] [抄袭版论文] [答案文件]")
        sys.exit(1)

    orig_path, copy_path, ans_path = sys.argv[1], sys.argv[2], sys.argv[3]
    try:
        orig_text = read_file(orig_path)
        copy_text = read_file(copy_path)
        rate = calculate_similarity(orig_text, copy_text)
        write_result(ans_path, rate)
        print(f"重复率: {rate:.2f}")
    except FileError as e:
        print(f"[错误] {e}")
        sys.exit(2)
    except Exception as e:  # pylint: disable=broad-except
        print(f"[未预期错误] {e}")
        sys.exit(3)


if __name__ == '__main__':
    main()
