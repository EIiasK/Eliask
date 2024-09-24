# 四则运算生成程序
import argparse  # 用于解析命令行参数
import random  # 用于生成随机数
import sys  # 用于退出程序
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
        numerator = random.randint(1, denominator - 1)  # 分子
        return Fraction(numerator, denominator)


class Expression:
    def __init__(self, operator=None, left=None, right=None, value=None, parenthesis=False):
        """
        表达式类，用于表示算术表达式的树结构。
        """
        self.operator = operator  # 运算符，如 '+', '-', '*', '/'
        self.left = left  # 左子表达式
        self.right = right  # 右子表达式
        self.value = value  # 叶子节点的数值（Fraction 类型）
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
        获取表达式的规范形式字符串，用于检查重复。
        """
        if self.value is not None:
            return number_to_string(self.value)
        else:
            left_canonical = self.left.canonical_form()
            right_canonical = self.right.canonical_form()
            if self.operator in ['+', '*']:
                # 对于加法和乘法，操作数排序
                operands = sorted([left_canonical, right_canonical])
                expr_str = f"{operands[0]} {self.operator} {operands[1]}"
            else:
                expr_str = f"{left_canonical} {self.operator} {right_canonical}"
            if self.parenthesis:
                expr_str = f"({expr_str})"
            return expr_str


def generate_expression(max_operators, range_limit):
    """
    递归生成随机的算术表达式，运算符个数不超过 max_operators。
    """
    if max_operators == 0:
        # 基本情况，生成一个数值节点
        value = generate_number(range_limit)
        return Expression(value=value)
    else:
        if random.choice(['number', 'expression']) == 'number':
            # 生成数值节点
            value = generate_number(range_limit)
            return Expression(value=value)
        else:
            # 生成运算符节点
            operator = random.choice(['+', '-', '*', '/'])
            left_operators = random.randint(0, max_operators - 1)
            right_operators = max_operators - 1 - left_operators
            if operator == '-':
                # 对于减法，确保左操作数大于等于右操作数
                while True:
                    left_expr = generate_expression(left_operators, range_limit)
                    right_expr = generate_expression(right_operators, range_limit)
                    try:
                        left_value = left_expr.evaluate()
                        right_value = right_expr.evaluate()
                        if left_value >= right_value:
                            break
                    except ZeroDivisionError:
                        continue
            elif operator == '/':
                # 对于除法，确保结果为真分数
                while True:
                    left_expr = generate_expression(left_operators, range_limit)
                    right_expr = generate_expression(right_operators, range_limit)
                    try:
                        right_value = right_expr.evaluate()
                        if right_value == 0:
                            continue
                        result = left_expr.evaluate() / right_value
                        if result.numerator < result.denominator:
                            break
                    except ZeroDivisionError:
                        continue
            else:
                # 对于加法和乘法，确保左操作数小于等于右操作数
                left_expr = generate_expression(left_operators, range_limit)
                right_expr = generate_expression(right_operators, range_limit)
                left_value = left_expr.evaluate()
                right_value = right_expr.evaluate()
                if operator in ['+', '*'] and left_value > right_value:
                    left_expr, right_expr = right_expr, left_expr
            expr = Expression(operator=operator, left=left_expr, right=right_expr)
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

def generate_problems(n, range_limit):
    """
    生成 n 道不重复的算术题目，数值范围在 [0, range_limit)。
    """
    expressions = []
    canonical_forms = set()
    while len(expressions) < n:
        expr = generate_valid_expression(3, range_limit)
        canonical_str = expr.canonical_form()
        canonical_hash = hash(canonical_str)
        if canonical_hash not in canonical_forms:
            # 检查是否重复
            canonical_forms.add(canonical_hash)
            expressions.append(expr)


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
    postfix = infix_to_postfix(tokens)    # 中缀表达式转后缀表达式
    expr = build_expression_tree(postfix) # 构建表达式树
    return expr

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

def infix_to_postfix(tokens):
    """
    将中缀表达式的标记列表转换为后缀表达式。
    """
    precedence = {'+':1, '-':1, '*':2, '/':2}
    output = []
    stack = []
    for token in tokens:
        if token not in '+-*/()':
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # 弹出左括号
        else:
            while stack and stack[-1] != '(' and precedence[token] <= precedence[stack[-1]]:
                output.append(stack.pop())
            stack.append(token)
    while stack:
        output.append(stack.pop())
    return output

def build_expression_tree(postfix):
    """
    根据后缀表达式构建表达式树。
    """
    stack = []
    for token in postfix:
        if token not in '+-*/':
            value = parse_number(token)
            stack.append(Expression(value=value))
        else:
            right = stack.pop()
            left = stack.pop()
            expr = Expression(operator=token, left=left, right=right)
            stack.append(expr)
    return stack[0]

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
