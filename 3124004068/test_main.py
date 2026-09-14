# -*- coding: utf-8 -*-
"""
论文查重程序单元测试
包含 14 个测试用例，覆盖预处理、SimHash、余弦相似度、综合相似度、文件 IO
"""
import os
import sys
import tempfile
import unittest
import subprocess

from main import (
    read_file, write_result, preprocess,
    compute_simhash, hamming_distance,
    cosine_similarity, calculate_similarity,
    FileError,
)


class TestPreprocess(unittest.TestCase):
    """文本预处理测试"""

    def test_preprocess_empty(self):
        """测试1: 空字符串返回空列表"""
        self.assertEqual(preprocess(""), [])

    def test_preprocess_punctuation(self):
        """测试2: 中文标点被去除"""
        tokens = preprocess("今天，天气晴！")
        self.assertNotIn("，", tokens)
        self.assertNotIn("！", tokens)

    def test_preprocess_case(self):
        """测试3: 英文大小写统一为小写"""
        tokens = preprocess("Hello WORLD")
        self.assertIn("hello", tokens)
        self.assertIn("world", tokens)


class TestSimHash(unittest.TestCase):
    """SimHash 指纹测试"""

    def test_simhash_identical(self):
        """测试4: 相同文本产生相同 SimHash"""
        tokens = preprocess("今天天气很好")
        self.assertEqual(
            compute_simhash(tokens),
            compute_simhash(tokens)
        )

    def test_hamming_same(self):
        """测试5: 同一哈希汉明距离为 0"""
        h = compute_simhash(preprocess("abc"))
        self.assertEqual(hamming_distance(h, h), 0)

    def test_hamming_symmetry(self):
        """测试6: 汉明距离对称"""
        h1 = compute_simhash(preprocess("abc"))
        h2 = compute_simhash(preprocess("xyz"))
        self.assertEqual(
            hamming_distance(h1, h2),
            hamming_distance(h2, h1)
        )


class TestCosine(unittest.TestCase):
    """余弦相似度测试"""

    def test_cosine_identical(self):
        """测试7: 相同词集余弦相似度为 1"""
        tokens = preprocess("今天 天气 晴")
        self.assertAlmostEqual(
            cosine_similarity(tokens, tokens), 1.0, places=5
        )

    def test_cosine_no_common(self):
        """测试8: 无公共词时余弦相似度为 0"""
        t1 = preprocess("苹果 香蕉")
        t2 = preprocess("汽车 飞机")
        self.assertEqual(cosine_similarity(t1, t2), 0.0)

    def test_cosine_empty(self):
        """测试9: 空输入余弦相似度为 0"""
        self.assertEqual(cosine_similarity([], ["a"]), 0.0)
        self.assertEqual(cosine_similarity(["a"], []), 0.0)


class TestSimilarity(unittest.TestCase):
    """综合相似度测试"""

    def test_similarity_identical(self):
        """测试10: 完全相同文本相似度接近 1"""
        text = "今天是星期天，天气晴，今天晚上我要去看电影。"
        rate = calculate_similarity(text, text)
        self.assertGreater(rate, 0.99)

    def test_similarity_sample(self):
        """测试11: 样例抄袭文本相似度在 0.5~1.0 之间"""
        orig = "今天是星期天，天气晴，今天晚上我要去看电影。"
        copy = "今天是周天，天气晴朗，我晚上要去看电影。"
        rate = calculate_similarity(orig, copy)
        self.assertGreater(rate, 0.5)
        self.assertLess(rate, 1.0)

    def test_similarity_completely_different(self):
        """测试12: 完全不同文本相似度低于 0.5"""
        orig = "苹果香蕉橘子梨"
        copy = "汽车飞机轮船火车"
        rate = calculate_similarity(orig, copy)
        self.assertLess(rate, 0.5)


class TestFileIO(unittest.TestCase):
    """文件读写测试"""

    def test_read_missing_file(self):
        """测试13: 读取不存在的文件抛出 FileError"""
        with self.assertRaises(FileError):
            read_file("nonexistent_file_xyz_12345.txt")

    def test_write_and_read(self):
        """测试14: 写入 0.876 后读取应为 0.88"""
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "ans.txt")
            write_result(p, 0.876)
            with open(p, encoding='utf-8') as f:
                self.assertEqual(f.read(), "0.88")


class TestException(unittest.TestCase):
    """异常处理测试"""

    def test_read_empty_string_path(self):
        """测试15: 空路径读取抛 FileError"""
        with self.assertRaises(FileError):
            read_file("")

    def test_write_invalid_path(self):
        """测试16: 写入无效路径抛 FileError"""
        with self.assertRaises(FileError):
            write_result("Z:/nonexistent_dir_xyz/ans.txt", 0.5)


class TestEdgeCases(unittest.TestCase):
    """边界与异常覆盖测试，用于提升覆盖率"""

    def test_read_gbk_file(self):
        """测试17: GBK 编码文件自动回退读取"""
        with tempfile.NamedTemporaryFile(
                mode='wb', suffix='.txt', delete=False) as f:
            f.write("中文测试内容".encode('gbk'))
            path = f.name
        try:
            content = read_file(path)
            self.assertIn("中文", content)
        finally:
            os.unlink(path)

    def test_hamming_zero(self):
        """测试18: 汉明距离输入 0 时返回 0"""
        self.assertEqual(hamming_distance(0, 0), 0)

    def test_cosine_one_empty(self):
        """测试19: 一边为空另一边非空，余弦为 0"""
        self.assertEqual(cosine_similarity([], ["a", "b"]), 0.0)

    def test_similarity_both_empty(self):
        """测试20: 两边都为空返回 1.0"""
        self.assertEqual(calculate_similarity("", ""), 1.0)

    def test_similarity_one_empty(self):
        """测试21: 一边为空返回 0.0"""
        self.assertEqual(calculate_similarity("", "abc"), 0.0)
        self.assertEqual(calculate_similarity("abc", ""), 0.0)

    def test_main_wrong_args(self):
        """测试22: 命令行参数数量错误时退出码为 1"""
        r = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True, text=True
        )
        self.assertEqual(r.returncode, 1)

    def test_main_file_not_exist(self):
        """测试23: 传入不存在的文件退出码为 2"""
        r = subprocess.run(
            [sys.executable, "main.py",
             "no1.txt", "no2.txt", "ans.txt"],
            capture_output=True, text=True
        )
        self.assertEqual(r.returncode, 2)

    def test_main_normal_run(self):
        """测试24: 命令行正常调用返回 0 并写出答案文件"""
        with tempfile.TemporaryDirectory() as d:
            orig = os.path.join(d, "orig.txt")
            copy = os.path.join(d, "copy.txt")
            ans = os.path.join(d, "ans.txt")
            with open(orig, 'w', encoding='utf-8') as f:
                f.write("今天天气很好，我去公园散步。")
            with open(copy, 'w', encoding='utf-8') as f:
                f.write("今天天气不错，我去公园走路。")
            r = subprocess.run(
                [sys.executable, "main.py", orig, copy, ans],
                capture_output=True, text=True
            )
            self.assertEqual(r.returncode, 0)
            self.assertTrue(os.path.exists(ans))
            with open(ans, encoding='utf-8') as f:
                content = f.read()
            self.assertRegex(content, r'^\d+\.\d{2}$')


class TestMainFunction(unittest.TestCase):
    """直接调用 main() 覆盖其内部逻辑"""

    def test_main_with_valid_files(self):
        """测试25: 直接调用 main()，传入真实文件"""
        with tempfile.TemporaryDirectory() as d:
            orig = os.path.join(d, "o.txt")
            copy = os.path.join(d, "c.txt")
            ans = os.path.join(d, "a.txt")
            with open(orig, 'w', encoding='utf-8') as f:
                f.write("今天天气很好")
            with open(copy, 'w', encoding='utf-8') as f:
                f.write("今天天气不错")
            old_argv = sys.argv
            sys.argv = ["main.py", orig, copy, ans]
            try:
                from main import main
                main()
                self.assertTrue(os.path.exists(ans))
            finally:
                sys.argv = old_argv

    def test_preprocess_with_whitespace(self):
        """测试26: 含多个空格的文本预处理"""
        tokens = preprocess("  今天   天气  很好  ")
        self.assertIn("今天", tokens)
        self.assertIn("天气", tokens)

    def test_read_directory_as_file(self):
        """测试27: 传入目录路径时抛 FileError"""
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileError):
                read_file(d)


if __name__ == '__main__':
    unittest.main(verbosity=2)