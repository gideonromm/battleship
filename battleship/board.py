import cell, ship

class Board:
    ocean = []
    
    def __init__(self, size):
        for x in range(size):
            self.ocean.append(Cell * size)

    def printBoard():
        for row in self.ocean:
            for cell in row:
                print cell.visited
