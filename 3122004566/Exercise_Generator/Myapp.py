# 四则运算生成程序
import argparse
import random     #生成随机数
import sys
from fractions import Fraction

def number_to_string(number):
    """
    将 Fraction 类型的数转换为字符串表示形式，支持真分数和带分数。
    """
    if number.denominator == 1:
        # 如果是整数
        return str(number.numerator)
    elif abs(number.numerator) > number.denominator:
        # 如果是带分数
        whole = abs(number.numerator) // number.denominator  # 整数部分
        remainder = abs(number.numerator) % number.denominator  # 分数部分的分子
        sign = '-' if number.numerator < 0 else ''
        return f"{sign}{whole}'{remainder}/{number.denominator}"
    else:
        # 如果是真分数
        sign = '-' if number.numerator < 0 else ''
        return f"{sign}{abs(number.numerator)}/{number.denominator}"

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
    def __init__(self, operator=None, operands=None, value=None, parenthesis=False):
        """
        表达式类，用于表示算术表达式的树结构。
        """
        self.operator = operator      # 运算符，如 '+', '-', '*', '/'
        self.operands = operands      # 操作数列表，对于多元运算符（如左结合的加法）
        self.value = value            # 叶子节点的数值（Fraction 类型）
        self.parenthesis = parenthesis  # 是否添加括号

    def evaluate(self):
        """
        计算表达式的值，返回 Fraction 类型的结果。
        """
        if self.value is not None:
            # 如果是数值节点，直接返回值
            return self.value
        else:
            # 递归计算操作数的值
            result = self.operands[0].evaluate()
            for operand in self.operands[1:]:
                if self.operator == '+':
                    result += operand.evaluate()
                elif self.operator == '-':
                    result -= operand.evaluate()
                elif self.operator == '*':
                    result *= operand.evaluate()
                elif self.operator == '/':
                    result /= operand.evaluate()
            return result

    def to_string(self):
        """
        将表达式转换为字符串形式，添加必要的括号和空格。
        """
        if self.value is not None:
            # 数值节点，转换为字符串
            return number_to_string(self.value)
        else:
            # 运算符节点，递归转换操作数
            if self.operator in ['+', '*']:
                # 对于左结合的加法和乘法，用运算符连接所有操作数
                expr_str = f" {self.operator} ".join([operand.to_string() for operand in self.operands])
            else:
                # 对于减法和除法，只能是二元运算
                left_str = self.operands[0].to_string()
                right_str = self.operands[1].to_string()
                expr_str = f"{left_str} {self.operator} {right_str}"
            if self.parenthesis:
                # 如果需要添加括号
                expr_str = f"({expr_str})"
            return expr_str

    def canonical_form(self):
        """
        获取表达式的规范形式，用于检查重复。
        对于加法和乘法，考虑左结合性，仅在同一层次上允许操作数交换。
        """
        if self.value is not None:
            return ('num', self.value)
        else:
            # 获取每个操作数的规范形式
            operands_canonical = [operand.canonical_form() for operand in self.operands]
            if self.operator in ['+', '*']:
                # 对于加法和乘法，在同一层次上对操作数排序
                operands_canonical[1:] = sorted(operands_canonical[1:])
            return (self.operator, tuple(operands_canonical))

def generate_expression(max_operators, range_limit):
    """
    递归生成随机的算术表达式，运算符个数不超过 max_operators。
    """
    if max_operators == 0:
        # 基本情况，生成一个数值节点
        value = generate_number(range_limit)
        return Expression(value=value)
    else:
        # 随机选择运算符
        operator = random.choice(['+', '-', '*', '/'])
        if operator in ['+', '*']:
            # 对于加法和乘法，可以有多个操作数，体现左结合性
            num_operands = random.randint(2, max_operators + 1)
            operands = []
            remaining_operators = max_operators - (num_operands - 1)
            for _ in range(num_operands):
                ops = random.randint(0, remaining_operators)
                remaining_operators -= ops
                operand = generate_expression(ops, range_limit)
                operands.append(operand)
            expr = Expression(operator=operator, operands=operands)
        else:
            # 对于减法和除法，只能是二元运算
            left_ops = random.randint(0, max_operators - 1)
            right_ops = max_operators - 1 - left_ops
            left_expr = generate_expression(left_ops, range_limit)
            right_expr = generate_expression(right_ops, range_limit)
            if operator == '-':
                # 确保不出现负数
                while True:
                    try:
                        if left_expr.evaluate() >= right_expr.evaluate():
                            break
                        else:
                            left_expr = generate_expression(left_ops, range_limit)
                            right_expr = generate_expression(right_ops, range_limit)
                    except ZeroDivisionError:
                        left_expr = generate_expression(left_ops, range_limit)
                        right_expr = generate_expression(right_ops, range_limit)
            elif operator == '/':
                # 确保结果是真分数
                while True:
                    try:
                        if right_expr.evaluate() != 0 and abs(left_expr.evaluate() / right_expr.evaluate()) < 1:
                            break
                        else:
                            left_expr = generate_expression(left_ops, range_limit)
                            right_expr = generate_expression(right_ops, range_limit)
                    except ZeroDivisionError:
                        left_expr = generate_expression(left_ops, range_limit)
                        right_expr = generate_expression(right_ops, range_limit)
            expr = Expression(operator=operator, operands=[left_expr, right_expr])
        expr.parenthesis = random.choice([True, False])  # 随机决定是否添加括号
        return expr

def generate_valid_expression(max_operators, range_limit):
    """
    生成一个有效的算术表达式，确保计算结果非负且不产生除零错误。
    """
    while True:
        expr = generate_expression(max_operators, range_limit)
        try:
            value = expr.evaluate()
            if value < 0:
                continue
            return expr
        except ZeroDivisionError:
            continue

def expressions_equal(expr1, expr2):
    """
    判断两个表达式是否等价，考虑左结合性和有限次交换。
    """
    return expr1.canonical_form() == expr2.canonical_form()

def generate_problems(n, range_limit):
    """
    生成 n 道不重复的算术题目，数值范围在 [0, range_limit)。
    """
    expressions = []
    canonical_forms = set()
    attempts = 0  # 用于避免无限循环
    while len(expressions) < n and attempts < n * 10:
        expr = generate_valid_expression(3, range_limit)
        canonical = expr.canonical_form()
        if canonical not in canonical_forms:
            # 检查是否重复
            canonical_forms.add(canonical)
            expressions.append(expr)
        attempts += 1
    if len(expressions) < n:
        print(f"无法生成足够的不重复题目，已生成 {len(expressions)} 道题目。")
    return expressions

def parse_number(s):
    """
    将字符串形式的数值解析为 Fraction 类型。
    支持整数、真分数和带分数。
    """
    s = s.strip()
    if "'" in s:
        # 处理带分数，如 2'3/5
        whole_str, frac_str = s.split("'")
        whole = int(whole_str)
        numerator, denominator = map(int, frac_str.split('/'))
        return Fraction(whole * denominator + numerator, denominator)
    elif '/' in s:
        # 处理真分数，如 3/5
        numerator, denominator = map(int, s.split('/'))
        return Fraction(numerator, denominator)
    else:
        # 处理整数
        return Fraction(int(s))

def main():
    """
    主函数，解析命令行参数并执行相应的功能。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, help='生成题目的个数')
    parser.add_argument('-r', type=int, help='数值范围（不包括该数）')
    parser.add_argument('-e', type=str, help='题目文件')
    parser.add_argument('-a', type=str, help='答案文件')
    args = parser.parse_args()

    if args.n is not None and args.r is not None:
        # 生成题目模式
        if args.n <= 0:
            print("题目个数应为正整数。")
            sys.exit(1)
        if args.r <= 1:
            print("数值范围应大于1。")
            sys.exit(1)
        expressions = generate_problems(args.n, args.r)
        with open('Exercises.txt', 'w', encoding='utf-8') as f_ex:
            for idx, expr in enumerate(expressions, 1):
                f_ex.write(f"{expr.to_string()} =\n")  # 写入题目
        with open('Answers.txt', 'w', encoding='utf-8') as f_ans:
            for expr in expressions:
                value = expr.evaluate()
                ans_str = number_to_string(value)
                f_ans.write(f"{ans_str}\n")  # 写入答案
    elif args.e is not None and args.a is not None:
        # 批改答案模式
        grade(args.e, args.a)
    else:
        # 参数不足，打印帮助信息
        parser.print_help()
        sys.exit(1)

def parse_expression(expr_str):
    """
    将字符串形式的算术表达式解析为 Expression 对象。
    """
    expr_str = expr_str.replace(' ', '')  # 去除空格
    tokens = tokenize(expr_str)           # 分词
    expr, _ = parse_tokens(tokens)
    return expr

def tokenize(expr_str):
    """
    将表达式字符串分割为标记列表（数字、运算符、括号）。
    """
    tokens = []
    i = 0
    while i < len(expr_str):
        if expr_str[i] in '+-*/()':
            tokens.append(expr_str[i])
            i += 1
        else:
            j = i
            while j < len(expr_str) and expr_str[j] not in '+-*/()':
                j += 1
            tokens.append(expr_str[i:j])
            i = j
    return tokens

def parse_tokens(tokens, index=0):
    """
    递归解析标记列表，构建表达式树。
    """
    def parse_operand():
        nonlocal index
        token = tokens[index]
        if token == '(':
            index += 1
            expr, _ = parse_expression()
            if tokens[index] != ')':
                raise ValueError("缺少右括号")
            index += 1
            return expr
        else:
            index += 1
            value = parse_number(token)
            return Expression(value=value)

    def parse_expression():
        nonlocal index
        left = parse_operand()
        while index < len(tokens) and tokens[index] in '+-*/':
            op = tokens[index]
            index += 1
            right = parse_operand()
            if op in ['+', '*']:
                # 左结合性
                operands = [left, right]
                while index < len(tokens) and tokens[index] == op:
                    index += 1
                    next_operand = parse_operand()
                    operands.append(next_operand)
                left = Expression(operator=op, operands=operands)
            else:
                left = Expression(operator=op, operands=[left, right])
        return left, index

    expr, index = parse_expression()
    return expr, index

def grade(exercise_file, answer_file):
    """
    批改答案，生成批改结果文件。
    """
    with open(exercise_file, 'r', encoding='utf-8') as f_ex:
        exercises = f_ex.readlines()
    with open(answer_file, 'r', encoding='utf-8') as f_ans:
        answers = f_ans.readlines()
    if len(exercises) != len(answers):
        print("题目数与答案数不一致。")
        sys.exit(1)
    correct = []
    wrong = []
    for idx, (ex_line, ans_line) in enumerate(zip(exercises, answers), 1):
        try:
            ex_expr = ex_line.strip().rstrip(' =')
            ans_str = ans_line.strip()
            expr = parse_expression(ex_expr)
            correct_answer = expr.evaluate()
            user_answer = parse_number(ans_str)
            if correct_answer == user_answer:
                correct.append(idx)
            else:
                wrong.append(idx)
        except Exception as e:
            wrong.append(idx)
    with open('Grade.txt', 'w', encoding='utf-8') as f_grade:
        f_grade.write(f"Correct: {len(correct)} ({', '.join(map(str, correct))})\n")
        f_grade.write(f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})\n")

if __name__ == '__main__':
    main()
