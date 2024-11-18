import sys

arg = sys.argv
comand=['']

def asignacion(c):
    if c == '=' or c == '+=' or c == '-=' or c== '*=' or c == '/=':
        return True
    else:
        return False