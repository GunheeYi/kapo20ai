import sys
import time
import math

rDiffs = [-1,-1,-1, 0, 0, 1, 1, 1]
cDiffs = [-1, 0, 1,-1, 1,-1, 0, 1]

def other(player):
    if player==1: return 2
    else: return 1

def inMap(r, c):
    return 0<=r and r<7 and 0<=c and c<7

class Board:
    def getFrac(self):
        if self.lastPlayer==self.myPlayer: return float(self.lps)/(self.lps+self.tps)
        else: return float(self.tps)/(self.lps+self.tps)

    def readBoard(self, myPlayer, input_str, lastPlayer):
        self.myPlayer = myPlayer

        input_lines = input_str.split("\n")
        mapp = []
        for i in range(7):
            mapp.append(list(map(int, input_lines[i+1].split(" "))))
        
        self.mapp = mapp

        self.lastPlayer = lastPlayer
        self.lps = 0 # Last Player's
        self.tps = 0 # To Player's

        for i in range(7):
            for j in range(7):
                if self.mapp[i][j] != 0:
                    if self.mapp[i][j] == lastPlayer: self.lps += 1
                    else: self.tps += 1

        self.lastMove = (-1, -1, -1, -1)
        
    def makeBoard(self, myPlayer, mapp, lastPlayer, lps, tps, lastMove):
        self.myPlayer = myPlayer
        self.mapp = mapp
        self.lastPlayer = lastPlayer
        self.lps = lps
        self.tps = tps
        self.lastMove = lastMove

    def isFull(self):
        return self.lps+self.tps==49
    
    def availableMoves(self):
        actions = []
        for row in range(7):
                for col in range(7):
                    if self.mapp[row][col] == other(self.lastPlayer):
                        for i in range(max(row-2, 0), min(row+3, 7)):
                            for j in range(max(col-2, 0), min(col+3, 7)):
                                if self.mapp[i][j] == 0:
                                    actions.append((row, col, i, j))
        return actions
    
    def move(self, movement):
        r, c, rr, cc = movement
        dist = max(abs(r-rr), abs(c-cc))
        
        newMapp = self.mapp

        newMapp[rr][cc] = other(self.lastPlayer)
        self.tps += 1

        if dist==2:
            newMapp[r][c] = 0
            self.tps -= 1
        
        for rDiff in rDiffs:
            for cDiff in cDiffs:
                adjR = rr+rDiff
                adjC = cc+cDiff
                if inMap(adjR, adjC) and newMapp[adjR][adjC]==self.lastPlayer:
                    newMapp[adjR][adjC] = other(self.lastPlayer)
                    self.tps += 1
                    self.lps -= 1
        
        newBoard = Board()
        newBoard.makeBoard(self.myPlayer, newMapp, other(self.lastPlayer), self.tps, self.lps, movement)
        return newBoard
    
    def possibles(self):
        possibles = []
        for movement in self.availableMoves():
            possibles.append(self.move(movement))
        return possibles

def ucb(fi, ni, Ni):
    return fi/ni + math.sqrt(2*math.log(Ni)/ni)

class Node:
    def __init__(self, parent, board):
        self.parent = parent
        self.ni = 1
        self.board = board
        self.fi = self.board.getFrac()
        self.isLeaf = True

    def updateAsParent(self, dfi):
        self.ni += 1
        self.fi += dfi

    def updateUCB(self, Ni):
        self.ucb = ucb(self.fi, self.ni, Ni)
    
    def getWinRate(self):
        return self.fi/self.ni
    
class MCTS:
    def appendChildren(self, nodeI):
        self.nodes[nodeI].isLeaf = False
        nChild = 0
        for possible in self.nodes[nodeI].board.possibles():
            nChild += 1
            self.nodes.append(Node(nodeI, possible))
            dfi = possible.getFrac()
            parent = nodeI
            while True:
                self.nodes[parent].updateAsParent(dfi)
                if parent==0: break
                else: parent = self.nodes[parent].parent
        return nChild
    
    def updateUCBs(self):
        for node in self.nodes:
            node.updateUCB(self.Ni)
    
    def getBestMove(self):
        bestI = 1
        for compareI in range(2, self.nRootChild+1):
            if self.nodes[compareI].getWinRate() > self.nodes[bestI].getWinRate():
                bestI = compareI
        return self.nodes[bestI].board.lastMove

    def __init__(self, myPlayer, node):
        self.myPlayer = myPlayer
        self.Ni = 1
        self.nodes = []
        self.nodes.append(node)
        self.nRootChild = self.appendChildren(0)
        self.updateUCBs()
    
    def explore(self):
        toExplore = 0
        for i in range(len(self.nodes)):
            if self.nodes[i].isLeaf: toExplore = i
        for i in range(toExplore+1, len(self.nodes)):
            if self.nodes[i].isLeaf and self.nodes[i].ucb > self.nodes[toExplore].ucb: toExplore = i

        if(self.appendChildren(toExplore)>0):
            self.Ni += 1
            self.updateUCBs()

if __name__ == "__main__":
    input_str = sys.stdin.read()

    if input_str.startswith("READY"):
        sys.stdout.write("OK")

    elif input_str.startswith("PLAY"):
        startTime = time.time()
        player = int(__file__[2])
        board = Board()
        board.readBoard(player, input_str, other(player))
        mcts = MCTS(player, Node(0, board))
        
        while True:
            mcts.explore()
            elapsed = time.time()-startTime
            if elapsed > 9.5: break

        bestMove = mcts.getBestMove()
        sys.stdout.write(f"{bestMove[0]} {bestMove[1]} {bestMove[2]} {bestMove[3]}")
