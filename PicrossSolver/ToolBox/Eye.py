import numpy as np
from ToolBox.Pen import Pen
from matplotlib.pyplot import imshow

class Eye(Pen) :
    
    def check_sol(self, guess:np.array, solution:np.array) -> None :
        assert guess.shape == solution.shape, "Shapes incorrect !"
        for l, r in zip(range(self.line), range(self.row)) :
            if guess[l, r] != "" and guess[l, r] != solution[l, r] :
                diff_matrix = np.equal(guess, solution)
                
                imshow(diff_matrix)
                raise ValueError(f"Matrix is false at coordinates {(l, r)} !\n"+
                                 f"guess :\t{guess[l, r]}\n"+
                                 f"solution : \t{solution[l, r]}")

