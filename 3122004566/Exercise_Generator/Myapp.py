# 四则运算生成程序
import argparse  # 用于解析命令行参数
import random    # 用于生成随机数
import sys       # 用于退出程序
from fractions import Fraction  # 用于处理分数

def number_to_string(number):
    """
    将 Fraction 类型的数转换为字符串表示形式，支持真分数和带分数。
    """
    if number.denominator == 1:
        # 如果是整数
        return str(number.numerator)
    elif number.numerator > number.denominator:
        # 如果是带分数
        whole = number.numerator // number.denominator  # 整数部分
        remainder = number.numerator % number.denominator  # 分数部分的分子
        return f"{whole}'{remainder}/{number.denominator}"
    else:
        # 如果是真分数
        return f"{number.numerator}/{number.denominator}"