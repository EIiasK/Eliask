import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def read_file(file_path):
    """
    读取文件内容
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def cosine_similarity_between_texts(text1, text2):
    """
    计算两个文本之间的 Cosine 相似度
    """
    # 使用 TfidfVectorizer 将文本转化为 TF-IDF 向量
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])

    # 计算 Cosine 相似度
    similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    return similarity_matrix[0][0]


def main():
    # 从命令行获取文件路径
    if len(sys.argv) != 4:
        print("用法（终端或命令行输入）: python check_plagiarism.py <原文文件路径> <抄袭版文件路径> <输出文件路径>")
        return

    orig_file_path = sys.argv[1]
    plagiarized_file_path = sys.argv[2]
    output_file_path = sys.argv[3]

    # 读取原文文件和抄袭版文件
    orig_text = read_file(orig_file_path)
    plagiarized_text = read_file(plagiarized_file_path)

    # 计算相似度
    similarity = cosine_similarity_between_texts(orig_text, plagiarized_text)

    # 将相似度结果写入输出文件
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{similarity:.2f}")

    print(f"相似度计算完成，结果已保存到 {output_file_path}")


if __name__ == '__main__':
    main()