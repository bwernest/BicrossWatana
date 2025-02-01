import numpy as np

class Pen() :

    def draw_value(
        self,
        drawing:np.array,
        key:str,
        location:str,
        value:str
        ) -> np.array :

        num = int(eval(key[1:])) - 1
        if key[0] == "L" :
            drawing[num, location] = value
        elif key[0] == "R" :
            drawing[location, num] = value
        else :
            raise ValueError(f"Unable to read key : {key}")
        return drawing
    
    def fill_line_with_crosses(self,
                               drawing:np.array,
                               key:str
                               ) -> np.array :
        length = self.get_length(drawing, key)
        for location in range(length) :
            value = self.get_value(drawing, key, location)
            if value == "" :
                self.draw_value(drawing, key, location, value)
    
    def get_value(self,
                  drawing:np.array,
                  key:str,
                  location:str) -> str :
        num = int(eval(key[1:])) - 1
        if key[0] == "L" :
            return drawing[num, location]
        elif key[0] == "R" :
            return drawing[location, num]

    def get_length(self,
                   drawing:np.array,
                   key:str,
                   ) -> int :
        if key[0] == "L" :
            return drawing.shape[0]
        elif key[0] == "R" :
            return drawing.shape[1]
