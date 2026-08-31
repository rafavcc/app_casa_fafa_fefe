def meu_decorador(funcao):
    def embrulho():
        print("Antes da função")
        funcao()
        print("Depois da função")

    return embrulho


@meu_decorador
def ola():
    print("Olá, Rafael!")


ola()