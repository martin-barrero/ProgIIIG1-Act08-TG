
# **Introducción**
El Sudoku es un juego de lógica que consiste en completar una cuadrícula de 9x9 celdas con números del 1 al 9. Cumpliendose que cada fila, columna y cuadricula 3x3 no puede repetir números. Más allá de su función recreativa, es un ejemplo clásico y útil para el modelamiento y solución a través de programación por restricciones.

Para esto se presenta el desarrollo de un algoritmo para resolver tableros de Sudoku utilizando programación por restricciones. El cuál utiliza modelamiento por CSP, restricciones con reglas básicas y avanzadas del sudoku y una adaptación del algoritmo look-ahead, MAC (Maintaining Arc Consistency) usando las restricciones vistas en clase en vez del algoritmo AC-3.

# **Planteamiento del problema**
El problema a solucionar se basa en representar celda como una variable cada casilla, con dominios que contienen los posibles valores del 1 al 9, y restricciones que aseguran la validez de las soluciones (unicidad en filas, columnas y cajas).


Se ha implementado un algoritmo de búsqueda con retroceso (backtracking), complementado por técnicas de inferencia local para mejorar la eficiencia, incluyendo consistencia por diferencia y eliminación de pares desnudos. Además, se modeló el problema mediante una red de restricciones entre variables vecinas, apoyándose en la técnica de mantenimiento de consistencia de arco (MAC) para reducir el espacio de búsqueda.

Este enfoque demuestra cómo los principios fundamentales de la programación por restricciones pueden aplicarse eficazmente a la resolución de problemas combinatorios complejos, como el Sudoku, mediante una implementación en Python clara y extensible.

# **Metodología**

# **Estructura general de código**

## Librerías
```python
import itertools as it
from collections import defaultdict
```
## Funciones de construcción

```python
def Build_neighbors(constraints): 
  neighbors = defaultdict(set)
  for group in constraints:
    for var in group:
      neighbors[var].update(set(group) - {var})
  return neighbors

def DefColsConstrints(idCols, dom):
  colsconstraints = []
  for id in idCols:
    constraintVars = [f"{id}{i}" for i in dom]
    colsconstraints.append(constraintVars)
  return colsconstraints

def DefRowsConstrints(idCols, dom):
  rolsconstraints = []
  for i in dom:
    ronstraintVars = [f"{id}{i}" for id in idCols]
    rolsconstraints.append(ronstraintVars)
  return rolsconstraints

def DefBoxconstraints():
  boxes = []
  row_blocks = [range(1, 4), range(4, 7), range(7, 10)]
  col_blocks = ['ABC', 'DEF', 'GHI']
  for rows in row_blocks:
    for cols in col_blocks:
      box = [f"{col}{row}" for row in rows for col in cols]
      boxes.append(box)
  return boxes
```
## Funciones de consistencia

```python
def ConsistenceDifference(constraints, varDoms):
  for constraint in constraints:
    for var in constraint:
      if len(varDoms[var]) == 1:
        for varAux in constraint:
          if varAux != var:
            varDoms[varAux].discard(list(varDoms[var])[0])
  return varDoms

def ConsistenceDomsEqual(constraints, varDoms):
  for var1 in constraints:
    if len(varDoms[var1]) == 2:
      for var2 in constraints:
        if var1 != var2 and varDoms[var1] == varDoms[var2]:
          for var3 in constraints:
            if var3 != var1 and var3 != var2:
              varDoms[var3].discard(list(varDoms[var1])[0])
              varDoms[var3].discard(list(varDoms[var1])[1])
  return varDoms
```

## Funciones auxiliares
```python
def Is_solved(varDoms):
  return all(len(varDoms[v]) == 1 for v in varDoms)

def Select_unassigned_var(varDoms):
  unassigned = [(v, varDoms[v]) for v in varDoms if len(varDoms[v]) > 1]
  return min(unassigned, key = lambda x: len(x[1]))[0]

def Print_sudoku(varDoms):
  if not varDoms:
    print("El tablero no tiene solución")
    return
  for r in range(1, 10):
    row = []
    for c in idCols:
      val = varDoms[f"{c}{r}"]
      row.append(str(list(val)[0]))
    print(" ".join(row))
```
## Algoritmo principal
```python
def Backtrack(varDoms, neighbors):
  if Is_solved(varDoms):
    return varDoms
  var = Select_unassigned_var(varDoms)
  for value in varDoms[var]:
    new_vars = {v: varDoms[v].copy() for v in varDoms}
    new_vars[var] = {value}
    new_vars = ConsistenceDifference(constraintsVars, new_vars)
    for const in constraintsVars:
      new_vars = ConsistenceDomsEqual(const, new_vars)
    if all(len(new_vars[v]) > 0 for v in new_vars):
      result = Backtrack(new_vars, neighbors)
      if result:
        return result
  return None
```

## Declaración de variables y lectura de datos
```python
dom = set(range(1, 10))
idCols = "ABCDEFGHI"
keys = list(it.product(dom, idCols))
strKeys = [f"{key[1]}{key[0]}" for key in keys]
vars = {key: dom.copy() for key in strKeys}

with open('board.txt', 'r') as f:
  for key in vars.keys():
    valor = f.readline().strip()
    if valor.isdigit() and len(valor) == 1:
      vars[key] = {int(valor)}
```

## Construcción de restricciones
```python
constraintsVars = DefColsConstrints(idCols, dom) + DefRowsConstrints(idCols, dom) + DefBoxconstraints()

neighbors = Build_neighbors(constraintsVars)
```
## Ejecución
```cpp
solution = Backtrack(vars, neighbors)
Print_sudoku(solution)
```

# **Discusión**
Porque usamos lo que usamos

# Conclusiones
