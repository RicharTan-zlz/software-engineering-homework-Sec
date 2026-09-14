# 论文查重程序

> 软件工程第一次个人编程作业 · 学号 3124004068

## 一、功能简介

给定一份原文和一个抄袭版论文文件，程序计算两者之间的重复率，并将结果（保留两位小数）写入指定的答案文件。

## 二、算法

采用 **SimHash + 余弦相似度** 的混合方案：

| 步骤 | 方法 | 说明 |
|------|------|------|
| 1 | 文本清洗 | 去除标点、空白，统一大小写 |
| 2 | 中文分词 | jieba 分词，关闭 HMM |
| 3 | SimHash | 生成 64 位指纹，计算汉明距离 |
| 4 | 余弦相似度 | 基于词频向量计算夹角余弦 |
| 5 | 加权融合 | 最终相似度 = 0.5 × SimHash + 0.5 × 余弦 |

## 三、环境要求

- Python 3.8+
- jieba==0.42.1

安装依赖：

    pip install -r requirements.txt

## 四、使用方法

    python main.py [原文文件] [抄袭版论文] [答案文件]

示例：

    python main.py D:\tests\orig.txt D:\tests\orig_add.txt D:\tests\ans.txt

输出：

    重复率: 0.76

同时 `ans.txt` 中会写入 `0.76`。

## 五、项目结构

    3124004068/
    ├── main.py            # 主程序
    ├── test_main.py       # 单元测试（27 个用例）
    ├── requirements.txt   # 依赖列表
    ├── README.md          # 本文件
    └── .gitignore         # Git 忽略配置

## 六、测试

运行单元测试：

    python -m unittest test_main.py -v

生成覆盖率报告：

    python -m coverage run -m unittest test_main.py
    python -m coverage report -m
    python -m coverage html

当前覆盖率：
- main.py：88%
- 总体：94%

## 七、代码质量

- pylint 评分：10.00/10
- 覆盖率：94%
- 单元测试：27 个，全部通过

## 八、性能

| 文本大小 | 处理时间 |
|---------|---------|
| 315 KB | 1.02 秒 |
| 10 MB  | 约 2.1 秒 |

瓶颈在 jieba 分词（占总耗时 48%），算法本身耗时 < 0.01 秒。

## 九、异常处理

| 异常 | 场景 | 处理 |
|------|------|------|
| FileError | 文件不存在/不是文件 | 打印错误，退出码 2 |
| UnicodeDecodeError | UTF-8 解码失败 | 回退 GBK 编码 |
| IOError | 读写失败 | 包装为 FileError |
| 参数错误 | argv 数量不对 | 打印用法，退出码 1 |