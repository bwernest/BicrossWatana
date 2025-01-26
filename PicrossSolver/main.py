"""___Ideas_________________________________________________________________"""
"""
- Check des données d'entrée (nb de lignes, nb de colonnes, données manquantes)
"""
"""___Module________________________________________________________________"""

import matplotlib.pyplot as plt
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

    def __init__(self, path:str) -> None :
        self.import_from_txt(path)
        self.draw = np.zeros((self.line, self.row), dtype=str)

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

    def solve(self) -> None :
        self.easy_tips()

    def easy_tips(self) -> None :
        for key, tip in self.tips.items() :
            tip_length = self.get_tip_length(tip)
            if key[0] == "L" and tip_length == self.line :
                self.fill_line(key, tip)
            elif key[0] == "R" and tip_length == self.row :
                self.fill_line(key, tip)

    def get_tip_length(self, tip:str) -> int :
        lenT = len(tip)
        blocs = sum(int(eval(tip[i][1:])) for i in range(lenT))
        spaces = 0
        for bloc in range(lenT-1) :
            if tip[bloc][0] == tip[bloc+1][0] :
                spaces += 1
        return blocs + spaces

    def fill_line(self, key:str, tip:str) -> None :
        line = np.zeros(self.row, dtype=str)
        shift = 0
        for bloc in self.tips[key] :
            color = bloc[0]
            length = int(eval(bloc[1:]))
            for i in range(shift, length+shift) :
                line[i] = color
            shift += length + 1
        if key[0] == "L" :
            self.draw[int(key[1:])] = line
        elif key[0] == "R" :
            self.draw[:, int(key[1:])] = line
    
    def show(self) -> None :
        disp_draw = np.zeros((self.line, self.row), dtype=int)
        for line in range(self.line) :
            for row in range(self.row) :
                if self.draw[line, row] != "" :
                    disp_draw[line, row] = ord(self.draw[line, row])
        plt.imshow(disp_draw)

"""___Function______________________________________________________________"""

"""___Execution_____________________________________________________________"""

grid = PicrossSolver("mushroom.txt")

grid.solve()
grid.show()
