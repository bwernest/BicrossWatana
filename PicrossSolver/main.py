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
    done_keys : list[str] = []

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
        for key, tip in self.tips.items() :
            tip_length = self.get_tip_length(tip)

            # Lignes évidentes
            if tip_length == self.line or tip_length == self.row :
                self.fill_line(key, tip)
            
            # Méthode décalage
            max_bloc = max([int(eval(tip[i][1:])) for i in range(len(tip))])
            shift = self.line if key[0] == "L" else self.row
            shift -= tip_length
            if max_bloc > shift and key not in self.done_keys :
                self.shift(key, tip, shift)

    def shift(self, key:str, tip:str, shift:int) -> None :
        start = shift
        for b, bloc in enumerate(tip) :
            if int(eval(bloc[1:])) > shift :
                fillable = int(eval(bloc[1:])) - shift
                if key[0] == "L" :
                    self.draw[int(key[1:])-1, start:start+fillable] = bloc[0]
                elif key[0] == "R" :
                    self.draw[start:start+fillable, int(key[1:])-1] = bloc[0]
                start += fillable + 1 # TODO not sure of +1 (+shift maybe)

            else :
                start += int(eval(bloc[1:]))
            
            if b < len(tip)-1 :
                if tip[b][0] == tip[b+1][0] :
                    start += 1

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
        line[line == ""] = "X"
        if key[0] == "L" :
            self.draw[int(key[1:])-1] = line
        elif key[0] == "R" :
            self.draw[:, int(key[1:])-1] = line
        self.done_keys.append(key)
    
    def show(self) -> None :
        disp_draw = np.zeros((self.line, self.row), dtype=int)
        colors = []
        for line in range(self.line) :
            for row in range(self.row) :
                if self.draw[line, row] != "" :
                    color = ord(self.draw[line, row])
                    disp_draw[line, row] = color
                    if color not in colors : colors.append(color)
        for c in range(len(colors)) :
            disp_draw[disp_draw == colors[c]] = c + 1
        plt.imshow(disp_draw)

"""___Function______________________________________________________________"""

"""___Execution_____________________________________________________________"""

grid = PicrossSolver("mushroom.txt")

grid.solve()
grid.show()
