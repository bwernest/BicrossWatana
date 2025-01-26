"""___Ideas_________________________________________________________________"""
"""
- Check des données d'entrée (nb de lignes, nb de colonnes, données manquantes)
"""
"""___Module________________________________________________________________"""

import numpy as np

"""___Data__________________________________________________________________"""

tset_file = "mushroom.txt"

"""___Class_________________________________________________________________"""

class PicrossSolver() :

    line : int = 0
    row : int = 0
    nb_color : int
    tips : dict[str:list[str]] = {}
    draw : np.array

    def __init__(self, path : str) -> None :
        self.import_from_txt(path)

    def import_from_txt(self, path:str) -> None :
        with open(path, "r") as txt :
            data = txt.read()
        data = data.replace(" ", "").split("\n")
        while "" in data :
            data.remove("")
        for line in data :
            key, values = line.split(":")
            key = key.upper()
            values = values.split(",")
            self.tips[key] = values
            self.tips[key] = [self.tips[key][i].upper() for i in range(len(self.tips[key]))]
            if key[0] == "L" :
                self.line += 1
            elif key[0] == "R" :
                self.row += 1

"""___Function______________________________________________________________"""

"""___Execution_____________________________________________________________"""

grid = PicrossSolver("mushroom.txt")

print(grid.tips)
print(grid.line, grid.row)
