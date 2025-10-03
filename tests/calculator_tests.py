import pytest
import sys
from io import StringIO
from src.main import is_int, check_op, unary_op, check_num, check_brackets, remove_brackets, calc, run

class TestIsInt:
    """Тесты для функции is_int"""
    @pytest.mark.parametrize("input_val,expected", [
    (5.0, True),  # целое как float
    (5.5, False),  # не целое
    (0.0, True),  # ноль
    (-3.0, True),  # отрицательное целое
    (-3.5, False),  # отрицательное не целое
    (10, True),  # целое int
    ])
    def test_is_int(self, input_val, expected):
        assert is_int(input_val) == expected

class TestCheckOp:
    """Тесты для функции check_op"""
    @pytest.mark.parametrize("operator,expected", [
        ("+", True),
        ("-", True),
        ("*", True),
        ("/", True),
        ("%", True),
        ("//", True),
        ("**", True),
        ("$", False),  # унарная операция
        ("~", False),  # унарная операция
        ("abc", False),  # не операция
        ("1", False),  # число
    ])
    def test_check_op(self, operator, expected):
        assert check_op(operator) == expected

class TestUnaryOp:
    """Тесты для функции unary_op"""
    @pytest.mark.parametrize("operator,expected", [
        ("$", True),
        ("~", True),
        ("+", False),  # бинарная операция
        ("-", False),  # бинарная операция
        ("abc", False),  # не операция
    ])
    def test_unary_op(self, operator, expected):
        assert unary_op(operator) == expected

class TestCheckNum:
    """Тесты для функции check_num"""
    @pytest.mark.parametrize("input_str,expected", [
        ("123", True),
        ("12.34", True),
        ("-56", True),
        ("-78.9", True),
        ("0", True),
        ("0.0", True),
        ("abc", False),
        ("12a", False),
        ("", False),
        ("12.34.56", False),
    ])
    def test_check_num(self, input_str, expected):
        assert check_num(input_str) == expected

class TestCheckBrackets:
    """Тесты для функции check_brackets"""
    @pytest.mark.parametrize("expression,expected", [
        ("(a + b)", True),
        ("((a + b) * c)", True),
        ("(((a)))", True),
        ("()", True),
        ("", True),
        (")(", False),
        ("(a + b))", False),
        ("((a + b)", False),
        ("(a + (b * c)", False),
        ("a + b)", False),
        ("(a + b", False),
    ])
    def test_check_brackets(self, expression, expected):
        assert check_brackets(expression) == expected


class TestRemoveBrackets:
    """Тесты для функции remove_brackets"""

    @pytest.mark.parametrize("expression,expected", [
        ("(a + b)", "a + b"),
        ("((a + b))", "a + b"),
        ("(a)", "a"),
        ("()", ""),
        ("(1 + (2 * 3))", "1 +  2 * 3"),
        ("(a + b", None),  # некорректные скобки
    ])
    def test_remove_brackets(self, expression, expected):
        result = remove_brackets(expression)
        assert result == expected


class TestCalc:
    """Тесты для функции calc"""

    @pytest.mark.parametrize("expression,expected_output", [
        (["2", "3", "+"], 5),
        (["5", "2", "-"], 3),
        (["3", "4", "*"], 12),
        (["10", "2", "/"], 5),
        (["2", "3", "**"], 8),
        (["5", "2", "//"], 2),
        (["7", "3", "%"], 1),
    ])
    def test_calc_binary_operations(self, expression, expected_output, capsys):
        calc(expression)
        captured = capsys.readouterr()
        assert float(captured.out.strip()) == expected_output

    @pytest.mark.parametrize("expression,expected_output", [
        (["5", "$"], 5),
        (["5", "~"], -5),
        (["-3", "~"], 3),
    ])
    def test_calc_unary_operations(self, expression, expected_output, capsys):
        calc(expression)
        captured = capsys.readouterr()
        assert float(captured.out.strip()) == expected_output

    @pytest.mark.parametrize("expression,expected_error", [
        (["5", "0", "/"], ZeroDivisionError),
        (["5", "0", "//"], ZeroDivisionError),
        (["5", "0", "%"], ZeroDivisionError),
        (["5.5", "2", "//"], ValueError),
        (["5", "2.5", "%"], ValueError),
    ])
    def test_calc_errors(self, expression, expected_error):
        with pytest.raises(expected_error):
            calc(expression)

    def test_calc_syntax_error(self):
        with pytest.raises(IndexError, match="Invalid expression"):
            calc(["2", "3", "+", "5"])  # лишний элемент


class TestRun:
    """Тесты для основной функции run"""

    def test_run_basic_operations(self, monkeypatch, capsys):
        test_input = "2 3 +\n5 2 -\n3 4 *\n10 2 /\n"
        monkeypatch.setattr(sys, 'stdin', StringIO(test_input))

        run()

        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        assert lines == ['5.0', '3.0', '12.0', '5.0']

    def test_run_with_brackets(self, monkeypatch, capsys):
        test_input = "( 2 3 + )\n( ( 5 2 - ) )\n"
        monkeypatch.setattr(sys, 'stdin', StringIO(test_input))

        run()

        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        assert lines == ['5.0', '3.0']

    def test_run_division_by_zero(self, monkeypatch, capsys):
        test_input = "5 0 /\n"
        monkeypatch.setattr(sys, 'stdin', StringIO(test_input))

        run()

        captured = capsys.readouterr()
        assert "ERROR: Division by zero" in captured.out

    def test_run_invalid_brackets(self, monkeypatch, capsys):
        test_input = "( 2 3 +\n"
        monkeypatch.setattr(sys, 'stdin', StringIO(test_input))

        run()

        captured = capsys.readouterr()
        assert "ERROR: Invalid brackets" in captured.out

    def test_run_value_error(self, monkeypatch, capsys):
        test_input = "5.5 2 //\n"
        monkeypatch.setattr(sys, 'stdin', StringIO(test_input))

        run()

        captured = capsys.readouterr()
        assert "ERROR: Operands for // must be integers" in captured.out

    def test_run_invalid_expression(self, monkeypatch, capsys):
        test_input = "2 3 + 5\n"
        monkeypatch.setattr(sys, 'stdin', StringIO(test_input))

        run()

        captured = capsys.readouterr()
        assert "ERROR: expression is incorrect" in captured.out


class TestComplexExpressions:
    """Тесты для сложных выражений"""

    @pytest.mark.parametrize("expression,expected", [
        (["3", "4", "4", "*", "1", "5", "-", "2", "**", "/", "+"], 4.0),
        (["2", "3", "~", "*", "5", "+"], -1.0),
        (["10", "3", "~", "$", "+"], 7.0),
    ])
    def test_complex_expressions(self, expression, expected, capsys):
        calc(expression)
        captured = capsys.readouterr()
        assert float(captured.out.strip()) == expected


# Дополнительные тесты для edge cases
class TestEdgeCases:
    """Тесты для граничных случаев"""

    def test_empty_expression(self):
        with pytest.raises(IndexError):
            calc([])

    def test_single_number(self, capsys):
        calc(["42"])
        captured = capsys.readouterr()
        assert float(captured.out.strip()) == 42.0

    def test_multiple_unary_operations(self, capsys):
        calc(["5", "~", "~"])  # двойное отрицание
        captured = capsys.readouterr()
        assert float(captured.out.strip()) == 5.0
