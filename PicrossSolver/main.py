"""___Ideas_________________________________________________________________"""
"""
- Check des données d'entrée (nb de lignes, nb de colonnes, données manquantes)
- Ajout de croix si fini (pas comme small holes)
"""
"""___Module________________________________________________________________"""

from copy import deepcopy
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
    VPs : dict[str:np.array] = {}

    def __init__(self, path:str) -> None :
        self.import_from_txt(path)
        self.draw = np.zeros((self.line, self.row), dtype=str)
        self.get_VPs()

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

    def get_VPs(self) -> None :
        for key, tip in self.tips.items() :
            nb_bloc = len(tip)
            if key[0] == "L" :
                VP = np.ones((nb_bloc, self.row), dtype=int)
            elif key[0] == "R" :
                VP = np.ones((nb_bloc, self.line), dtype=int)
            self.VPs[key] = VP

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
            
        self.changes = 4
        count = 0
        while self.changes > 0 :
            draw_start = deepcopy(self.draw)
            count += 1
            print(count)
            for key, tip in self.tips.items() :
                if key not in self.done_keys :
                    
                    # Méthode full
                    self.fill_full(key, tip)
                    self.VP_shift(key, tip)
                    self.fill_crosses(key)
                    self.check_blocs(key, tip)
                    self.investigate_draw(key, tip)
                    if self.check_line(key) :
                        if key[0] == "L" :
                            for i in range(self.row) :
                                if self.draw[int(key[1:])-1, i] == "" :
                                    self.draw[int(key[1:])-1, i] = "X"
                        elif key[0] == "R" :
                            for i in range(self.line) :
                                if self.draw[i, int(key[1:])-1] == "" :
                                    self.draw[i, int(key[1:])-1] = "X"
                        self.done_keys.append(key)
            if (draw_start == self.draw).all() :
                self.changes -= 1

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

    def VP_shift(self, key:str, tip:list[str]) -> None :
        positions = []
        VP = self.VPs[key]
        for b, bloc in enumerate(tip) :
            bloc_length = int(eval(bloc[1:]))
            for pos in range(len(VP[b])-bloc_length+1) :
                if sum(VP[b, pos:pos+bloc_length]) == bloc_length :
                    positions.append(pos)
        min_pos, max_pos = min(positions), max(positions)+bloc_length
        range_pos = max_pos - min_pos
        if sum(VP[b, min_pos:max_pos]) == range_pos :
            shift = range_pos - bloc_length
            print(f"{key} : {min_pos} - {max_pos} : {shift}")
            if shift < bloc_length :
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
        VP = self.VPs[key]

        # Cross
        crosses_index = self.get_crosses_index(key)
        for cross_index in crosses_index :
            VP[:, cross_index] = 0
        
        # Available colors
        VP = self.remove_unavailable_colors(VP, key, tip)
        
        # Neighbors
        max_b = len(tip)-1
        for b, bloc in enumerate(tip) :
            min_start = self.get_min_start(b, tip, VP)
            max_end = self.get_max_end(b, tip, VP)
            print(f"{key} : {min_start} - {max_end}")
            VP[b, :min_start] = 0
            VP[b, max_end:] = 0
            if b > 0 : assert min_start > 0, f"Min start error : {key} : {min_start}"
            if b < max_b : assert max_end < len(VP[0]), f"Max end error : {key} : {max_end}"
        
        # Fill
        self.VPs[key] = VP

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
        debug_line = []
        lenV = len(VP[prev])
        while prev < b :
            prev_length = int(eval(tip[prev][1:]))
            while sum(VP[prev][min_start:min_start+prev_length]) != prev_length :
                if min_start > lenV-prev_length :
                    raise ValueError(f"min_end to big :\ntip : {tip}\nb = {b}\nVP : {VP}\ndebug_line : {debug_line}")
                min_start += 1
                debug_line.append(0)
            if tip[prev][0] == tip[prev+1][0] :
                min_start += 1
                debug_line.append(0)
            min_start += prev_length
            for _ in range(prev_length) : debug_line.append(1)
            prev += 1
        self_length = int(eval(tip[b][1:]))
        while sum(VP[b][min_start:min_start+self_length]) != self_length :
            min_start += 1
        return min_start
    
    def get_max_end(self, b:int, tip:list[str], VP:np.array) -> int :
        max_end = len(VP[0])
        follow = len(tip)-1
        debug_line = []
        while follow > b :
            follow_length = int(eval(tip[follow][1:]))
            while sum(VP[follow][max_end-follow_length:max_end]) != follow_length :
                if max_end < 0 :
                    raise ValueError(f"max_end to little :\ntip : {tip}\nb = {b}\nVP : {VP}\ndebug_line = {debug_line[::-1]}")
                max_end -= 1
                debug_line.append(0)
            if tip[follow][0] == tip[follow-1][0] :
                max_end -= 1
                debug_line.append(0)
            max_end -= follow_length
            for _ in range(follow_length) : debug_line.append(1)
            follow -= 1
        self_length = int(eval(tip[b][1:]))
        while sum(VP[b][max_end-self_length:max_end]) != self_length :
            max_end -= 1
        return max_end

    def fill_crosses(self, key:str) -> None :
        VP = self.VPs[key]
        for k in range(VP.shape[1]) :
            if sum(VP[:, k]) == 0 :
                if key[0] == "L" :
                    if self.draw[int(eval(key[1:]))-1, k] == "" :
                        self.draw[int(eval(key[1:]))-1, k] = "X"
                elif key[0] == "R" :
                    if self.draw[k, int(eval(key[1:]))-1] == "" :
                        self.draw[k, int(eval(key[1:]))-1] = "X"
                
    def check_line(self, key:str) -> bool :
        line = self.draw[int(key[1:])-1] if key[0] == "L" else self.draw[:, int(key[1:])-1] 
        if "" not in line :
            return True
        tip = self.tips[key]
        str_line = ""
        for i in range(len(line)) :
            if line[i] == "" :
                str_line += "X"
            str_line += line[i]
        line = str_line.split("X")
        while "" in line :
            line.remove("")
        for k in range(len(line)) :
            line[k] = line[k][0]+str(len(line[k]))
        if line == tip :
            return True
        return False

    def check_blocs(self, key:str, tip:list[str]) -> None :
        VP = self.VPs[key]
        for line in range(VP.shape[0]) :
            bloc = tip[line]
            bloc_length = int(eval(bloc[1:]))
            if 1 in VP[line] :
                index = list(VP[line]).index(1)
                num = int(key[1:])-1
                if sum(VP[line]) == bloc_length :
                    if key[0] == "L" :
                        self.draw[num, index:index+bloc_length] = bloc[0]
                    elif key[0] == "R" :
                        self.draw[index:index+bloc_length, num] = bloc[0]
                else :  # De la merde
                    lenV = VP.shape[1]
                    consecutive = bloc_length
                    while index+consecutive+1 < lenV and sum(VP[line][index:index+consecutive+1]) == consecutive+1 :
                        consecutive += 1
                    if consecutive < 2*bloc_length :
                        shift = 2*bloc_length-1-consecutive
                        if key[0] == "L" :
                            self.draw[num, index+shift:index+consecutive-shift]
                        elif key[0] == "R" :
                            self.draw[index+shift:index+consecutive-shift, num]

    def investigate_draw(self, key:str, tip:list[str]) -> None :
        VP = self.VPs[key]
        num = int(eval(key[1:])) - 1
        if key[0] == "L" :
            draw_line = self.draw[num, :]
        elif key[0] == "R" :
            draw_line = self.draw[:, num]
        
        for e, elem in enumerate(draw_line) :
            if elem == "X" :
                VP[:, e] = np.zeros(VP.shape[1])
            elif elem == "" :
                pass
            else :
                for b, bloc in enumerate(tip) :
                    if bloc[0] != elem :
                        if VP[b, e] != 0 :
                            print("oui")
                        VP[b, e] = 0
        self.VPs[key] = VP

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

# level = "mushroom"
level = "totoro"
grid = PicrossSolver(f"{level}.txt")

grid.solve()
grid.show()

print(np.sort(grid.done_keys))
