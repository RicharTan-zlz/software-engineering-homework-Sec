# -*- coding: utf-8 -*-
"""
论文查重程序 —— 第一版（基础文件读写）
用法: python main.py [原文文件] [抄袭版论文] [答案文件]
"""
import sys
import os


class FileError(Exception):
    """自定义文件异常"""
    pass


def read_file(path: str) -> str:
    """读取文件内容，支持 UTF-8 编码"""
    if not os.path.exists(path):
        raise FileError(f"文件不存在: {path}")
    if not os.path.isfile(path):
        raise FileError(f"路径不是文件: {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, 'r', encoding='gbk', errors='ignore') as f:
            return f.read()


def write_result(path: str, rate: float) -> None:
    """写出结果，保留两位小数"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"{rate:.2f}")


def main():
    if len(sys.argv) != 4:
        print("用法: python main.py [原文文件] [抄袭版论文] [答案文件]")
        sys.exit(1)

    orig_path, copy_path, ans_path = sys.argv[1], sys.argv[2], sys.argv[3]
    try:
        orig_text = read_file(orig_path)
        copy_text = read_file(copy_path)
        # 第一版先返回固定值，验证流程
        rate = 0.50
        write_result(ans_path, rate)
        print(f"重复率: {rate:.2f}")
    except FileError as e:
        print(f"[错误] {e}")
        sys.exit(2)


if __name__ == '__main__':
    main()