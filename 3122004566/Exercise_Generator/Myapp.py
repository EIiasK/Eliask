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


class Expression:
    def __init__(self, operator=None, left=None, right=None, value=None, parenthesis=False):
        """
        表达式类，用于表示算术表达式的树结构。
        """
        self.operator = operator  # 运算符，如 '+', '-', '*', '/'
        self.left = left          # 左子表达式
        self.right = right        # 右子表达式
        self.value = value        # 叶子节点的数值（Fraction 类型）
        self.parenthesis = parenthesis  # 是否添加括号

    def evaluate(self):
        """
        计算表达式的值，返回 Fraction 类型的结果。
        """
        if self.value is not None:
            # 如果是数值节点，直接返回值
            return self.value
        else:
            # 递归计算左、右子表达式的值
            left_value = self.left.evaluate()
            right_value = self.right.evaluate()
            if self.operator == '+':
                return left_value + right_value
            elif self.operator == '-':
                return left_value - right_value
            elif self.operator == '*':
                return left_value * right_value
            elif self.operator == '/':
                return left_value / right_value

    def to_string(self):
        """
        将表达式转换为字符串形式，添加必要的括号和空格。
        """
        if self.value is not None:
            # 数值节点，转换为字符串
            return number_to_string(self.value)
        else:
            # 运算符节点，递归转换左右子表达式
            left_str = self.left.to_string()
            right_str = self.right.to_string()
            op = self.operator
            expr_str = f"{left_str} {op} {right_str}"
            if self.parenthesis:
                # 如果需要添加括号
                expr_str = f"({expr_str})"
            return expr_str

    def canonical_form(self):
        """
        获取表达式的规范形式，用于检查重复题目。
        对于交换律的运算符（加法和乘法），按照操作数排序。
        """
        if self.value is not None:
            return ('num', self.value)
        else:
            left_canonical = self.left.canonical_form()
            right_canonical = self.right.canonical_form()
            if self.operator in ['+', '*']:
                # 对于加法和乘法，操作数排序
                operands = [left_canonical, right_canonical]
                operands.sort()
                return (self.operator, operands[0], operands[1])
            else:
                return (self.operator, left_canonical, right_canonical)
