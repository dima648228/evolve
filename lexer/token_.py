"""
Модуль с описанием токенов и их типов для лексического анализа.
"""

import string
from enum import Enum


class TokenType(Enum):
    """
    Перечисление типов токенов. Содержит все возможные типы, которые может обработать лексер.
    """
    # Типы данных
    T_INT = 'T_INT'          # Целое число
    T_FLOAT = 'T_FLOAT'      # Вещественное число
    T_STRING = 'T_STRING'    # Строка
    T_TRUE = 'T_TRUE'        # Логическое значение True
    T_FALSE = 'T_FALSE'      # Логическое значение False

    # Арифметические операторы
    T_PLUS = 'PLUS'          # Оператор сложения
    T_MINUS = 'MINUS'        # Оператор вычитания
    T_MULTIPLY = 'MULTIPLY'  # Оператор умножения
    T_DIVIDE = 'DIVIDE'      # Оператор деления
    T_MODULO = 'MODULO'      # Оператор остатка от деления
    T_POWER = 'POWER'        # Оператор возведения в степень

    # Операторы сравнения
    T_EQ = 'EQ'              # Равенство
    T_NE = '!='              # Неравенство
    T_LT = 'LT'              # Меньше
    T_GT = 'GT'              # Больше
    T_LTE = 'LTE'            # Меньше или равно
    T_GTE = 'GTE'            # Больше или равно

    # Скобки и запятые
    T_LPAREN = 'LPAREN'      # Открывающая круглая скобка
    T_RPAREN = 'RPAREN'      # Закрывающая круглая скобка
    T_LBRACE = 'LBRACE'      # Открывающая фигурная скобка
    T_RBRACE = 'RBRACE'      # Закрывающая фигурная скобка
    T_LBRACKET = 'LBRACKET'  # Открывающая квадратная скобка
    T_RBRACKET = 'RBRACKET'  # Закрывающая квадратная скобка
    T_COMMA = 'COMMA'        # Запятая
    T_DOT = 'DOT'            # Точка
    T_SEMICOLON = 'SEMICOLON' # Точка с запятой
    T_COLON = 'COLON'        # Двоеточие
    T_EOF = 'EOF'            # Конец файла

    # Общее
    T_IDENTIFIER = 'IDENTIFIER'  # Идентификатор (переменные, функции и т.д.)
    T_EQUAL = 'EQUAL'            # Оператор присваивания

    # Ключевые слова
    T_VAR = 'VAR'            # Объявление переменной
    T_IF = 'IF'              # Условный оператор if
    T_ELSE = 'ELSE'          # Условный оператор else
    T_WHILE = 'WHILE'        # Цикл while
    T_FOR = 'FOR'            # Цикл for
    T_CONTINUE = 'CONTINUE'  # Ключевое слово continue
    T_BREAK = 'BREAK'        # Ключевое слово break
    T_FUNCTION = 'FUNCTION'  # Объявление функции
    T_RETURN = 'RETURN'      # Ключевое слово return


# Константы для идентификации символов
DIGITS = '0123456789'               # Все цифры
LETTERS = string.ascii_letters      # Все буквы латинского алфавита
LETTERS_DIGITS = LETTERS + DIGITS   # Комбинация букв и цифр


class Token:
    """
    Класс Token представляет токен, созданный лексером.
    Содержит тип токена, его значение и позиции в исходном коде.
    """

    def __init__(self, type, value=None, pos_start=None, pos_end=None):
        """
        Инициализация токена.

        Параметры:
            type (TokenType): Тип токена.
            value (any): Значение токена.
            pos_start (Position): Начальная позиция токена в исходном коде.
            pos_end (Position): Конечная позиция токена в исходном коде.
        """
        self.type = type
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
        else:
            self.pos_start = None

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        
        if pos_end:
            self.pos_end = pos_end

    def matches(self, type_, value):
        """
        Проверяет, соответствует ли токен указанному типу и значению.

        Параметры:
            type_ (TokenType): Ожидаемый тип токена.
            value (any): Ожидаемое значение токена.

        Возвращает:
            bool: True, если токен соответствует, иначе False.
        """
        return self.type == type_ and self.value == value

    def __repr__(self):
        """
        Возвращает строковое представление токена для отладки.

        Возвращает:
            str: Строковое представление токена.
        """
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
