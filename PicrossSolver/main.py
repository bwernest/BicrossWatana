"""___Ideas_________________________________________________________________"""
"""
- Check des données d'entrée (nb de lignes, nb de colonnes, données manquantes)
- Ajout de croix si fini (pas comme small holes)
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
                self.done_keys.append(key)
            
            # Méthode décalage
            max_bloc = max([int(eval(tip[i][1:])) for i in range(len(tip))])
            shift = self.row if key[0] == "L" else self.line
            shift -= tip_length
            if max_bloc > shift and key not in self.done_keys :
                self.shift(key, tip, shift)
            
            # Méthode full
            self.fill_full(key, tip)

    def shift(self, key:str, tip:list[str], shift:int) -> None :
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

    def VP_shift(self, key:str, tip:list[str], VP:np.array) -> None :
        positions = []
        for b, bloc in enumerate(tip) :
            bloc_length = int(eval(bloc[1:]))
            for pos in range(len(VP[b])-bloc_length+1) :
                if sum(VP[b, pos:pos+bloc_length]) == bloc_length :
                    positions.append(pos)
        min_pos, max_pos = min(positions), max(positions)+bloc_length
        range_pos = max_pos - min_pos
        if sum(VP[b, min_pos:max_pos]) == range_pos :
            shift = range_pos - bloc_length
            if shift < bloc_length :
                print(f"key : {key}")
                if key[0] == "L" :
                    self.draw[int(key[1:])-1, min_pos+shift:max_pos-shift] = bloc[0]
                elif key[0] == "R" :
                    self.draw[min_pos+shift:max_pos-shift, int(key[1:])-1] = bloc[0]

    def get_tip_length(self, tip:list[str]) -> int :
        lenT = len(tip)
        blocs = sum(int(eval(tip[i][1:])) for i in range(lenT))
        spaces = 0
        for bloc in range(lenT-1) :
            if tip[bloc][0] == tip[bloc+1][0] :
                spaces += 1
        return blocs + spaces

    def fill_line(self, key:str, tip:list[str]) -> None :
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
        
    def fill_full(self, key:str, tip:list[str]) -> None :
        
        # Initialisation
        VP = self.get_VP(key, tip)

        # Cross
        crosses_index = self.get_crosses_index(key)
        for cross_index in crosses_index :
            VP[:, cross_index] = 0
        
        # Available colors
        VP = self.remove_unavailable_colors(VP, key, tip)
        
        # Neighbors
        for b, bloc in enumerate(tip) :
            min_start = self.get_min_start(b, tip, VP)
            max_end = self.get_max_end(b, tip, VP)
            VP[b, :min_start] = 0
            VP[b, max_end+1:] = 0
        
        # Fill
        print(f"Final VP {key} :\n{VP}\n")
        self.VP_shift(key, tip, VP)

    def get_VP(self, key:str, tip:list[str]) -> np.array :
        nb_bloc = len(tip)
        if key[0] == "L" :
            VP = np.ones((nb_bloc, self.row), dtype=int)
        elif key[0] == "R" :
            VP = np.ones((nb_bloc, self.line), dtype=int)
        return VP

    def get_crosses_index(self, key:str) -> list[int] :
        if key[0] == "L" :
            return [i for i in range(self.row) if self.draw[int(key[1:])-1, i] == "X"]
        elif key[0] == "R" :
            return [i for i in range(self.line) if self.draw[i, int(key[1:])-1] == "X"]

    def remove_unavailable_colors(self, VP:np.array, key:str, tip:list[str]) -> np.array :
        
        # Gets available colors
        opposite_side = "L" if key[0] == "R" else "R"
        for i in range(len(VP[0])) :
            colors = []
            for bloc_color in self.tips[opposite_side+str(i+1)] :
                colors.append(bloc_color[0]) if bloc_color[0] not in colors else None
            
            # Removes if unavailable
            for b, bloc in enumerate(tip) :
                color = bloc[0]
                if color not in colors :
                    VP[b, i] = 0
        return VP

    def get_min_start(self, b:int, tip:list[str], VP:np.array) -> int :
        min_start = 0
        prev = 0
        while prev < b :
            prev_length = int(eval(tip[prev][1:]))
            while sum(VP[prev][min_start:min_start+prev_length]) != prev_length :
                min_start += 1
            if tip[prev][0] == tip[prev+1][0] :
                min_start += 1
            prev += 1
        self_length = int(eval(tip[b][1:]))
        while sum(VP[b][min_start:min_start+self_length]) != self_length :
            min_start += 1
        return min_start
    
    def get_max_end(self, b:int, tip:list[str], VP:np.array) -> int :
        max_end = len(VP[0])
        follow = len(tip)-1
        while follow > b :
            follow_length = int(eval(tip[follow][1:]))
            while sum(VP[follow][max_end-follow_length:max_end]) != follow_length :
                max_end -= 1
            if tip[follow][0] == tip[follow-1][0] :
                max_end -= 1
            follow -= 1
        self_length = int(eval(tip[b][1:]))
        while sum(VP[b][max_end-self_length:max_end]) != self_length :
            max_end -= 1
        return max_end

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

level = "mushroom"
# level = "totoro"
grid = PicrossSolver(f"{level}.txt")

grid.solve()
grid.show()
