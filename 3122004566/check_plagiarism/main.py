import sys
import threading
import re  # 用于正则表达式操作，以便去除标点符号
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 创建一个全局的 TfidfVectorizer 实例，避免重复构建词汇表
vectorizer = TfidfVectorizer()
vectorizer_lock = threading.Lock()  # 锁，用于线程安全


def preprocess_text(text):
    """
    预处理文本，去除标点符号并转换为小写
    """
    # 去除标点符号
    text = re.sub(r'[^\w\s]', '', text)
    # 转换为小写
    text = text.lower()
    return text


def read_file(file_path):
    """
    读取文件内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                raise ValueError(f"文件 {file_path} 为空。")
            return content
    except FileNotFoundError:
        print(f"未找到文件 {file_path} ")
        raise
    except Exception as e:
        print(f"读取文件错误 {file_path}: {e}")
        raise


def cosine_similarity_between_texts(text1, text2):
    """
    计算两个文本之间的 Cosine 相似度
    """
    try:
        # 使用全局的 vectorizer，需加锁保证线程安全
        with vectorizer_lock:
            # 由于预处理后词汇表可能变化，需要每次都拟合
            tfidf_matrix = vectorizer.fit_transform([text1, text2])

        # 使用稀疏矩阵计算 Cosine 相似度
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return similarity_matrix[0][0]
    except Exception as e:
        print(f"计算 cosine 相似度错误: {e}")
        raise


def main():
    # 从命令行获取文件路径
    if len(sys.argv) != 4:
        print("用法（命令行参数输入）: python main.py <论文原文文件路径> <疑似抄袭的文件路径> <输出的答案文件路径>")
        return

    orig_file_path = sys.argv[1]
    plagiarized_file_path = sys.argv[2]
    output_file_path = sys.argv[3]

    # 读取原文文件和抄袭版文件
    orig_text = read_file(orig_file_path)
    plagiarized_text = read_file(plagiarized_file_path)

    # 预处理文本
    orig_text = preprocess_text(orig_text)
    plagiarized_text = preprocess_text(plagiarized_text)

    # 计算相似度
    similarity = cosine_similarity_between_texts(orig_text, plagiarized_text)

    # 将相似度结果写入输出文件
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{similarity:.2f}")
        print(f"相似度计算完成，结果已保存到 {output_file_path}")
    except Exception as e:
        print(f"写入 {output_file_path} 出错: {e}")
        raise


if __name__ == '__main__':
    main()
