from time import sleep

def wrapper(funcao):
    def wrapper_inside(*args):
        print("1a linha")
        resultado = funcao(*args)
        print("2a linha")
        return resultado
    return wrapper_inside

@wrapper
def soma(*args):
    print("FUNCAO DE SOMA")
    sleep(2)
    return sum(args)

a = soma(1,2,3)

print(a)