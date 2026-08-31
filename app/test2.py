from time import sleep
from datetime import datetime

def decoradora(funcao):
    def wrapper(a,b):
        inicio = datetime.now()
        resultado = funcao(a,b)
        fim = datetime.now()
        diferenca = fim - inicio
        print(diferenca)
        return resultado
    return wrapper

@decoradora
def soma(first : int, second : int):
    print("FUNCAO DE SOMA")
    sleep(2)
    return sum([first,second])

print(soma(2,5))