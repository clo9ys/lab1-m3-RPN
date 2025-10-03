# LEVEL M3
import sys


def is_int(el):
    """
    Проверяет, является ли число целым.

    Args:
        el: Число для проверки

    Returns:
        bool: True если число целое, False в противном случае
    """
    return el == int(el)


def check_op(el):
    """
    Проверяет, является ли элемент бинарной операцией.

    Args:
        el: Элемент для проверки

    Returns:
        bool: True если элемент является бинарной операцией, False в противном случае
    """
    return el in ["+", "*", "-", "/", "%", "//", "**"]


def unary_op(el):
    """
    Проверяет, является ли элемент унарной операцией.

    Args:
        el: Элемент для проверки

    Returns:
        bool: True если элемент является унарной операцией, False в противном случае
    """
    return el in ['$', '~']


def check_num(el):
    """
    Проверяет, можно ли преобразовать строку в число.

    Args:
        el: Строка для проверки

    Returns:
        bool: True если строку можно преобразовать в число, False в противном случае
    """
    try:
        float(el)
        return 1
    except ValueError:
        return 0


def check_brackets(expr):
    """
    Проверяет корректность расстановки скобок в выражении.

    Args:
        expr: Входное выражение

    Returns:
        bool: True если скобки расставлены правильно, False в противном случае
    """
    stack = []

    for char in expr:
        if char == '(':  # Открывающая скобка - добавляем в стек
            stack.append(char)

        elif char == ')':  # Закрывающая скобка
            if stack:  # Если есть соответствующая открывающая
                stack.pop()
            else:
                return 0  # Закрывающая без открывающей - ошибка

    return len(stack) == 0  # Все скобки должны быть закрыты


def remove_brackets(expr):
    """
    Удаляет все скобки из выражения, если они корректны.

    Args:
        expr: Выражение со скобками

    Returns:
        str: Выражение без скобок
    """
    if check_brackets(expr):
        res_str = ''
        for char in expr:
            if char not in '()':  # Пропускаем скобки
                res_str += char
            else:
                res_str += ' '
        return res_str.strip() # Итоговое выражение без скобок
    return None


def calc(expr):
    """
    Вычисляет выражение в обратной польской нотации (RPN).

    Args:
        expr: Список токенов выражения в RPN

    Raises:
        ZeroDivisionError: При делении на ноль
        ValueError: При недопустимых значениях для операций // или %
        SyntaxError: Если в стеке остались лишние элементы после вычислений

    """
    stack = []

    # Обрабатываем каждый элемент выражения
    for el in expr:
        if check_num(el):
            # Число - добавляем в стек (преобразуем к float)
            stack.append(float(el))

        elif unary_op(el):
            # Унарные операции: извлекаем один операнд
            num1 = stack.pop()
            match el:
                case "$":
                    stack.append(num1)  # Унарный плюс (ничего не меняет)
                case "~":
                    stack.append(-1 * num1)  # Унарный минус

        elif check_op(el):
            # Бинарные операции: извлекаем два операнда
            num1 = stack.pop()
            num2 = stack.pop()
            res = 0

            # Выполняем соответствующую операцию
            match el:
                case "+":
                    res = num1 + num2
                case "**":
                    res = num2 ** num1  # Возведение в степень
                case "*":
                    res = num1 * num2
                case "-":
                    res = num2 - num1  # Важно: num2 - num1 (порядок в RPN)
                case "//":
                    # Целочисленное деление - требуются целые числа
                    if is_int(num2) and is_int(num1) and num1 != 0:
                        res = int(num2 // num1)
                    elif num1 == 0:
                        raise ZeroDivisionError("Integer division by zero")
                    else:
                        raise ValueError("Operands for // must be integers")
                case "/":
                    # Обычное деление
                    if num1 != 0:
                        res = num2 / num1
                    else:
                        raise ZeroDivisionError("Division by zero")
                case "%":
                    # Остаток от деления - требуются целые числа
                    if is_int(num2) and is_int(num1) and num1 != 0:
                        res = int(num2 % num1)
                    elif num1 == 0:
                        raise ZeroDivisionError("Modulo by zero")
                    else:
                        raise ValueError("Operands for % must be integers")

            stack.append(res)  # Результат операции помещаем обратно в стек

    # После обработки всех элементов в стеке должен остаться только результат
    result = stack.pop()
    if not stack:  # Стек должен быть пуст
        print(result)
    else:
        raise IndexError("Invalid expression")


def run():
    """
    Основная функция для чтения и вычисления выражений из стандартного ввода.

    Читает выражения построчно из stdin, проверяет скобки и вычисляет результат.
    Обрабатывает различные типы ошибок с соответствующими сообщениями.
    """
    for line in sys.stdin:
        try:
            # Проверяем наличие скобок в выражении
            if '(' in line or ')' in line:
                if check_brackets(line):
                    # Удаляем скобки и вычисляем выражение
                    new_line = remove_brackets(line)
                    calc(new_line.strip().split())
                else:
                    raise SyntaxError("Invalid brackets")
            else:
                # Выражение без скобок - вычисляем напрямую
                calc(line.strip().split())

        # Обработка различных типов ошибок
        except ZeroDivisionError as zero:
            print(f"ERROR: {zero}")
        except ValueError as val:
            print(f"ERROR: {val}")
        except IndexError:
            print(f"ERROR: expression is incorrect")
        except SyntaxError as syn:
            print(f"ERROR: {syn}")


if __name__ == "__main__":
    run()