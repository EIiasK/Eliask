import sys
import os
import unittest

# 获取当前文件夹和父目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# 将父目录添加到 sys.path
sys.path.insert(0, parent_dir)

from main import cosine_similarity_between_texts  # 导入被测试的函数

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

if __name__ == '__main__':
    unittest.main()
