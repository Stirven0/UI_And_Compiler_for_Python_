import argparse
import importlib
# Definimos los tipos de tokens
TOKEN_TYPES = {
    'NUMBER': 'NUMBER',
    'STRING': 'STRING',
    'BOOLEAN': 'BOOLEAN',
    'NULL': 'NULL',
    'IDENTIFIER': 'IDENTIFIER',
    'OPERATOR': 'OPERATOR',
    'RELATIONAL': 'RELATIONAL',
    'ASSIGNMENT': 'ASSIGNMENT',
    'DELIMITERS': 'DELIMITERS',
    'COMMENT': 'COMMENT',
    'EOF': 'EOF',
    'KEYWORD': 'KEYWORD',
    'INDENT': 'INDENT',
    'DEDENT': 'DEDENT',
    'MEMBER_ACCESS': 'MEMBER_ACCESS'
}

# Definimos las palabras clave
KEYWORDS = {
    'if', 'else', 'elif', 'while', 'for',  'def', 'class', 'return', 'import'
}

# Definimos los operadores relacionales
RELATIONAL_OPERATORS = {'==', '!=', '<=', '>=', '<', '>'}

# Definimos los operadores de asignación
ASSIGNMENT_OPERATORS = {'=', '+=', '-=', '*=', '/='}
BOOLEAN_LITERALS = {'True', 'False'}
NULL_LITERAL = {'None', 'Null'}
LOGICAL_OPERATORS = {'and', 'or', 'not'}


class Lexer:
    def __init__(self, input_string):
        self.input = input_string
        self.position = 0
        self.current_char = self.input[self.position] if self.input else None
        self.indent_stack = [0]  # Pila para manejar niveles de indentación
        self.line_start = True   # Para manejar la detección de indentaciones en nuevas líneas

    def tokens(self):
        tokens = []
        token = self.get_next_token()
        
        while token['type'] != TOKEN_TYPES['EOF']:
            tokens.append(token)
            token = self.get_next_token()
        
        tokens.append(token)
        return tokens
            
    def advance(self):
        """Mueve la posición un carácter hacia adelante."""
        self.position += 1
        if self.position >= len(self.input):
            self.current_char = None
        else:
            self.current_char = self.input[self.position]

    def peek(self):
        """Devuelve el siguiente carácter sin avanzar la posición."""
        peek_pos = self.position + 1
        if peek_pos >= len(self.input):
            return None
        return self.input[peek_pos]

    def skip_whitespace(self):
        """Ignora los espacios en blanco fuera de indentación/dedentación."""
        while self.current_char is not None and self.current_char.isspace() and self.current_char not in '\n\t':
            self.advance()

    def number(self):
        """Reconoce un número."""
        num_str = ''
        while self.current_char is not None and self.current_char.isdigit():
            num_str += self.current_char
            self.advance()
        return {'type': TOKEN_TYPES['NUMBER'], 'value': int(num_str)}

    def string(self, quote_type):
        """Reconoce una cadena de texto."""
        string_val = ''
        self.advance()  # Saltar la comilla inicial
        while self.current_char is not None and self.current_char != quote_type:
            string_val += self.current_char
            self.advance()
        self.advance()  # Saltar la comilla final
        return {'type': TOKEN_TYPES['STRING'], 'value': string_val}

    LOGICAL_OPERATORS = {'and', 'or', 'not'}

    def identifier_or_literal(self):
        """Reconoce un identificador, palabra clave, booleano o nulo."""
        id_str = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()
        if id_str in KEYWORDS:
            return {'type': TOKEN_TYPES['KEYWORD'], 'value': id_str}
        elif id_str in LOGICAL_OPERATORS:
            return {'type': TOKEN_TYPES['OPERATOR'], 'value': id_str}
        elif id_str in BOOLEAN_LITERALS:
            return {'type': TOKEN_TYPES['BOOLEAN'], 'value': id_str}
        elif id_str in NULL_LITERAL:
            return {'type': TOKEN_TYPES['NULL'], 'value': None}
        else:
            return {'type': TOKEN_TYPES['IDENTIFIER'], 'value': id_str}


    def handle_indent_dedent(self):
        """Maneja indentación y dedentación."""
        indent_level = 0
        while self.current_char == ' ' or self.current_char == '\t':
            if self.current_char == ' ':
                indent_level += 1
            elif self.current_char == '\t':
                indent_level += 4  # Asumiendo tabulación como 4 espacios
            self.advance()

        last_indent = self.indent_stack[-1]

        if indent_level > last_indent:
            self.indent_stack.append(indent_level)
            return {'type': TOKEN_TYPES['INDENT'], 'value': indent_level}
        elif indent_level < last_indent:
            while indent_level < self.indent_stack[-1]:
                self.indent_stack.pop()
            return {'type': TOKEN_TYPES['DEDENT'], 'value': self.indent_stack[-1]}

        return None

    def relational_operator(self):
        """Reconoce un operador relacional."""
        rel_op_str = self.current_char
        if self.peek() in ('=', '<', '>'):
            rel_op_str += self.peek()
            self.advance()
        self.advance()
        return {'type': TOKEN_TYPES['RELATIONAL'], 'value': rel_op_str}

    def assignment_operator(self):
        """Reconoce un operador de asignación."""
        assign_op_str = self.current_char
        if self.peek() == '=':
            assign_op_str += self.peek()
            self.advance()
        self.advance()
        return {'type': TOKEN_TYPES['ASSIGNMENT'], 'value': assign_op_str}

    def comment(self):
        """Reconoce un comentario."""
        comment_str = ''
        while self.current_char is not None and self.current_char != '\n':
            comment_str += self.current_char
            self.advance()
        return {'type': TOKEN_TYPES['COMMENT'], 'value': comment_str}

    def get_next_token(self):
        """Obtiene el siguiente token de la entrada."""
        while self.current_char is not None:
            if self.current_char.isspace():
                if self.current_char == '\n':
                    self.advance()
                    self.line_start = True
                    indent_token = self.handle_indent_dedent()
                    if indent_token:
                        return indent_token
                else:
                    self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.number()

            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier_or_literal()

            if self.current_char in '+-*/':
                if self.peek() == '=':
                    return self.assignment_operator()
                else:
                    token = {'type': TOKEN_TYPES['OPERATOR'], 'value': self.current_char}
                    self.advance()
                    return token

            if self.current_char == '=':
                if self.peek() == '=':
                    return self.relational_operator()
                else:
                    return self.assignment_operator()

            if self.current_char in '!<>':
                return self.relational_operator()

            if self.current_char in '(){}[],:.':
                if self.current_char == '.':
                    token = {'type': TOKEN_TYPES['MEMBER_ACCESS'], 'value': self.current_char}
                else:
                    token = {'type': TOKEN_TYPES['DELIMITERS'], 'value': self.current_char}
                self.advance()
                return token

            if self.current_char == '\'' or self.current_char == '\"':
                return self.string(self.current_char)

            if self.current_char == '#':
                return self.comment()

            raise Exception(f'Error léxico: carácter no reconocido "{self.current_char}"')

        # EOF: cuando llegamos al final de la cadena de entrada
        if len(self.indent_stack) > 1:
            self.indent_stack.pop()
            return {'type': TOKEN_TYPES['DEDENT'], 'value': None}

        return {'type': TOKEN_TYPES['EOF'], 'value': None}

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, expected):
        raise Exception(f"Error de sintaxis: se esperaba {expected}, pero se encontró {self.current_token['value']}")

    def advance(self):
        """Avanza al siguiente token."""
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        """Verifica si el tipo del token actual coincide con el esperado."""
        if isinstance(self.current_token, list):  # Por si `handle_indent_dedent` devuelve múltiples dedents
            self.current_token = self.current_token.pop(0)

        if self.current_token['type'] == token_type:
            self.advance()
        else:
            self.error(token_type)

    def parse(self):
        """Regla de inicio del programa: un conjunto de declaraciones."""
        statements = []
        while self.current_token['type'] != TOKEN_TYPES['EOF']:
            statement = self.statement()
            if statement:
                statements.append(statement)
        return {'type': 'PROGRAM', 'body': statements}

    def statement(self):
        """Reconoce una declaración, como una asignación, import, o una declaración de control."""
        if self.current_token['type'] == TOKEN_TYPES['KEYWORD']:
            if self.current_token['value'] == 'if':
                return self.if_statement()
            elif self.current_token['value'] == 'while':
                return self.while_statement()
            elif self.current_token['value'] == 'def':
                return self.function_definition()
            elif self.current_token['value'] == 'import':  # Añadir manejo para `import`
                return self.import_statement()
            elif self.current_token['value'] == 'return':
                return self.parse_return()
        elif self.current_token['type'] == TOKEN_TYPES['IDENTIFIER']:
            return self.assignment_statement()
        else:
            self.error('declaración válida')

    def import_statement(self):
        """Reconoce una declaración de `import`."""
        self.eat(TOKEN_TYPES['KEYWORD'])  # Comemos la palabra clave `import`
        module_name = self.current_token
        self.eat(TOKEN_TYPES['IDENTIFIER'])  # Comemos el identificador que sigue a `import`
        return {'type': 'IMPORT', 'module': module_name['value']}
    
    def return_statement(self):
        self.eat(TOKEN_TYPES['KEYWORD'])
        
        return
    
    def assignment_statement(self):
        """Reconoce una declaración de asignación."""
        identifier = self.current_token
        self.eat(TOKEN_TYPES['IDENTIFIER'])  # Comemos el identificador
        self.eat(TOKEN_TYPES['ASSIGNMENT'])  # Comemos el símbolo de asignación '='
        expr = self.expression()  # Obtenemos la expresión del lado derecho
        return {'type': 'ASSIGNMENT', 'identifier': identifier['value'], 'expression': expr}

    def expression(self):
        """Reconoce una expresión."""
        node = self.logical_or()

        return node


    def logical_or(self):
        """Reconoce expresiones que incluyen 'or'."""
        node = self.logical_and()

        while self.current_token['value'] == 'or':
            token = self.current_token
            self.eat(TOKEN_TYPES['OPERATOR'])
            node = {'type': 'LOGICAL_OP', 'operator': token['value'], 'left': node, 'right': self.logical_and()}

        return node

    def logical_and(self):
        """Reconoce expresiones que incluyen 'and'."""
        node = self.equality()

        while self.current_token['value'] == 'and':
            token = self.current_token
            self.eat(TOKEN_TYPES['OPERATOR'])
            node = {'type': 'LOGICAL_OP', 'operator': token['value'], 'left': node, 'right': self.equality()}

        return node

    def equality(self):
        """Reconoce operadores de igualdad '==' y '!='."""
        node = self.relational()
# error
        while self.current_token['value'] in ('==', '!='):
            token = self.current_token
            self.eat(TOKEN_TYPES['RELATIONAL'])
            node = {'type': 'EQUALITY_OP', 'operator': token['value'], 'left': node, 'right': self.relational()}

        return node

    def relational(self):
        """Reconoce operadores relacionales ('<', '>', '<=', '>=')."""
        node = self.term()

        while self.current_token['value'] in ('<', '>', '<=', '>='):
            token = self.current_token
            self.eat(TOKEN_TYPES['RELATIONAL'])
            node = {'type': 'RELATIONAL_OP', 'operator': token['value'], 'left': node, 'right': self.term()}

        return node
    
    def term(self):
        """Reconoce un término, que puede ser un número, identificador, o una subexpresión."""
        token = self.current_token

        if token['type'] == TOKEN_TYPES['NUMBER']:
            self.eat(TOKEN_TYPES['NUMBER'])
            return {'type': 'NUMBER', 'value': token['value']}
        elif token['type'] == TOKEN_TYPES['STRING']:
            self.eat(TOKEN_TYPES['STRING'])
            return {'type': 'STRING', 'value': token['value']}
        elif token['type'] == TOKEN_TYPES['IDENTIFIER']:
            result = {'type': 'IDENTIFIER', 'value': token['value']}
            self.eat(TOKEN_TYPES['IDENTIFIER'])

            # Manejo del acceso a miembros ('.')
            while self.current_token['type'] == TOKEN_TYPES['MEMBER_ACCESS']:
                self.eat(TOKEN_TYPES['MEMBER_ACCESS'])  # Comemos el '.'
                member = self.current_token
                self.eat(TOKEN_TYPES['IDENTIFIER'])  # Comemos el identificador después del '.'
                result = {'type': 'MEMBER_ACCESS', 'object': result, 'member': member['value']}

            return result
        elif token['type'] == TOKEN_TYPES['BOOLEAN']:
            self.eat(TOKEN_TYPES['BOOLEAN'])
            return {'type': 'BOOLEAN', 'value': token['value']}
        elif token['type'] == TOKEN_TYPES['NULL']:
            self.eat(TOKEN_TYPES['NULL'])
            return {'type': 'NULL', 'value': None}
        elif token['value'] == '[':
            self.eat(TOKEN_TYPES['DELIMITERS'])  # Comemos '('
            expr = self.expression()
            self.eat(TOKEN_TYPES['DELIMITERS'])  # Comemos ')'
            return expr
        else:
            self.error('número, cadena, identificador, o expresión entre paréntesis')

    def parse_return(self):
        """Maneja la declaración return."""
        token = self.current_token
        self.eat(TOKEN_TYPES['KEYWORD'])  # Come la palabra clave 'return'
    
        if self.current_token['type'] != TOKEN_TYPES['EOF'] and self.current_token['type'] != TOKEN_TYPES['DELIMITERS']:
            return_expr = self.expression()  # La expresión que está retornando
        else:
            return_expr = None  # Si no hay expresión, retorna None
    
        return {'type': 'RETURN_STATEMENT', 'value': return_expr}

    def if_statement(self):
        """Reconoce una declaración `if`, junto con `elif` y `else` opcionales."""
        self.eat(TOKEN_TYPES['KEYWORD'])  # Consume la palabra clave `if`
        condition = self.expression()  # Obtiene la condición
        self.eat(TOKEN_TYPES['DELIMITERS'])  # Consume ':'
        if_block = self.block()  # Obtiene el bloque de código para `if`

        # Manejo de `elif` opcionales
        elif_blocks = []
        while self.current_token['type'] == TOKEN_TYPES['KEYWORD'] and self.current_token['value'] == 'elif':
            self.eat(TOKEN_TYPES['KEYWORD'])  # Consume `elif`
            elif_condition = self.expression()  # Condición para `elif`
            self.eat(TOKEN_TYPES['DELIMITERS'])  # Consume ':'
            elif_block = self.block()  # Bloque de código para `elif`
            elif_blocks.append({'condition': elif_condition, 'block': elif_block})

        # Manejo de `else` opcional
        else_block = None
        if self.current_token['type'] == TOKEN_TYPES['KEYWORD'] and self.current_token['value'] == 'else':
            self.eat(TOKEN_TYPES['KEYWORD'])  # Consume `else`
            self.eat(TOKEN_TYPES['DELIMITERS'])  # Consume ':'
            else_block = self.block()  # Bloque de código para `else`

        return {
            'type': 'IF',
            'condition': condition,
            'if_block': if_block,
            'elif_blocks': elif_blocks,
            'else_block': else_block
        }

    def while_statement(self):
        """Reconoce una declaración `while`."""
        self.eat(TOKEN_TYPES['KEYWORD'])  # Comemos el `while`
        condition = self.expression()  # Obtenemos la condición
        self.eat(TOKEN_TYPES['DELIMITERS'])  # Comemos ':'
        block = self.block()  # Reconocemos el bloque de código
        return {'type': 'WHILE', 'condition': condition, 'block': block}

    def function_definition(self):
        """Reconoce una declaración de función `def`."""
        self.eat(TOKEN_TYPES['KEYWORD'])  # Comemos el `def`
        func_name = self.current_token
        self.eat(TOKEN_TYPES['IDENTIFIER'])  # Comemos el nombre de la función
        self.eat(TOKEN_TYPES['DELIMITERS'])  # Comemos '('
        params = []
        if self.current_token['type'] == TOKEN_TYPES['IDENTIFIER']:
            params.append(self.current_token['value'])
            self.eat(TOKEN_TYPES['IDENTIFIER'])
            while self.current_token['value'] == ',':
                self.eat(TOKEN_TYPES['DELIMITERS'])  # Comemos ','
                params.append(self.current_token['value'])
                self.eat(TOKEN_TYPES['IDENTIFIER'])
        self.eat(TOKEN_TYPES['DELIMITERS'])  # Comemos ')'
        self.eat(TOKEN_TYPES['DELIMITERS'])  # Comemos ':'
        block = self.block()  # Reconocemos el bloque de código
        return {'type': 'FUNCTION_DEF', 'name': func_name['value'], 'params': params, 'block': block}

    def block(self):
        """Reconoce un bloque de código."""
        statements = []
        self.eat(TOKEN_TYPES['INDENT'])  # Comemos la indentación

        while self.current_token['type'] != TOKEN_TYPES['DEDENT']:
            statement = self.statement()
            if statement:
                statements.append(statement)

        self.eat(TOKEN_TYPES['DEDENT'])  # Comemos la dedentación
        return {'type': 'BLOCK', 'body': statements}

class SemanticAnalyzer:
    def __init__(self, parse_tree):
        self.symbol_table = {}
        self.analyze(parse_tree)

    def analyze(self, node):
        # if isinstance(node, list):
        #     for item in node:
        #         self.analyze(item)
        #     return
        method_name = f'analyze_{node["type"].lower()}'
        method = getattr(self, method_name, self.generic_analyze)
        return method(node)


    def generic_analyze(self, node):
        raise Exception(f"No hay método de análisis semántico para {node['type']}")

    def analyze_program(self, node):
        for statement in node['body']:
            self.analyze(statement)

    def analyze_assignment(self, node):
        identifier = node['identifier']
        expression = node['expression']
        value = self.analyze(expression)
        self.symbol_table[identifier] = value

    def analyze_string(self, node):
        # Simplemente devolvemos el valor de la cadena
        return node['value']

    def analyze_expression(self, node):
        if node['type'] == 'NUMBER':
            return node['value']
        elif node['type'] == 'STRING':
            return node['value']
        elif node['type'] == 'IDENTIFIER':
            if node['value'] not in self.symbol_table:
                raise Exception(f"Variable no declarada: {node['value']}")
            return self.symbol_table[node['value']]
        elif node['type'] == 'LOGICAL_OP':
            left = self.analyze(node['left'])
            right = self.analyze(node['right'])
            if node['operator'] == 'and':
                return left and right
            elif node['operator'] == 'or':
                return left or right
        elif node['type'] == 'EQUALITY_OP':
            left = self.analyze(node['left'])
            right = self.analyze(node['right'])
            if node['operator'] == '==':
                return left == right
            elif node['operator'] == '!=':
                return left != right
        elif node['type'] == 'RELATIONAL_OP':
            left = self.analyze(node['left'])
            right = self.analyze(node['right'])
            if node['operator'] == '<':
                return left < right
            elif node['operator'] == '>':
                return left > right
            elif node['operator'] == '<=':
                return left <= right
            elif node['operator'] == '>=':
                return left >= right
        else:
            raise Exception(f"Tipo de expresión desconocido: {node['type']}")

    def analyze_identifier(self, node):
            identifier = node['value']
            if identifier not in self.symbol_table:
                raise Exception(f"Variable no declarada: {identifier}")
            return self.symbol_table[identifier]

    def analyze_logical_op(self, node):
        left = self.analyze(node['left'])
        right = self.analyze(node['right'])
        if node['operator'] == 'and':
            return left and right
        elif node['operator'] == 'or':
            return left or right
        else:
            raise Exception(f"Operador lógico desconocido: {node['operator']}")
    
    def analyze_equality_op(self, node):
        left = self.analyze(node['left'])
        right = self.analyze(node['right'])
        if node['operator'] == '==':
            return left == right
        elif node['operator'] == '!=':
            return left != right
        else:
            raise Exception(f"Operador de igualdad desconocido: {node['operator']}")

    def analyze_relational_op(self, node):
        left = self.analyze(node['left'])
        right = self.analyze(node['right'])
        if node['operator'] == '<':
            return left < right
        elif node['operator'] == '>':
            return left > right
        elif node['operator'] == '<=':
            return left <= right
        elif node['operator'] == '>=':
            return left >= right
        else:
            raise Exception(f"Operador relacional desconocido: {node['operator']}")


    def analyze_member_access(self, node):
        object_node = node['object']
        member = node['member']
        object_value = self.analyze(object_node)
        if isinstance(object_value, dict) and member in object_value:
            return object_value[member]
        elif object_node['type'] == 'IDENTIFIER' and object_node['value'] in self.symbol_table:
            module = self.symbol_table[object_node['value']]
            if isinstance(module, dict) and member in module:
                return module[member]
        raise Exception(f"Acceso a miembro inválido o miembro no encontrado: {member}")

    def analyze_if(self, node):
        condition = self.analyze(node['condition'])
        if_block = self.analyze(node['if_block'])
        elif_blocks = [self.analyze(elif_block) for elif_block in node.get('elif_blocks', [])]
        else_block = self.analyze(node['else_block']) if node.get('else_block') else None
        return {
            'condition': condition,
            'if_block': if_block,
            'elif_blocks': elif_blocks,
            'else_block': else_block
        }

    def analyze_while(self, node):
        condition = self.analyze(node['condition'])
        block = self.analyze(node['block'])
        return {'condition': condition, 'block': block}

    def analyze_function_def(self, node):
        func_name = node['name']
        params = node['params']
        block = node['block']
        # Registrar la función en la tabla de símbolos
        self.symbol_table[func_name] = {'params': params, 'block': block}
        
        # Analizar y registrar los parámetros en la tabla de símbolos
        for param in params:
            self.symbol_table[param] = None  # Puedes inicializarlo con algún valor por defecto si es necesario
        
        # Analizar el bloque de la función
        for statement in block['body']:
            self.analyze(statement)
        
        return {'name': func_name, 'params': params, 'block': block}


    def analyze_return_statement(self, node):
        return self.analyze(node['value'])
    

    def analyze_import(self, node):
        module_name = node['module']
        print(f"Importando módulo: {module_name}")
        module = importlib.import_module(module_name)
        # Registrar el módulo importado y sus miembros en la tabla de símbolos
        self.symbol_table[module_name] = {name: getattr(module, name) for name in dir(module) if not name.startswith('_')}
        return

def main():
    print('llame a este archivo usando el comando "python Lexer.py -f ruta/del/archivo.py"\npara analizar codigo no estatico')
    parser = argparse.ArgumentParser(description='Compyler for Python By: Stirven')
    parser.add_argument('-f', '--file', type=str, help='Archivo a procesar')
    parser.add_argument('-l', '--lexer', type=str, help='Retorna una lista de TOKENS')
    parser.add_argument('-p', '--parser', type=str, help='Retorna el arbol sintactico en formato Json')
    parser.add_argument('-s', '--semantic', type=str, help='Retorna latabla semantica')
    args = parser.parse_args()
    if args.file:
        with open(args.file, 'r') as file:
            input_string = file.read()
    else:
        input_string = input("Ingrese el código a analizar: ")

    
    lexer = Lexer(input_string)
    
    if args.lexer:
        with open("outputLexer.txt", "w") as file:
            file.write(lexer.tokens())
            
    parser = Parser(lexer)
    
    if args.parser:
        with open("outputParser.txt", "w") as file:
            file.write(parser.parse())
            
    semantic_analyzer = SemanticAnalyzer(parser.parse())
    
    if args.semantic:
        with open("outputSemantic.txt", "w") as file:
            file.write(lexer.tokens())

        
    # parse_tree = parser.parse()
    # semantic_analyzer = SemanticAnalyzer(parse_tree)
    # for token in lexer.tokens():
    #     print(token)
    # print(lexer.tokens())
    print(parser.parse())
        

if __name__ == '__main__':
    main()
