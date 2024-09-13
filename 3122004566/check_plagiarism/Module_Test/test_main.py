import sys
import os
import unittest

# 获取当前文件夹和父目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# 将父目录添加到 sys.path
sys.path.insert(0, parent_dir)

from main import cosine_similarity_between_texts  # 导入被测试的函数
from main import read_file

class TestPlagiarismDetection(unittest.TestCase):
    def test_identical_texts(self):
        text = "今天是星期天，天气晴，今天晚上我要去看电影。"
        similarity = cosine_similarity_between_texts(text, text)
        self.assertAlmostEqual(similarity, 1.0, places=2)

    def test_completely_different_texts(self):
        text1 = "今天天气不错，我想去公园散步。"
        text2 = "数据结构与算法是计算机科学的基础。"
        similarity = cosine_similarity_between_texts(text1, text2)
        self.assertLess(similarity, 0.1)  # 相似度应小于 0.1

    def test_partial_similarity(self):
        text1 = "今天是星期天，天气晴，今天晚上我要去看电影。"
        text2 = "今天是周天，天气晴朗，我晚上要去看电影。"
        similarity = cosine_similarity_between_texts(text1, text2)
        self.assertGreater(similarity, 0.5)

    def test_empty_text(self):
        text1 = ""
        text2 = "任何文本"
        similarity = cosine_similarity_between_texts(text1, text2)
        self.assertEqual(similarity, 0.0)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            read_file("non_existent_file.txt")

    def test_empty_file(self):
        # 创建一个空文件
        with open("empty.txt", 'w', encoding='utf-8') as f:
            pass  # 空操作，文件内容为空
        # 测试 read_file 是否抛出 ValueError 异常
        with self.assertRaises(ValueError):
            text = read_file("empty.txt")
        # 清理测试文件
        import os
        os.remove("empty.txt")

    def test_vectorization_exception(self):
        # 直接传入一个非字符串类型的数据，可能导致函数内部异常以触发异常并用self.assertRaises捕获
        text = None  # 非法输入
        with self.assertRaises(Exception):
            cosine_similarity_between_texts(text, "正常文本")

if __name__ == '__main__':
    unittest.main()
