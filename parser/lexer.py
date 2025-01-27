"""
Модуль лексера для анализа исходного кода.
"""

from parser.token_ import *  # Модуль с определением токенов.
from debug.error_ import *  # Модуль для обработки ошибок.


class Lexer:
    """
    Класс Lexer выполняет лексический анализ исходного кода.
    Он преобразует текст программы в последовательность токенов для дальнейшей обработки.

    Атрибуты:
        fn (str): Имя файла исходного кода.
        code (str): Содержимое исходного кода.
        pos (Position): Текущая позиция в анализируемом коде.
        currentChar (str): Текущий символ, на котором находится лексер.
    """

    def __init__(self, fn, code) -> None:
        """
        Инициализация объекта лексера.

        Параметры:
            fn (str): Имя файла исходного кода.
            code (str): Содержимое исходного кода.
        """
        self.fn = fn
        self.code = code
        self.pos = Position(-1, 0, -1, fn, code)
        self.currentChar = None

        self.advance()

    def advance(self):
        """
        Продвигает текущую позицию на один символ вперед.
        Если достигнут конец строки, устанавливает currentChar в None.
        """
        self.pos.advance(self.currentChar)
        self.currentChar = self.code[self.pos.idx] if self.pos.idx < len(self.code) else None

    def advance_n(self, n):
        """
        Продвигает текущую позицию на n символов вперед.

        Параметры:
            n (int): Количество символов для продвижения.
        """
        for _ in range(n):
            self.advance()

    def is_digital(self):
        """
        Проверяет, является ли текущий символ цифрой.

        Возвращает:
            bool: True, если символ цифра, иначе False.
        """
        return self.currentChar in DIGITS

    def make_tokens(self):
        """
        Основной метод лексера, который преобразует исходный код в последовательность токенов.

        Возвращает:
            list[Token]: Список токенов.
            Error: Объект ошибки, если токенизация завершилась ошибкой.
        """
        tokens = []
        single_char_tokens = {
            '+': TokenType.T_PLUS,
            '-': TokenType.T_MINUS,
            '*': TokenType.T_MULTIPLY,
            '/': TokenType.T_DIVIDE,
            '=': TokenType.T_EQUAL,
            '>': TokenType.T_GT,
            '<': TokenType.T_LT,
            ',': TokenType.T_COMMA,
            '(': TokenType.T_LPAREN,
            ')': TokenType.T_RPAREN,
            '{': TokenType.T_LBRACE,
            '}': TokenType.T_RBRACE,
            ';': TokenType.T_SEMICOLON
        }

        double_char_tokens = {
            '==': TokenType.T_EQ,
            '!=': TokenType.T_NE,
            '>=': TokenType.T_GTE,
            '<=': TokenType.T_LTE,
            '+=': TokenType.T_PLUS_ASSIGN,
            '-=': TokenType.T_MINUS_ASSIGN
        }

        keywords = {
            'true': TokenType.T_TRUE,
            'false': TokenType.T_FALSE,
            'var': TokenType.T_VAR,
            'function': TokenType.T_FUNCTION,
            'return': TokenType.T_RETURN,
            'if': TokenType.T_IF,
            'elseif': TokenType.T_ELSEIF,
            'else': TokenType.T_ELSE
        }

        while self.currentChar is not None:
            if self.currentChar in ' \t\n':  # Пропуск пробелов и пустых символов.
                self.advance()
            elif self.currentChar == '/' and self.peek() == '/':  # Пропуск однострочных комментариев.
                self.skip_comment()
            elif self.currentChar in DIGITS:  # Обработка чисел.
                tokens.append(self.make_number())
            elif self.currentChar == '"':  # Обработка строк.
                tokens.append(self.make_string())
            elif self.currentChar in LETTERS:  # Обработка идентификаторов и ключевых слов.
                tokens.append(self.make_identifier_or_keyword(keywords))
            elif f"{self.currentChar}{self.peek()}" in double_char_tokens:
                tokens.append(Token(double_char_tokens[f"{self.currentChar}{self.peek()}"], pos_start=self.pos))
                self.advance_n(2)
            elif self.currentChar in single_char_tokens:  # Обработка одиночных символов-токенов.
                tokens.append(Token(single_char_tokens[self.currentChar], pos_start=self.pos))
                self.advance()
            else:  # Обработка некорректных символов.
                pos_start = self.pos.copy()
                char = self.currentChar
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f"'{char}'")

        tokens.append(Token(TokenType.T_EOF, pos_start=self.pos))  # Добавление токена конца файла.
        #print(tokens)
        return tokens, None

    def peek(self):
        """
        Возвращает следующий символ, не продвигая текущую позицию.

        Возвращает:
            str: Следующий символ или None, если достигнут конец строки.
        """
        peek_pos = self.pos.idx + 1
        return self.code[peek_pos] if peek_pos < len(self.code) else None

    def skip_comment(self):
        """
        Пропускает символы однострочного комментария.
        """
        while self.currentChar is not None and self.currentChar != "\n":
            self.advance()
        self.advance()

    def make_number(self):
        """
        Создает токен числа (целого или вещественного).

        Возвращает:
            Token: Токен числа.
        """
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.currentChar is not None and self.currentChar in DIGITS + '.':
            if self.currentChar == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.currentChar
            self.advance()

        token_type = TokenType.T_FLOAT if dot_count == 1 else TokenType.T_INT
        return Token(token_type, float(num_str) if dot_count == 1 else int(num_str), pos_start, self.pos)

    def make_string(self):
        """
        Создает токен строки.

        Возвращает:
            Token: Токен строки.
        """
        self.advance()
        string = ''
        while self.currentChar != '"':
            if self.currentChar is None: 
                break
            string += self.currentChar
            self.advance()
        self.advance()
        return Token(TokenType.T_STRING, string, self.pos.copy(), self.pos)

    def make_identifier_or_keyword(self, keywords):
        """
        Создает токен идентификатора или ключевого слова.

        Параметры:
            keywords (dict): Словарь ключевых слов.

        Возвращает:
            Token: Токен идентификатора или ключевого слова.
        """
        id_str = ''
        pos_start = self.pos.copy()

        while self.currentChar is not None and self.currentChar in LETTERS_DIGITS + '_':
            id_str += self.currentChar
            self.advance()

        tok_type = keywords.get(id_str, TokenType.T_IDENTIFIER)
        return Token(tok_type, id_str, pos_start, self.pos)
