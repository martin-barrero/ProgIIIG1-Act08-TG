import itertools as it  # Biblioteca que permite trabajar con iteradores, útil para crear combinaciones
from collections import defaultdict  # Diccionario que permite asignar un tipo por defecto para claves nuevas

# ===================== FUNCIONES DE CONSTRUCCIÓN =====================

# Función que crea un diccionario donde cada variable (casilla) tiene un conjunto de vecinos (casillas que comparten restricciones)
def Build_neighbors(constraints): 
  neighbors = defaultdict(set)  # Diccionario donde cada clave tendrá como valor un conjunto vacío por defecto
  for group in constraints:  # constraints: [['A1', 'A2', ...], ['B1', 'B2', ...]], es decir, grupos de restricciones (filas, columnas, cajas)
    for var in group:  # Itera sobre cada casilla del grupo
      neighbors[var].update(set(group) - {var})  # Agrega al conjunto de vecinos todas las casillas del grupo excepto la misma
  return neighbors  # Devuelve el diccionario con los vecinos de cada casilla

# Define las restricciones por columna (cada columna debe tener números únicos del 1 al 9)
def DefColsConstrints(idCols, dom):
  colsconstraints = []
  for id in idCols:  # Para cada columna (letra)
    constraintVars = [f"{id}{i}" for i in dom]  # Genera las celdas de esa columna (A1, A2, ..., A9)
    colsconstraints.append(constraintVars)
  return colsconstraints

# Define las restricciones por fila (cada fila debe tener números únicos del 1 al 9)
def DefRowsConstrints(idCols, dom):
  rolsconstraints = []
  for i in dom:  # Para cada fila (número)
    ronstraintVars = [f"{id}{i}" for id in idCols]  # Genera las celdas de esa fila (A1, B1, ..., I1)
    rolsconstraints.append(ronstraintVars)
  return rolsconstraints

# Define las restricciones por cada caja 3x3
def DefBoxconstraints():
  boxes = []
  row_blocks = [range(1, 4), range(4, 7), range(7, 10)]  # Filas divididas en bloques 1-3, 4-6, 7-9
  col_blocks = ['ABC', 'DEF', 'GHI']  # Columnas divididas en bloques A-C, D-F, G-I

  for rows in row_blocks:
    for cols in col_blocks:
      box = [f"{col}{row}" for row in rows for col in cols]  # Genera celdas para cada caja
      boxes.append(box)
  return boxes

# ===================== FUNCIONES DE CONSISTENCIA =====================

# Esta función elimina de los dominios los valores ya asignados a otras celdas dentro de una misma restricción
def ConsistenceDifference(constraints, varDoms):
  for constraint in constraints:
    for var in constraint:
      if len(varDoms[var]) == 1:  # Si la celda ya tiene un valor asignado
        for varAux in constraint:
          if varAux != var:  # Para el resto de celdas del grupo
            varDoms[varAux].discard(list(varDoms[var])[0])  # Elimina ese valor de sus dominios
  return varDoms

# Esta función aplica una técnica de "naked pair": si dos celdas tienen el mismo par de valores, se eliminan de otras celdas
def ConsistenceDomsEqual(constraints, varDoms):
  for var1 in constraints:
    if len(varDoms[var1]) == 2:  # Si la celda tiene exactamente 2 valores posibles
      for var2 in constraints:
        if var1 != var2 and varDoms[var1] == varDoms[var2]:  # Si hay otra celda con el mismo par
          for var3 in constraints:
            if var3 != var1 and var3 != var2:
              varDoms[var3].discard(list(varDoms[var1])[0])  # Elimina esos dos valores de las demás celdas
              varDoms[var3].discard(list(varDoms[var1])[1])
  return varDoms

# ===================== FUNCIONES AUXILIARES =====================

# Verifica si el Sudoku está resuelto (todas las celdas tienen un único valor)
def Is_solved(varDoms):
  return all(len(varDoms[v]) == 1 for v in varDoms)

# Selecciona una celda no asignada con la menor cantidad de valores posibles (heurística de mínima cantidad de valores)
def Select_unassigned_var(varDoms):
  unassigned = [(v, varDoms[v]) for v in varDoms if len(varDoms[v]) > 1]  # Filtra celdas sin asignar
  return min(unassigned, key = lambda x: len(x[1]))[0]  # Devuelve la que tiene menor dominio

# Imprime el Sudoku de forma legible
def Print_sudoku(varDoms):
  if not varDoms:  # Si no hay solución
    print("El tablero no tiene solución")
    return

  for r in range(1, 10):  # Itera sobre filas
    row = []
    for c in idCols:  # Itera sobre columnas
      val = varDoms[f"{c}{r}"]
      row.append(str(list(val)[0]))  # Imprime el número o un punto si no está resuelto
    print(" ".join(row))  # Une los valores separados por espacios

# ===================== ALGORITMO PRINCIPAL =====================

# Algoritmo de búsqueda con retroceso (backtracking) usando inferencia local
def Backtrack(varDoms, neighbors):
  if Is_solved(varDoms):  # Si el Sudoku está resuelto
    return varDoms

  var = Select_unassigned_var(varDoms)  # Elegimos una variable no asignada
  for value in varDoms[var]:  # Probamos cada valor posible
    new_vars = {v: varDoms[v].copy() for v in varDoms}  # Copiamos los dominios para no modificar el original
    new_vars[var] = {value}  # Asignamos un valor a la variable elegida

    # Aplicamos inferencia basada en restricciones
    new_vars = ConsistenceDifference(constraintsVars, new_vars)
    for const in constraintsVars:
      new_vars = ConsistenceDomsEqual(const, new_vars)

    # Si ningún dominio se vació, continuamos recursivamente
    if all(len(new_vars[v]) > 0 for v in new_vars):
      result = Backtrack(new_vars, neighbors)
      if result:
        return result  # Si se encontró solución, se retorna

  return None  # Si no hay solución, se retorna None

# ===================== DECLARACIÓN DE VARIABLES Y LECTURA DE DATOS =====================

dom = set(range(1, 10))  # Posibles valores del 1 al 9
idCols = "ABCDEFGHI"  # Columnas del tablero

# Creamos claves tipo (1, 'A'), (1, 'B'), ..., (9, 'I') combinando filas y columnas
keys = list(it.product(dom, idCols))
strKeys = [f"{key[1]}{key[0]}" for key in keys]  # Convertimos a formato de celda: 'A1', 'B1', ..., 'I9'

# Creamos un diccionario donde cada celda tiene por dominio todos los valores posibles (1 al 9)
vars = {key: dom.copy() for key in strKeys}

# Leemos el archivo del tablero (una celda por línea), y si hay un número válido, lo fijamos como valor único de esa celda
with open('board.txt', 'r') as f:
  for key in vars.keys():
    valor = f.readline().strip()  # Leemos línea y eliminamos espacios en blanco
    if valor.isdigit() and len(valor) == 1:  # Si es un dígito único (1 a 9)
      vars[key] = {int(valor)}  # Asignamos ese valor como único posible en el dominio de esa celda

# ===================== CONSTRUCCIÓN DE RESTRICCIONES =====================

# Unimos todas las restricciones: columnas, filas y cajas
constraintsVars = DefColsConstrints(idCols, dom) + DefRowsConstrints(idCols, dom) + DefBoxconstraints()

# Construimos los vecinos de cada celda a partir de las restricciones
neighbors = Build_neighbors(constraintsVars)

# ===================== EJECUCIÓN =====================

# Ejecuta el algoritmo de búsqueda para encontrar la solución
solution = Backtrack(vars, neighbors)

# Muestra el resultado en pantalla
Print_sudoku(solution)