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

# --- FUNCIONES DE CONSISTENCIA ---

# Propagación: reduce dominios en función de las combinaciones válidas que coinciden con vecinos
def DomainCrossing(neighbors, varDoms):
  for cell, clues in neighbors.items():
    for clue in clues:
      group = next((g for g in sumConstraints if g[0] == clue), None)
      if group is None:
        continue
      groupCells = group[1]
      combinations = group[2]
      if cell not in groupCells:
        continue

      i = groupCells.index(cell)
      possible_values = set()
      for comb in combinations:
        valid = True
        for j, var in enumerate(groupCells):
          if var == cell:
            continue
          if comb[j] not in varDoms[var]:
            valid = False
            break
        if valid:
          possible_values.add(comb[i])
      varDoms[cell] = varDoms[cell].intersection(possible_values)
  return varDoms

# En cada grupo, si una celda tiene valor fijo, eliminar ese valor de dominios de las demás (restricción de diferencia)
def ConsistenceDifference(constraints, varDoms):
  for constraint in constraints:
    for var in constraint:
      if len(varDoms[var]) == 1:
        for varAux in constraint:
          if varAux != var:
            varDoms[varAux].discard(list(varDoms[var])[0])
  return varDoms

# --- FUNCIONES AUXILIARES ---

# Construye el diccionario de vecinos (pistas a las que pertenece cada celda blanca)
def Neighbors(sumConstraints):
  neighbors = {var: [] for var in vars}
  # Lista de todas las celdas blancas (no bloqueadas ni pistas)
  whiteCells = list(set([clave for sublista in differenceConstraints for clave in sublista]))
  neighbors = {k: v for k, v in neighbors.items() if k in whiteCells}
  # Para cada grupo de suma, añadir la pista como vecino de las celdas
  for group in sumConstraints:
    groupName = group[0]
    groupCells = group[1]
    for cell in groupCells:
      if cell in whiteCells and groupName not in neighbors[cell]:
        neighbors[cell].append(groupName)
  return neighbors

# Imprime el tablero de Kakuro con el estado actual de variables
def PrintBoard(vars):
  print("Kakuro Code: ", code, "\n")
  print(" ".join("  ABCDEFGHI"))
  print(" ".join("  ---------"))
  for i in range(1, 10):
    row = []
    for c in "ABCDEFGHI":
      cell = f"{c}{i}"
      val = vars[cell]
      if val == {0}:
        row.append("0")      # Celda negra
      elif any(" " in str(v) for v in val):
        row.append("X")      # Celda con pista
      elif len(val) == 1:
        row.append(str(list(val)[0]))  # Celda con valor único asignado
      else:
        row.append(".")      # Celda sin valor fijo aún
    print(i, "|", " ".join(row))

# Obtener arcos para AC-3: pares de variables en el mismo grupo de suma
def GetArcs(sumConstraints):
  arcs = []
  for group in sumConstraints:
    cells = group[1]
    for xi in cells:
      for xj in cells:
        if xi != xj:
          arcs.append((xi, xj))
  return arcs

# --- ALGORITMO AC-3 ---

# Revisar consistencia entre xi y xj; eliminar valores inconsistentes de dominio de xi
def Revise(xi, xj, domains, sumConstraints):
  revised = False
  to_remove = set()

  relevant_groups = [g for g in sumConstraints if xi in g[1] and xj in g[1]]

  for vi in domains[xi]:
    valid = False
    for group in relevant_groups:
      cells = group[1]
      combos = group[2]
      idx_xi = cells.index(xi)
      idx_xj = cells.index(xj)

      for combo in combos:
        if combo[idx_xi] == vi and combo[idx_xj] in domains[xj]:
          compatible = True
          for k, cell in enumerate(cells):
            if cell == xi or cell == xj:
              continue
            if combo[k] not in domains[cell]:
              compatible = False
              break
          if compatible:
            valid = True
            break
      if valid:
        break
    if not valid:
      to_remove.add(vi)
      revised = True

  if revised:
      domains[xi] -= to_remove

  return revised
