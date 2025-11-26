import re


class inf:
    def __init__(self, sign):
        # sign - boolean (False - positive, True - negative)
        self.sign = sign


class nan:
    def __init__(self):
        pass


class MyNum:
    def __init__(self, value):
        self.value = value

    def __add__(self, other):
        if isinstance(self.value, nan) or isinstance(other.value, nan):
            return nan()
        elif isinstance(self.value, inf) or isinstance(other.value, inf):
            if isinstance(self.value, inf) and isinstance(other.value, inf):
                if self.value.sign == other.value.sign:
                    return inf(self.value.sign)
                else:
                    return nan()
            elif isinstance(self.value, inf):
                return self.value
            else:
                return other.value
        else:
            return self.value + other.value

    def __sub__(self, other):
        if isinstance(self.value, nan) or isinstance(other.value, nan):
            return nan()
        elif isinstance(self.value, inf) or isinstance(other.value, inf):
            if isinstance(self.value, inf) and isinstance(other.value, inf):
                if self.value.sign == other.value.sign:
                    return nan()
                else:
                    return self.value
            elif isinstance(self.value, inf):
                return self.value
            else:
                return inf(not other.value.sign)
        else:
            return self.value - other.value

    def __mul__(self, other):
        if isinstance(self.value, nan) or isinstance(other.value, nan):
            return nan()
        elif isinstance(self.value, inf) or isinstance(other.value, inf):
            if isinstance(self.value, inf) and isinstance(other.value, inf):
                return inf(self.value.sign ^ other.value.sign)
            else:
                if isinstance(self.value, inf):
                    if other.value == 0:
                        return nan()
                    return inf(self.value.sign ^ (other.value < 0))
                else:
                    if self.value == 0:
                        return nan()
                    return inf(other.value.sign ^ (self.value < 0))
        else:
            return self.value * other.value

    def __truediv__(self, other):
        if isinstance(self.value, nan) or isinstance(other.value, nan):
            return nan()
        elif isinstance(self.value, inf) or isinstance(other.value, inf):
            if isinstance(self.value, inf) and isinstance(other.value, inf):
                return nan()
            elif isinstance(self.value, inf):
                if other.value == 0:
                    return nan()
                return inf(self.value.sign ^ (other.value < 0))
            else:
                return 0.0
        else:
            if other.value == 0:
                if self.value == 0:
                    return nan()
                else:
                    return inf(self.value < 0)
            else:
                return self.value / other.value

    def __pow__(self, other):
        if isinstance(self.value, nan) or isinstance(other.value, nan):
            return nan()
        elif isinstance(self.value, inf):
            if isinstance(other.value, inf):
                if other.value.sign == False: 
                    return self.value
                else: 
                    return 0.0
            elif other.value > 0:
                return self.value
            elif other.value == 0:
                return 1.0
            else:
                return 0.0
        elif isinstance(other.value, inf):
            if other.value.sign == False:  
                if abs(self.value) > 1:
                    return inf(False)
                elif abs(self.value) < 1:
                    return 0.0
                else:
                    return nan()  
            else:  
                if abs(self.value) > 1:
                    return 0.0
                elif abs(self.value) < 1:
                    return inf(False)
                else:
                    return nan()
        else:
            if self.value == 0 and other.value < 0:
                return inf(True)
            else:
                try:
                    return self.value ** other.value
                except:
                    return nan()

    def __neg__(self):
        if isinstance(self.value, nan):
            return nan()
        elif isinstance(self.value, inf):
            return inf(not self.value.sign)
        else:
            return 0 - self.value


PRECEDENCE = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '^': 3,
    'u-': 4
}


def tokenize(expression):
    clean_expression = expression.lower().replace(" ", "")
    pattern = re.compile(r'\d+\.\d+|\d+|inf|nan|[()+\-*/^]')
    tokens = pattern.findall(clean_expression)

    reconstructed = "".join(tokens)
    if len(reconstructed) != len(clean_expression):
        raise ValueError("Invalid characters")

    return tokens


def to_rpn(tokens):
    output = []
    stack = []
    last_token = None

    for token in tokens:
        is_number = token.replace('.', '', 1).isdigit() or token in ['inf', 'nan']

        if is_number:
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack:
                stack.pop()
        elif token in PRECEDENCE:
            op = token
            if op == '-' and (last_token is None or last_token in PRECEDENCE or last_token == '('):
                op = 'u-'

            while (stack and stack[-1] in PRECEDENCE and
                   PRECEDENCE[stack[-1]] >= PRECEDENCE[op]):
                if op == 'u-' or op == '^':
                    break
                output.append(stack.pop())
            stack.append(op)

        last_token = token

    while stack:
        output.append(stack.pop())

    return output


def evaluate_rpn(rpn_queue):
    stack = []
    for token in rpn_queue:
        if token.replace('.', '', 1).isdigit():
            stack.append(MyNum(float(token)))
        elif token == 'inf':
            stack.append(MyNum(inf(False)))
        elif token == 'nan':
            stack.append(MyNum(nan()))
        elif token in PRECEDENCE:
            if token == 'u-':
                if not stack: return MyNum(nan())
                a = stack.pop()
                res = -a
                stack.append(MyNum(res.value if isinstance(res, MyNum) else res))
            else:
                if len(stack) < 2: return MyNum(nan())
                b = stack.pop()
                a = stack.pop()
                res = None
                if token == '+':
                    res = a + b
                elif token == '-':
                    res = a - b
                elif token == '*':
                    res = a * b
                elif token == '/':
                    res = a / b
                elif token == '^':
                    res = a ** b

                val_to_store = res.value if isinstance(res, MyNum) else res
                stack.append(MyNum(val_to_store))

    return stack[0] if stack else MyNum(nan())


def calculate(expression):
    try:
        tokens = tokenize(expression)
        rpn = to_rpn(tokens)
        result = evaluate_rpn(rpn)
        return result
    except Exception:
        return MyNum(nan())


def format_result(my_num_obj):
    val = my_num_obj.value
    if isinstance(val, nan):
        return "nan"
    elif isinstance(val, inf):
        return "-inf" if val.sign else "inf"
    else:
        if val == int(val):
            return str(int(val))
        return str(val)


def main():
    print("Калькулятор запущен. Введите выражение (или 'exit' для выхода).")
    print("Используйте '_' для подстановки предыдущего результата.")

    last_result = None

    while True:
        try:
            user_input = input(">>> ")
        except EOFError:
            break

        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Выход из программы.")
            break

        if not user_input.strip():
            continue

        expression = user_input

        if '_' in expression:
            if last_result is None:
                print("Ошибка: Нет предыдущего результата для использования '_'.")
                continue
            prev_res_str = format_result(last_result)
            expression = expression.replace('_', prev_res_str)

        try:
            tokenize(expression)
            result_obj = calculate(expression)
            last_result = result_obj
            print(f"Результат: {format_result(result_obj)}")
        except ValueError:
            print("Ошибка: Введено недопустимое выражение.")


if __name__ == "__main__":
    main()
