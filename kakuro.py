# --- IMPORTACIÓN DE LIBRERÍAS ---
import itertools as it # Funciones de combinaciones y permutaciones
from collections import defaultdict # Para inicializar diccionarios en el que el valor va a ser un elemento por defecto
from collections import deque # Para usar colas doblemente terminadas
import copy # Para hacer un copiado de estructuras más complejas

# --- LECTURA DE DATOS ---
# Dominio de valores posibles para las celdas (1 a 9)
dom = set(range(1, 10))
# Identificadores de columnas del tablero
idCols = "ABCDEFGHI"

# Producto cartesiano de números y columnas para crear claves
keys = list(it.product(dom, idCols))
# Claves en formato "LetraNúmero" (ej: "A1")
strKeys = [f"{key[1]}{key[0]}" for key in keys]

# Diccionario con dominio completo para cada celda inicialmente
vars = {key: dom.copy() for key in strKeys}

# Lectura del archivo con el código del tablero y valores iniciales por celda
with open('c:/Juan UTP/Programación III/python/board3.txt', 'r') as f:
  code = f.readline().strip()  # Código identificador del tablero
  for key in vars.keys():
    valor = f.readline().strip()
    # Si la celda es negra o bloqueada se asigna {0}
    if "0" in valor:
      vars[key] = {int(0)}
    # Si la celda contiene pista o restricción se asigna el string con espacio
    if " " in valor:
      vars[key] = {valor}

# --- FUNCIONES DE CONSTRUCCIÓN ---

# Definición de restricciones de columnas: obtiene grupos de celdas blancas sin bloqueos ni pistas
def DefColsConstraints(idCols, dom):
  colsconstraints = []
  for id in idCols:
    constraintsVars = [f"{id}{i}" for i in dom]
    # Filtrar celdas bloqueadas o con pista
    for key in list(constraintsVars):
      if 0 in vars.get(key, []) or any(" " in str(s) for s in vars.get(key, [])):
        constraintsVars.remove(key)
    colsconstraints.append(constraintsVars)
  return colsconstraints

# Definición de restricciones de filas: obtiene grupos de celdas blancas sin bloqueos ni pistas
def DefRowsConstraints(idCols, dom):
  rowsconstraints = []
  for i in dom:
    constraintsVars = [f"{id}{i}" for id in idCols]
    # Filtrar celdas bloqueadas o con pista
    for key in list(constraintsVars):
      if 0 in vars.get(key, []) or any(" " in str(s) for s in vars.get(key, [])):
        constraintsVars.remove(key)
    rowsconstraints.append(constraintsVars)
  return rowsconstraints

# Ajusta los grupos de columnas para que sean secuencias contiguas
def FixColsConstraints(lists):
  result = []
  for sublist in lists: 
    actualGroup = [sublist[0]] 
    for i in range(1, len(sublist)):
      previous = sublist[i - 1]
      actual = sublist[i]
      # Verifica continuidad en la columna y filas consecutivas
      if previous[0] == actual[0] and int(actual[1:]) == int(previous[1:]) + 1:
        actualGroup.append(actual) 
      else:
        result.append(actualGroup) 
        actualGroup = [actual]
    result.append(actualGroup)
  return result

# Ajusta los grupos de filas para que sean secuencias contiguas
def FixRowsConstraints(lists):
  result = []
  for sublist in lists:
    actualGroup = [sublist[0]]
    for i in range(1, len(sublist)):
      previous = sublist[i - 1]
      actual = sublist[i]
      # Verifica continuidad en la fila y columnas consecutivas
      if int(previous[1]) == int(actual[1]) and ord(actual[0]) == ord(previous[0]) + 1:
        actualGroup.append(actual)
      else:
        result.append(actualGroup)
        actualGroup = [actual]
    result.append(actualGroup)
  return result

# Genera combinaciones de m números cuya suma es n (para las restricciones de suma)
def sumCombinations(n, m):
    numeros = range(1, 10)
    return [c for c in it.permutations(numeros, m) if sum(c) == n]

# Define las restricciones de suma para columnas basándose en las pistas
def DefSumColsConstraints(colsConstraintsDifference):
  sumConstraints = []
  for constraint in colsConstraintsDifference:
    key = constraint[0]
    # La celda que contiene la pista (suma objetivo) está justo arriba del grupo
    element = key[0] + str(int(key[1]) - 1)
    string = str(next(iter(vars[element])))
    n = int(string.split()[0])  # Suma objetivo para la columna
    combinations = sumCombinations(n, len(constraint))
    constraintData = [element, constraint, combinations]
    sumConstraints.append(constraintData)
  return sumConstraints

# Define las restricciones de suma para filas basándose en las pistas
def DefSumRowsConstraints(rowsConstraintsDifference):
  sumConstraints = []
  for constraint in rowsConstraintsDifference:
    key = constraint[0]
    # La celda que contiene la pista (suma objetivo) está a la izquierda del grupo
    element = str(chr(ord(key[0]) - 1)) + key[1]
    string = str(next(iter(vars[element])))
    n = int(string.split()[1])  # Suma objetivo para la fila
    combinations = sumCombinations(n, len(constraint))
    constraintData = [element, constraint, combinations]
    sumConstraints.append(constraintData)
  return sumConstraints
