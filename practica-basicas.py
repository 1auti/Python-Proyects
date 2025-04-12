"""
Ejercicio 1:
Crea una función calculadora que reciba dos números y un operador (+, -, *, /)
y devuelva el resultado de la operación.
"""
import math


def calculadora(valor1, valor2, operacion):
    if operacion == '+':
        return valor1 + valor2
    elif operacion == '-':
        return valor1 - valor2
    elif operacion == '*':
        return valor1 * valor2
    elif operacion == '/':
        if valor2 != 0:
            return valor1 / valor2
        else:
            return "Error: División por cero"
    else:
        return "Operación no válida"

# Ejemplos de uso:
# print(calculadora(10, 5, '+'))  # 15
# print(calculadora(10, 5, '-'))  # 5
# print(calculadora(10, 5, '*'))  # 50
# print(calculadora(10, 0, '/'))  # Error: División por cero
# print(calculadora(10, 5, '/'))  # 2.0


"""
Ejercicio 2
Crea una funcion que calcula si es numero primo
"""

def es_primo(numero):
    if numero <= 1:
        return False

    i = 2
    while i < numero:
        if numero % i == 0:
            return "No es primo"
        i += 1

    return "Es primo"

# Pruebas
# print(es_primo(7))  # True
# print(es_primo(10)) # False

"""
Ejercicio 3 
Crea una función que cuente la frecuencia de cada palabra en un texto dado.
"""

import string

def calcular_frecuencia_palabras(texto:str):
   #Convertirmos las paalbras en minisculas y las separamos
    palabras = texto.lower().split()
    frecuencia = {}

    for palabra in palabras:
        if palabra in frecuencia:
         frecuencia[palabra] += 1
        else:
         frecuencia[palabra] = 1

    return frecuencia


# Ejemplo de uso
# texto = "Hola mundo hola universo mundo mundo"
# resultado = calcular_frecuencia_palabras(texto)
# print(resultado)

"""
Ejercicio 4: Palindromo
Escribe una función que determine si una palabra o frase es un palíndromo (se lee igual de izquierda a derecha que de derecha a izquierda).
"""

def es_palindromo(texto:str):

  # Pasamos a minúsculas
  texto.lower()

  # Quitamos espacios y puntuación
  texto = texto.translate(str.maketrans('',"",string.punctuation)).replace("",'')

  #Compara el texto original con alrevez
  return texto == texto[::-1]

# print(es_palindromo("Anita lava la tina"))



"""
Ejercicio 5: Lista de Fibonacci
Crea una función que genere una lista con los primeros n números de la secuencia de Fibonacci.
"""

def generar_fibonacci(n:int) -> list:

    if n < 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0,1]

    fibonacci = [0,1]
    #devuelve la cantidad que hay en la lista
    while len(fibonacci) < n:
         siguiente = fibonacci[-1]  + fibonacci[-2]
         fibonacci.append(siguiente)

    return  fibonacci


# print(generar_fibonacci(10))

"""
Ejercicio 6: Ordenamiento de lista
Implementa el algoritmo de ordenamiento burbuja para ordenar una lista de números.
"""

def ordenamiento_burbuja(lista:list) -> list:
    n = len(lista)
    for i in range(n):

        for j in range(0,n - i - 1 ):
            if lista[j] > lista[j + 1]:
                # Intercambio
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
    return lista


# numeros = [5, 3, 8, 1, 2]
# ordenada = ordenamiento_burbuja(numeros)
# print("Lista ordenada:", ordenada)


"""
Ejercicio 7: Gestión de estudiantes
Crea un programa que permita añadir estudiantes con sus notas, calcular promedios y mostrar los estudiantes ordenados por promedio.
"""


class Estudiante:
    #self = el objeto que estás construyendo o usando
    def __init__(self, nombre, notas):
        self.nombre = nombre
        self.notas = notas
        self.promedio = sum(notas) / len(notas) if notas else 0

    def __str__(self):
        return f"{self.nombre}: {self.promedio:.2f}"


class GestorEstudiantes:
    def __init__(self):
        self.estudiantes = []

    def agregar_estudiante(self, nombre, notas):
        estudiante = Estudiante(nombre, notas)
        self.estudiantes.append(estudiante)

    def mostrar_estudiantes(self):
        if not self.estudiantes:
            return "No hay estudiantes registrados"

        # Ordenar por promedio (de mayor a menor)
        self.estudiantes.sort(key=lambda est: est.promedio, reverse=True)

        """
        lambda est: est.promedio: Es una función que toma un objeto est (un estudiante) y devuelve el atributo promedio de ese estudiante.
        key: Es el argumento de la función sort que especifica cómo se debe ordenar cada elemento. En este caso, la lista se ordena por el atributo promedio de cada 
        estudiante.
        reverse=True: Esto indica que se debe ordenar en orden descendente (de mayor a menor).
        """

        resultado = "Lista de estudiantes (ordenados por promedio):\n"
        for estudiante in self.estudiantes:
            resultado += str(estudiante) + "\n"

        return resultado


# Ejemplo de uso
gestor = GestorEstudiantes()
gestor.agregar_estudiante("Ana", [8, 7, 9])
gestor.agregar_estudiante("Pedro", [6, 5, 7])
gestor.agregar_estudiante("Luis", [9, 10, 8])

print(gestor.mostrar_estudiantes())


"""
Ejercicio 8: Validador de contraseñas
Crea una función que verifique si una contraseña cumple con ciertos requisitos: al menos 8 caracteres, una mayúscula, una minúscula y un número.
"""


def validar_contraseña(contraseña):
    if len(contraseña) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"

    tiene_mayuscula = False
    tiene_minuscula = False
    tiene_numero = False

    for c in contraseña:
        if c.isupper():
            tiene_mayuscula = True
        elif c.islower():
            tiene_minuscula = True
        elif c.isdigit():
            tiene_numero = True

    if not tiene_mayuscula:
        return False, "La contraseña debe tener al menos una letra mayúscula"
    if not tiene_minuscula:
        return False, "La contraseña debe tener al menos una letra minúscula"
    if not tiene_numero:
        return False, "La contraseña debe tener al menos un número"

    return True, "Contraseña válida"


# Ejemplos de uso
print(validar_contraseña("abc123"))  # (False, "La contraseña debe tener al menos 8 caracteres")
print(validar_contraseña("abcdefgh"))  # (False, "La contraseña debe tener al menos una letra mayúscula")
print(validar_contraseña("ABCDEFGH"))  # (False, "La contraseña debe tener al menos una letra minúscula")
print(validar_contraseña("Abcdefgh"))  # (False, "La contraseña debe tener al menos un número")
print(validar_contraseña("Abcdef123"))  # (True, "Contraseña válida")

