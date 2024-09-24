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

def generate_number(range_limit):
    """
    生成一个随机的自然数或真分数，范围在 [0, range_limit)。
    """
    if random.choice(['natural', 'fraction']) == 'natural':
        # 生成自然数
        return Fraction(random.randint(0, range_limit - 1))
    else:
        # 生成真分数
        denominator = random.randint(2, range_limit - 1)  # 分母
        numerator = random.randint(1, denominator - 1)    # 分子
        return Fraction(numerator, denominator)

