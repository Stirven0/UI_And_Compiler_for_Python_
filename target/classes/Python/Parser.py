from Lexer import Lexer
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        """Consume el token actual si es del tipo esperado, si no lanza un error."""
        if self.current_token['type'] == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f"Error de sintaxis: se esperaba {token_type}, pero se encontró {self.current_token['type']}")

    def program(self):
        """Regla de producción principal para un programa completo."""
        while self.current_token['type'] != TOKEN_TYPES['EOF']:
            self.statement()

    def statement(self):
        """Regla para manejar las declaraciones o sentencias."""
        if self.current_token['type'] == TOKEN_TYPES['KEYWORD']:
            if self.current_token['value'] == 'if':
                self.if_statement()
            elif self.current_token['value'] == 'while':
                self.while_statement()
            elif self.current_token['value'] == 'for':
                self.for_statement()
            elif self.current_token['value'] == 'def':
                self.function_definition()
            else:
                self.expression()
        else:
            self.expression()

    def if_statement(self):
        """Regla de producción para una sentencia if."""
        self.eat(TOKEN_TYPES['KEYWORD'])  # 'if'
        self.expression()  # condición
        self.block()  # bloque de código

        if self.current_token['type'] == TOKEN_TYPES['KEYWORD'] and self.current_token['value'] == 'else':
            self.eat(TOKEN_TYPES['KEYWORD'])  # 'else'
            self.block()  # bloque de código del else

    def while_statement(self):
        """Regla para la sentencia while."""
        self.eat(TOKEN_TYPES['KEYWORD'])  # 'while'
        self.expression()  # condición
        self.block()  # bloque de código

    def for_statement(self):
        """Regla para la sentencia for."""
        self.eat(TOKEN_TYPES['KEYWORD'])  # 'for'
        self.expression()  # declaración inicial
        self.eat(TOKEN_TYPES['KEYWORD'])  # 'in'
        self.expression()  # rango o iterable
        self.block()  # bloque de código

    def function_definition(self):
        """Regla para la definición de funciones."""
        self.eat(TOKEN_TYPES['KEYWORD'])  # 'def'
        self.eat(TOKEN_TYPES['IDENTIFIER'])  # nombre de la función
        self.eat(TOKEN_TYPES['DELIMITERS'])  # '('
        self.parameters()  # parámetros opcionales
        self.eat(TOKEN_TYPES['DELIMITERS'])  # ')'
        self.block()  # cuerpo de la función

    def parameters(self):
        """Regla para los parámetros de una función."""
        if self.current_token['type'] == TOKEN_TYPES['IDENTIFIER']:
            self.eat(TOKEN_TYPES['IDENTIFIER'])  # primer parámetro
            while self.current_token['type'] == TOKEN_TYPES['DELIMITERS'] and self.current_token['value'] == ',':
                self.eat(TOKEN_TYPES['DELIMITERS'])  # coma
                self.eat(TOKEN_TYPES['IDENTIFIER'])  # siguiente parámetro

    def block(self):
        """Regla para un bloque de código."""
        self.eat(TOKEN_TYPES['DELIMITERS'])  # '{'
        while self.current_token['type'] != TOKEN_TYPES['DELIMITERS'] or self.current_token['value'] != '}':
            self.statement()
        self.eat(TOKEN_TYPES['DELIMITERS'])  # '}'

    def expression(self):
        """Regla para las expresiones."""
        self.term()
        while self.current_token['type'] == TOKEN_TYPES['OPERATOR']:
            self.eat(TOKEN_TYPES['OPERATOR'])
            self.term()

    def term(self):
        """Regla para manejar términos."""
        if self.current_token['type'] == TOKEN_TYPES['NUMBER']:
            self.eat(TOKEN_TYPES['NUMBER'])
        elif self.current_token['type'] == TOKEN_TYPES['STRING']:
            self.eat(TOKEN_TYPES['STRING'])
        elif self.current_token['type'] == TOKEN_TYPES['BOOLEAN']:
            self.eat(TOKEN_TYPES['BOOLEAN'])
        elif self.current_token['type'] == TOKEN_TYPES['IDENTIFIER']:
            self.eat(TOKEN_TYPES['IDENTIFIER'])
        elif self.current_token['type'] == TOKEN_TYPES['DELIMITERS'] and self.current_token['value'] == '(':
            self.eat(TOKEN_TYPES['DELIMITERS'])
            self.expression()
            self.eat(TOKEN_TYPES['DELIMITERS'])  # ')'
        else:
            raise Exception(f"Error de sintaxis: token inesperado {self.current_token}")

# Ejemplo de uso
lexer = Lexer("if x == 10: print(x)")
parser = Parser(lexer)
parser.program()
