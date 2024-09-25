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
    elif abs(number.numerator) > number.denominator:
        # 如果是带分数
        whole = number.numerator // number.denominator  # 整数部分
        remainder = abs(number.numerator % number.denominator)  # 分数部分的分子
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
        self.operator = operator
        self.left = left
        self.right = right
        self.value = value
        self.parenthesis = parenthesis

    def evaluate(self):
        """
        计算表达式的值，返回 Fraction 类型的结果。
        """
        if self.value is not None:
            print(f"Evaluating number: {self.value}")
            return self.value
        else:
            print(f"Evaluating: ({self.left.to_string()} {self.operator} {self.right.to_string()})")
            left_value = self.left.evaluate()
            right_value = self.right.evaluate()
            if self.operator == '+':
                result = left_value + right_value
            elif self.operator == '-':
                result = left_value - right_value
            elif self.operator == '*':
                result = left_value * right_value
            elif self.operator == '/':
                if right_value == 0:
                    raise ZeroDivisionError("除数为零")
                result = left_value / right_value
            print(f"Result of ({self.left.to_string()} {self.operator} {self.right.to_string()}) = {result}")
            return result

    def to_string(self):
        if self.value is not None:
            return number_to_string(self.value)
        else:
            left_str = self.left.to_string()
            right_str = self.right.to_string()
            expr_str = f"{left_str} {self.operator} {right_str}"
            if self.parenthesis:
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

def generate_expression(min_operators, max_operators, range_limit):
    """
    递归生成随机的算术表达式，运算符个数在[min_operators, max_operators]之间。
    """
    if max_operators == 0:
        # 如果没有可用的运算符数量，返回一个数值节点
        value = generate_number(range_limit)
        return Expression(value=value)
    else:
        if min_operators > 0:
            # 必须生成一个运算符节点
            operator = random.choice(['+', '-', '*', '/'])
            left_min = max(0, min_operators - 1)
            left_max = max_operators - 1
            left_operators = random.randint(left_min, left_max)
            right_min = max(0, min_operators - 1 - left_operators)
            right_max = max_operators - 1 - left_operators
            right_operators = random.randint(right_min, right_max)
        else:
            # 可以选择生成数值节点或运算符节点
            if random.choice(['number', 'expression']) == 'number':
                value = generate_number(range_limit)
                return Expression(value=value)
            else:
                operator = random.choice(['+', '-', '*', '/'])
                left_operators = random.randint(0, max_operators - 1)
                right_operators = max_operators - 1 - left_operators
        if operator == '-':
            # 对于减法，确保左操作数大于等于右操作数
            while True:
                left_expr = generate_expression(left_operators, left_operators, range_limit)
                right_expr = generate_expression(right_operators, right_operators, range_limit)
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
                left_expr = generate_expression(left_operators, left_operators, range_limit)
                right_expr = generate_expression(right_operators, right_operators, range_limit)
                try:
                    right_value = right_expr.evaluate()
                    if right_value == 0:
                        continue
                    result = left_expr.evaluate() / right_value
                    if 0 < abs(result) < 1:
                        break
                except ZeroDivisionError:
                    continue
        else:
            # 对于加法和乘法，直接生成
            left_expr = generate_expression(left_operators, left_operators, range_limit)
            right_expr = generate_expression(right_operators, right_operators, range_limit)
        expr = Expression(operator=operator, left=left_expr, right=right_expr)
        expr.parenthesis = random.choice([True, False])  # 随机决定是否添加括号
        return expr

def generate_valid_expression(min_operators, max_operators, range_limit):
    """
    生成一个有效的算术表达式，确保计算结果非负且不产生除零错误，且运算符数量符合要求。
    """
    while True:
        expr = generate_expression(min_operators, max_operators, range_limit)
        try:
            value = expr.evaluate()
            if value < 0:
                continue
            return expr
        except ZeroDivisionError:
            continue

def generate_problems(n, range_limit):
    """
    生成 n 道不重复的算术题目，数值范围在 [0, range_limit)，且每道题目至少包含一个运算符。
    """
    expressions = []
    canonical_forms = set()
    while len(expressions) < n:
        expr = generate_valid_expression(1, 3, range_limit)  # 最少1个运算符，最多3个运算符
        canonical = expr.canonical_form()
        if canonical not in canonical_forms:
            # 检查是否重复
            canonical_forms.add(canonical)
            expressions.append(expr)
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
                f_ex.write(f"{idx}. {expr.to_string()} =\n")  # 写入题目，添加编号
        with open('Answers.txt', 'w', encoding='utf-8') as f_ans:
            for idx, expr in enumerate(expressions, 1):
                value = expr.evaluate()
                ans_str = number_to_string(value)
                f_ans.write(f"{idx}. {ans_str}\n")  # 写入答案，添加编号
    elif args.e is not None and args.a is not None:
        # 批改答案模式
        grade(args.e, args.a)
    else:
        # 参数不足，打印帮助信息
        parser.print_help()
        sys.exit(1)

def tokenize(expr_str):
    """
    将表达式字符串分割为标记列表（数字、运算符、括号）。
    使用正则表达式正确识别分数和带分数。
    """
    import re
    # 定义正则表达式模式，匹配整数、真分数、带分数，以及运算符和括号
    token_pattern = r"\d+'?\d*/\d+|\d+/\d+|\d+|[+\-*/()]"
    tokens = re.findall(token_pattern, expr_str)
    return tokens

def parse_expression(expr_str):
    """
    将字符串形式的算术表达式解析为 Expression 对象。
    """
    expr_str = expr_str.replace(' ', '')  # 去除空格
    tokens = tokenize(expr_str)           # 分词
    postfix = infix_to_postfix(tokens)    # 中缀表达式转后缀表达式
    expr = build_expression_tree(postfix) # 构建表达式树
    return expr

def infix_to_postfix(tokens):
    """
    将中缀表达式的标记列表转换为后缀表达式。
    考虑运算符的优先级和左结合性。
    """
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    output = []
    stack = []
    for token in tokens:
        if token not in '+-*/()':
            # 操作数直接加入输出队列
            output.append(token)
        elif token == '(':
            # 左括号压入栈
            stack.append(token)
        elif token == ')':
            # 右括号，弹出栈顶运算符直到遇到左括号
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # 弹出左括号
        else:
            # 处理运算符
            while stack and stack[-1] != '(' and precedence.get(stack[-1], 0) >= precedence.get(token, 0):
                # 栈顶运算符优先级大于或等于当前运算符
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
            print(f"Pushed number: {value}")
        else:
            right = stack.pop()
            left = stack.pop()
            expr = Expression(operator=token, left=left, right=right)
            stack.append(expr)
            print(f"Popped {left.to_string()} and {right.to_string()} for operator '{token}'")
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
            # 去掉编号和等号
            ex_expr = ex_line.strip()
            if ex_expr.endswith('='):
                ex_expr = ex_expr[:-1]
            if '.' in ex_expr:
                ex_expr = ex_expr.split('.', 1)[1].strip()
            ans_str = ans_line.strip()
            if '.' in ans_str:
                ans_str = ans_str.split('.', 1)[1].strip()
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
