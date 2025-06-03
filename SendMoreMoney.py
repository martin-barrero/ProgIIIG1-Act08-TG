Letras=set("SEND MORE MONEY")
Letras.discard(' ')

print("Cantidad de letras:", len(Letras))
print("Letras:", Letras)

Digitos=set(range(10))
print("Dígitos:", Digitos)

import itertools as it
perms=list(it.permutations(Digitos,len(Letras)))
print("Permutaciones:", len(perms))

print(perms[0])
print(perms[907199])
print(perms[1814399])

Dicci={k:None for k in Letras}
print(Dicci)

pos=0
for k in Dicci.keys():
  print(f"posicion asociada a {k} es {pos}")
  pos+=1

for perm in perms:
  pos=0
  for k in Dicci.keys():
    Dicci[k]=perm[pos]
    pos+=1
  print(Dicci)
  input()