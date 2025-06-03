import itertools as it
from collections import defaultdict
import copy

dom = set(range(1, 10))
idCols = "ABCDEFGHI"

keys = list(it.product(dom, idCols))
strKeys = [f"{key[1]}{key[0]}" for key in keys]

vars = {key: dom.copy() for key in strKeys}

with open('boardkakuro.txt', 'r') as f:
  for key in vars.keys():
    valor = f.readline().strip()
    if "0" in valor:
      vars[key] = {int(0)}
    if " " in valor:
      vars[key] = {valor}

def DefColsConstraints(idCols, dom):
  colsconstraints = []
  for id in idCols:
    constraintsVars = [f"{id}{i}" for i in dom]
    for key in list(constraintsVars):
      if 0 in vars.get(key, []) or any(" " in str(s) for s in vars.get(key, [])):
        constraintsVars.remove(key)
    colsconstraints.append(constraintsVars)
  return colsconstraints

def DefRowsConstraints(idCols, dom):
  rowsconstraints = []
  for i in dom:
    constraintsVars = [f"{id}{i}" for id in idCols]
    for key in list(constraintsVars):
      if 0 in vars.get(key, []) or any(" " in str(s) for s in vars.get(key, [])):
        constraintsVars.remove(key)
    rowsconstraints.append(constraintsVars)
  return rowsconstraints

def fixColsConstraints(lists):
  result = []
  for sublist in lists: 
    actualGroup = [sublist[0]] 
    for i in range(1, len(sublist)):
      previous = sublist[i - 1]
      actual = sublist[i]
      if previous[0] == actual[0] and int(actual[1:]) == int(previous[1:]) + 1:
        actualGroup.append(actual) 
      else:
        result.append(actualGroup) 
        actualGroup = [actual]
    result.append(actualGroup)
  return result

def fixRowsConstraints(lists):
  result = []
  for sublist in lists:
    actualGroup = [sublist[0]]
    for i in range(1, len(sublist)):
      previous = sublist[i - 1]
      actual = sublist[i]
      if int(previous[1]) == int(actual[1]) and ord(actual[0]) == ord(previous[0]) + 1:
        actualGroup.append(actual)
      else:
        result.append(actualGroup)
        actualGroup = [actual]
    result.append(actualGroup)
  return result

def sumCombinations(n, m):
    numeros = range(1, 10)
    return [c for c in it.permutations(numeros, m) if sum(c) == n]

def DefSumColsConstraints(colsConstraintsDifference):
  sumConstraints = []
  for constraint in colsConstraintsDifference:
    key = constraint[0]
    element = key[0] + str(int(key[1]) - 1)
    string = str(next(iter(vars[element])))
    n = int(string.split()[0])
    combinations = sumCombinations(n, len(constraint))
    constraintData = [element, constraint, combinations]
    sumConstraints.append(constraintData)
  return sumConstraints

def DefSumRowsConstraints(rowsConstraintsDifference):
  sumConstraints = []
  for constraint in rowsConstraintsDifference:
    key = constraint[0]
    element = str(chr(ord(key[0]) - 1)) + key[1]
    string = str(next(iter(vars[element])))
    n = int(string.split()[1])
    combinations = sumCombinations(n, len(constraint))
    constraintData = [element, constraint, combinations]
    sumConstraints.append(constraintData)
  return sumConstraints

colsConstraints = DefColsConstraints(idCols, dom) 
rowsConstraints = DefRowsConstraints(idCols, dom)

colsConstraintsDifference = [sublist for sublist in colsConstraints if sublist]
rowsConstraintsDifference = [sublist for sublist in rowsConstraints if sublist]

fixCols = fixColsConstraints(colsConstraintsDifference)
fixRows = fixRowsConstraints(rowsConstraintsDifference)

colsSumConstraints = DefSumColsConstraints(fixCols)
rowsSumConstraints = DefSumRowsConstraints(fixRows)

sumConstraints = colsSumConstraints + rowsSumConstraints
differenceConstraints = fixCols + fixRows

cellConstraints = defaultdict(list)

def Neighbors(sumConstraints):
  neighbors = {var: [] for var in vars}
  whiteCells = list(set([clave for sublista in differenceConstraints for clave in sublista]))
  neighbors = {k: v for k, v in neighbors.items() if k in whiteCells}
  for group in sumConstraints:
    groupName = group[0]
    groupCells = group[1]
    for cell in groupCells:
      if cell in whiteCells and groupName not in neighbors[cell]:
        neighbors[cell].append(groupName)
  return neighbors

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


def ConsistenceDifference(constraints, varDoms):
  for constraint in constraints:
    for var in constraint:
      if len(varDoms[var]) == 1:
        for varAux in constraint:
          if varAux != var:
            varDoms[varAux].discard(list(varDoms[var])[0])
  return varDoms

neighbors = Neighbors(sumConstraints)

def print_board(vars):
  for i in range(1, 10):
    row = []
    for c in "ABCDEFGHI":
      cell = f"{c}{i}"
      val = vars[cell]
      if val == {0}:
        row.append("0")
      elif any(" " in str(v) for v in val):
        row.append("X")
      elif len(val) == 1:
        row.append(str(list(val)[0]))
      else:
        row.append(".")
    print(" ".join(row))

def infer(vars, sumConstraints, differenceConstraints):
    varDoms = copy.deepcopy(vars)
    while True:
        old = copy.deepcopy(varDoms)
        varDoms = DomainCrossing(neighbors, varDoms)
        varDoms = ConsistenceDifference(differenceConstraints, varDoms)
        if varDoms == old:
            break
    return varDoms

def get_arcs(sumConstraints):
    arcs = []
    for group in sumConstraints:
        cells = group[1]
        for xi in cells:
            for xj in cells:
                if xi != xj:
                    arcs.append((xi, xj))
    return arcs

from collections import deque

def revise(xi, xj, domains, sumConstraints):
    revised = False
    to_remove = set()

    # Obtener todos los grupos donde xi y xj estén juntos
    relevant_groups = [g for g in sumConstraints if xi in g[1] and xj in g[1]]

    for vi in domains[xi]:
        # Para que vi sea válido, debe haber al menos una combinación
        # en algún grupo que contiene xi y xj que permita vi y algún vj en domains[xj]
        valid = False
        for group in relevant_groups:
            cells = group[1]
            combos = group[2]
            idx_xi = cells.index(xi)
            idx_xj = cells.index(xj)

            for combo in combos:
                if combo[idx_xi] == vi and combo[idx_xj] in domains[xj]:
                    # Además, debemos verificar que para el resto de variables en el grupo,
                    # los valores de la combinación están en los dominios correspondientes
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


def ac3(domains, sumConstraints):
    queue = deque(get_arcs(sumConstraints))
    while queue:
        xi, xj = queue.popleft()
        if revise(xi, xj, domains, sumConstraints):
            if not domains[xi]:
                return False  # dominio vacío → inconsistente
            for group in sumConstraints:
                cells = group[1]
                if xi in cells:
                    for xk in cells:
                        if xk != xi and xk != xj:
                            queue.append((xk, xi))
    return domains

def infer_with_ac3(vars, sumConstraints, differenceConstraints):
    varDoms = copy.deepcopy(vars)
    while True:
        old = copy.deepcopy(varDoms)
        varDoms = DomainCrossing(neighbors, varDoms)
        varDoms = ConsistenceDifference(differenceConstraints, varDoms)
        varDoms = ac3(varDoms, sumConstraints)
        if varDoms == old:
            break
    return varDoms

def is_complete(domains):
    return all(len(domains[v]) == 1 for v in domains if domains[v] != {0} and not any(" " in str(s) for s in domains[v]))

def select_unassigned_variable(domains):
    # Heurística: la variable con menor dominio > 1
    candidates = [v for v in domains if len(domains[v]) > 1 and domains[v] != {0} and not any(" " in str(s) for s in domains[v])]
    return min(candidates, key=lambda v: len(domains[v])) if candidates else None

def backtracking_search(domains):
    if is_complete(domains):
        return domains

    var = select_unassigned_variable(domains)
    if not var:
        return None

    for value in sorted(domains[var]):
        new_domains = copy.deepcopy(domains)
        new_domains[var] = {value}
        try:
            inferred = infer_with_ac3(new_domains, sumConstraints, differenceConstraints)
            if all(inferred[v] for v in inferred):  # ningún dominio vacío
                result = backtracking_search(inferred)
                if result:
                    return result
        except:
            continue  # si ocurre error, ignoramos y seguimos con el siguiente valor

    return None  # sin solución con las asignaciones actuales

vars = infer_with_ac3(vars, sumConstraints, differenceConstraints)

if not is_complete(vars):
    vars = backtracking_search(vars)

print_board(vars)