import argparse  # 用于解析命令行参数
import random    # 用于生成随机数
import sys       # 用于退出程序
from fractions import Fraction  # 用于处理分数
import re        # 用于正则表达式

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
    使用正则表达式正确识别分数和带分数。
    """
    # 定义正则表达式模式，匹配带分数（如2'3/4）、真分数（如3/4）、整数和运算符
    token_pattern = r"\d+'?\d*/\d+|\d+/\d+|\d+|[+\-*/()]"
    tokens = re.findall(token_pattern, expr_str)
    return tokens

def parse_expression_recursive(tokens):
    """
    使用递归下降解析器解析表达式，并返回计算结果。
    """
    def parse_expression():
        """
        expression ::= term (( '+' | '-' ) term)*
        """
        nonlocal pos
        expr = parse_term()
        while pos < len(tokens) and tokens[pos] in ('+', '-'):
            op = tokens[pos]
            pos += 1
            term = parse_term()
            if op == '+':
                expr += term
            elif op == '-':
                expr -= term
        return expr

    def parse_term():
        """
        term ::= factor (( '*' | '/' ) factor)*
        """
        nonlocal pos
        term = parse_factor()
        while pos < len(tokens) and tokens[pos] in ('*', '/'):
            op = tokens[pos]
            pos += 1
            factor = parse_factor()
            if op == '*':
                term *= factor
            elif op == '/':
                if factor == 0:
                    raise ZeroDivisionError("除数为零")
                term /= factor
        return term

    def parse_factor():
        """
        factor ::= '(' expression ')' | number
        """
        nonlocal pos
        token = tokens[pos]
        if token == '(':
            pos += 1
            expr = parse_expression()
            if pos >= len(tokens) or tokens[pos] != ')':
                raise ValueError("缺少右括号")
            pos += 1
            return expr
        else:
            pos += 1
            return parse_number(token)

    pos = 0
    return parse_expression()

def remove_outer_parentheses(expr):
    """
    移除表达式最外层的括号（如果存在）。
    """
    while expr.startswith('(') and expr.endswith(')'):
        # 检查括号是否匹配
        count = 0
        for i in range(len(expr)):
            if expr[i] == '(':
                count += 1
            elif expr[i] == ')':
                count -= 1
            if count == 0 and i < len(expr) - 1:
                break
        else:
            # 如果整个表达式都在一对括号内，则移除
            expr = expr[1:-1]
            continue
        break
    return expr

def canonical_form(expr_str):
    """
    生成表达式的规范形式，用于检测重复题目。
    对于具备交换律的运算符（+ 和 *），操作数按升序排列。
    对于不具备交换律的运算符（- 和 /），保持操作顺序。
    """
    tokens = tokenize(expr_str)
    pos = 0

    def parse_expression():
        nonlocal pos
        expr = parse_term()
        while pos < len(tokens) and tokens[pos] in ('+', '-'):
            op = tokens[pos]
            pos += 1
            right = parse_term()
            if op in ('+'):
                # 交换律：排序操作数
                if expr > right:
                    expr, right = right, expr
            expr = f"{expr}{op}{right}"
        return expr

    def parse_term():
        nonlocal pos
        term = parse_factor()
        while pos < len(tokens) and tokens[pos] in ('*', '/'):
            op = tokens[pos]
            pos += 1
            right = parse_factor()
            if op in ('*'):
                # 交换律：排序操作数
                if term > right:
                    term, right = right, term
            term = f"{term}{op}{right}"
        return term

    def parse_factor():
        nonlocal pos
        token = tokens[pos]
        if token == '(':
            pos += 1
            expr = parse_expression()
            if pos >= len(tokens) or tokens[pos] != ')':
                raise ValueError("缺少右括号")
            pos += 1
            return f"({expr})"
        else:
            pos += 1
            return token

    canonical = parse_expression()
    return canonical

def generate_expression(min_operators, max_operators, range_limit, is_outermost=True):
    """
    递归生成随机的算术表达式，运算符个数在[min_operators, max_operators]之间。
    仅在必要时添加括号，以确保运算顺序。
    """
    if max_operators == 0:
        # 如果没有可用的运算符数量，返回一个数值节点
        value = generate_number(range_limit)
        return number_to_string(value)
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
                return number_to_string(generate_number(range_limit))
            else:
                operator = random.choice(['+', '-', '*', '/'])
                left_operators = random.randint(0, max_operators - 1)
                right_operators = max_operators - 1 - left_operators

        if operator == '-':
            # 对于减法，确保左操作数大于等于右操作数
            attempts = 0
            while True:
                left_expr = generate_expression(left_operators, left_operators, range_limit, is_outermost=False)
                right_expr = generate_expression(right_operators, right_operators, range_limit, is_outermost=False)
                try:
                    left_value = parse_expression_recursive(tokenize(left_expr))
                    right_value = parse_expression_recursive(tokenize(right_expr))
                    if left_value >= right_value:
                        break
                except ZeroDivisionError:
                    pass  # 重试
                attempts += 1
                if attempts > 10:
                    # 防止无限循环
                    break
        elif operator == '/':
            # 对于除法，确保结果为真分数
            attempts = 0
            while True:
                left_expr = generate_expression(left_operators, left_operators, range_limit, is_outermost=False)
                right_expr = generate_expression(right_operators, right_operators, range_limit, is_outermost=False)
                try:
                    right_value = parse_expression_recursive(tokenize(right_expr))
                    if right_value == 0:
                        raise ZeroDivisionError
                    result = parse_expression_recursive(tokenize(left_expr)) / right_value
                    if 0 < abs(result) < 1:
                        break
                except ZeroDivisionError:
                    pass  # 重试
                attempts += 1
                if attempts > 10:
                    # 防止无限循环
                    break
        else:
            # 对于加法和乘法，直接生成
            left_expr = generate_expression(left_operators, left_operators, range_limit, is_outermost=False)
            right_expr = generate_expression(right_operators, right_operators, range_limit, is_outermost=False)

        # 根据运算符优先级决定是否添加括号
        # 仅在需要改变默认运算顺序时添加括号
        # 例如，生成 "5 + 3 * 2" 时，不需要括号，因为乘法优先
        # 生成 "2 * (3 + 4)" 时，需要括号，以改变运算顺序
        add_parentheses = False
        if operator in ['+', '-']:
            # 如果左右表达式包含 '*' 或 '/', 则需要为其添加括号
            if re.search(r'[*/]', left_expr) or re.search(r'[*/]', right_expr):
                add_parentheses = True
        # 对于 '*' 和 '/', 一般不需要添加括号

        if add_parentheses and not is_outermost:
            expr = f"({left_expr} {operator} {right_expr})"
        else:
            expr = f"{left_expr} {operator} {right_expr}"
        return expr

def generate_valid_expression(min_operators, max_operators, range_limit):
    """
    生成一个有效的算术表达式，确保计算结果非负且不产生除零错误，且运算符数量符合要求。
    """
    attempts = 0
    while True:
        expr = generate_expression(min_operators, max_operators, range_limit, is_outermost=True)
        expr = remove_outer_parentheses(expr)  # 移除最外层括号
        try:
            value = parse_expression_recursive(tokenize(expr))
            if value < 0:
                raise ValueError("结果为负数")
            return expr
        except (ZeroDivisionError, ValueError):
            attempts += 1
            if attempts > 100:
                raise ValueError("无法生成有效的表达式")

def generate_problems(n, range_limit):
    """
    生成 n 道不重复的算术题目，数值范围在 [0, range_limit)，且每道题目至少包含一个运算符。
    """
    expressions = []
    canonical_forms = set()
    while len(expressions) < n:
        try:
            expr = generate_valid_expression(1, 3, range_limit)  # 最少1个运算符，最多3个运算符
            canon = canonical_form(expr)
            if canon not in canonical_forms:
                canonical_forms.add(canon)
                expressions.append(expr)
        except ValueError:
            continue  # 重试
    return expressions

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
            # 去掉编号
            if '.' in ex_expr:
                ex_expr = ex_expr.split('.', 1)[1].strip()
            ans_str = ans_line.strip()
            # 去掉编号
            if '.' in ans_str:
                ans_str = ans_str.split('.', 1)[1].strip()
            expr_value = parse_expression_recursive(tokenize(ex_expr))
            user_answer = parse_number(ans_str)
            if expr_value == user_answer:
                correct.append(idx)
            else:
                wrong.append(idx)
        except Exception as e:
            wrong.append(idx)
    with open('Grade.txt', 'w', encoding='utf-8') as f_grade:
        f_grade.write(f"Correct: {len(correct)} ({', '.join(map(str, correct))})\n")
        f_grade.write(f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})\n")

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
                f_ex.write(f"{idx}. {expr} =\n")  # 写入题目，添加编号
        with open('Answers.txt', 'w', encoding='utf-8') as f_ans:
            for idx, expr in enumerate(expressions, 1):
                value = parse_expression_recursive(tokenize(expr))
                ans_str = number_to_string(value)
                f_ans.write(f"{idx}. {ans_str}\n")  # 写入答案，添加编号
    elif args.e is not None and args.a is not None:
        # 批改答案模式
        grade(args.e, args.a)
    else:
        # 参数不足，打印帮助信息
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
