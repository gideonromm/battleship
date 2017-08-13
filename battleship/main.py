import sys
import uuid
from random import randint

class Ship:
    def __init__(self, length, name):
        self.hits = 0
        self.length = length
        self.name = name 

class Fleet:
    def __init__(self):
        self.ships = []
        self.ships.append(Ship(2, "Mini"))
        self.ships.append(Ship(3, "Submarine"))
        self.ships.append(Ship(4, "Cruiser"))
        self.ships.append(Ship(4, "Battleship"))
        self.ships.append(Ship(5, "Carrier"))

class Cell:
    def __init__(self, row, col):
        self.status = "-"   
        self.row = row
        self.col = col
        self.ship = None

    def fire(self):
        if self.ship:
            self.status = "H"
            self.ship.hits += 1
            if self.ship.hits == self.ship.length:
                return 2
            else:
                return 1
        else:
            self.status = "M"
            return 0

class Board:
    def __init__(self, size):
        self.ocean = []
        self.shipsPlaced = 0
        for x in range(size):
            row = [];
            for y in range(size):
                row.append(Cell(x, y))
            self.ocean.append(row)

    def printBoard(self):
        for row in self.ocean:
            for cell in row:
                sys.stdout.write(str(cell.status))
            print 

    def checkCell(self, cell):
        if cell.ship:
            raise Exception("You already placed your " + cell.ship.name + " ship in this cell: " + str(cell.row) + "," + str(cell.col))

    def placeShip(self, row, col, direction, ship):
        if (direction == 0):
            for cell in range(col, col+ship.length):
                try: 
                    self.checkCell(self.ocean[row][cell])
                except IndexError:
                    #print "You are trying to place a ship outside the ocean!"
                    raise Exception("You are trying to place a ship outside the ocean!")
                    return 
                except Exception, e:
                    #print e
                    raise
                    return 
            for cell in range(col, col+ship.length):
                self.ocean[row][cell].ship = ship
        else: 
            for cell in range(row, row+ship.length):
                try: 
                    self.checkCell(self.ocean[cell][col])
                except IndexError:
                    #print "You are trying to place a ship outside the ocean!"
                    raise Exception("You are trying to place a ship outside the ocean!")
                    return 
                except Exception, e:
                    #print e
                    raise
                    return 
            for cell in range(row, row+ship.length):
                self.ocean[cell][col].ship = ship
        return 1

class Player:
    def __init__(self, name, boardSize):
        self.fleet = Fleet()
        self.board = Board(boardSize)
        self.name = name
        self.type = "human"

    def setup(self):
        for ship in self.fleet.ships:
            self.placeShip(ship)

    def fire(self, player, row, col):
        result = player.board.ocean[row][col].fire()
        if result == 0:
            print "Miss!"
        elif result == 1:
            print "Hit!"
        elif result == 2: 
            print self.name + " sinks " + player.name + "'s " + player.board.ocean[row][col].ship.name
            player.fleet.ships.remove(player.board.ocean[row][col].ship)

class ComputerPlayer(Player):
    def __init__(self, name, boardSize):
        self.fleet = Fleet()
        self.board = Board(boardSize)
        self.name = name
        self.type = "computer"

    def guess(self, player):
        row = randint(0, len(player.board.ocean[0]) - 1)
        col = randint(0, len(player.board.ocean[0]) - 1)
        print "Computer guesses: " + str(row) + ", " + str(col)
        self.fire(player, row, col)

    def placeShip(self, ship):
        shipPlaced = 0
        while not shipPlaced:
            row = randint(0, len(self.board.ocean[0]) - 1)
            col = randint(0, len(self.board.ocean[0]) - 1)
            direction = randint(0,1)
            try:
                shipPlaced = self.board.placeShip(row, col, direction, ship)
            except:
                pass # Don't print errors

class GameState:
    def __init__(self, game):
        self.game = game
    def placeShip(self, player, row, col, direction, ship):
        print "You cannot place ships at this point in the game!"
        return
    def fire(self, player, opponent, row, col):
        print "You cannot fire at this point in the game!"
        return
    def register(self):
        print "You cannot register at this point inthe game!"
        return

class NewState(GameState):
    def register(self, name, type):
        if type == "computer":
            newPlayer = ComputerPlayer(name, self.game.boardSize)
            newPlayer.setup()
            self.game.readyPlayers += 1
        else:
            newPlayer = Player(name, self.game.boardSize)
        self.game.players.append(newPlayer)
        return newPlayer
    def start(self):
        if len(self.game.players) > 1:
            self.game.state = self.game.setupState
        else:
            print "Cannot start the game until at least 2 players register"

class SetupState(GameState):
    def start(self):
        if self.game.readyPlayers == len(self.game.players):
            self.game.turnPlayer = self.game.players[0]
            self.game.state = self.game.turnState
    def placeShip(self, player, row, col, direction, ship):
        try:
            shipPlaced = player.board.placeShip(row, col, direction, ship)
        except Exception, e:
            print e
        player.board.shipsPlaced += shipPlaced
        if player.board.shipsPlaced == len(player.fleet.ships):
            self.game.readyPlayers += 1
        return shipPlaced
        
class TurnState(GameState):
    def fire(self, player, opponent, row, col):
        if player != self.game.turnPlayer:
            print "It is not your turn."
            return
        player.fire(opponent, row, col)
        opponent.board.printBoard()
        if len(opponent.fleet.ships) < 1:   
            print player.name + " wins!"
            self.game.state = self.game.winState
            return
        if opponent.type == "computer":
            opponent.guess(player)
        else:
            self.game.turnPlayer = opponent
    
class WinState(GameState):
    True

class Game:
    def __init__(self):
        self.id = uuid.uuid1()
        self.boardSize = 10
        self.players = []
        self.readyPlayers = 0
        self.newState = NewState(self)
        self.setupState = SetupState(self)
        self.turnState = TurnState(self)
        self.winState = WinState(self)
        self.state = self.newState 
        self.turnPlayer = None 

    def register(self, name, type):
        return self.state.register(name, type)

    def start(self):
        self.state.start()

    def placeShip(self, player, row, col, direction, ship):
        return self.state.placeShip(player, row, col, direction, ship)

    def fire(self, player, opponent, row, col):
        self.state.fire(player, opponent, row, col)

    def getOpponent(self, player):
        index = self.players.index(player)
        return self.players[(index+1)]
###########################

myGame = Game()
player1 = myGame.register("Gadi", "human")
player2 = myGame.register("Computer", "computer")
print "The following players have registered for this game:"
for player in myGame.players:
    print "    " + player.name
myGame.start()

for ship in player1.fleet.ships:
    shipPlaced = 0
    while not shipPlaced:
        print "Hi, " + player1.name + ". " + "Please place the following ship: " + ship.name + " (length: " + str(ship.length) + ")"
        try:
            row = int(raw_input("Row: "))
            col = int(raw_input("Column: "))
            direction = int(raw_input("Direction [0 = horizontal, 1 = vertical]: "))
            shipPlaced = myGame.placeShip(player1, row, col, direction, ship)
        except KeyboardInterrupt, e:
            exit()
        except:
            pass
myGame.start()
# player1 continues to guess
while myGame.state == myGame.turnState:
        player = myGame.turnPlayer
        opponent = myGame.getOpponent(player)
        print "Guess where " + opponent.name + " is hiding his ships"
        print "  " + str(len(opponent.fleet.ships)) + " ships remaining: " 
        for ship in opponent.fleet.ships:
            print "    " + ship.name
        try:   
            row = int(raw_input("Row: "))
            col = int(raw_input("Column: "))
            myGame.fire(player, opponent, row, col)
        except KeyboardInterrupt, e:
            exit()
        except Exception, e:
            print e
            pass

