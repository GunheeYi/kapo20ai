import sys
#import random
import time
from operator import attrgetter
import math

rDiffs = [-1,-1,-1, 0, 0, 1, 1, 1]
cDiffs = [-1, 0, 1,-1, 1,-1, 0, 1]

def other(player):
    if player==1: return 2
    else: return 1

def inMap(r, c):
    return 0<=r and r<7 and 0<=c and c<7

def printMapp(mapp):
    for i in range(7):
        for j in range(7):
            print(f"{mapp[i][j]} ", end="")
        print()

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
        
        #self.frac = self.getFrac()
        self.lastMove = (-1, -1, -1, -1)
        
    def makeBoard(self, myPlayer, mapp, lastPlayer, lps, tps, lastMove):
        self.myPlayer = myPlayer
        self.mapp = mapp
        self.lastPlayer = lastPlayer
        self.lps = lps
        self.tps = tps
        #self.frac = self.getFrac()
        self.lastMove = lastMove

    def __str__(self):
        print("Map")
        printMapp(self.mapp)
        return f"\nmy player: {self.myPlayer}\nlast player: {self.lastPlayer}\nlps: {self.lps}\ntps: {self.tps}\nlast move: {self.lastMove}"
    
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
        #print(f"available: {actions}")
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
        #print("appending children..")
        self.nodes[nodeI].isLeaf = False
        nChild = 0
        for possible in self.nodes[nodeI].board.possibles():
            self.i += 1 #????
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
        #print("updating ucbs..")
        for node in self.nodes:
            node.updateUCB(self.Ni)
    
    def getBestMove(self):
        bestI = 1
        for compareI in range(2, self.nRootChild+1):
            if self.nodes[compareI].getWinRate() > self.nodes[bestI].getWinRate():
                bestI = compareI
        return self.nodes[bestI].board.lastMove

    def __init__(self, myPlayer, node):
        #print("initializing mcts..")
        self.myPlayer = myPlayer
        self.Ni = 1

        self.i = 0
        self.nodes = []
        self.nodes.append(node)
        self.nRootChild = self.appendChildren(0)
        self.updateUCBs()
        #self.bestMove = self.getBestMove()
    
    def explore(self):
        #print("exploring..")
        toExplore = 0
        for i in range(len(self.nodes)):
            if self.nodes[i].isLeaf: toExplore = i
            #print("b43a")
        for i in range(toExplore+1, len(self.nodes)):
            if self.nodes[i].isLeaf and self.nodes[i].ucb > self.nodes[toExplore].ucb: toExplore = i
            #print("bqaw")

        if(self.appendChildren(toExplore)>0):
            self.Ni += 1
            self.updateUCBs()

        
        #self.bestMove = self.getBestMove()


if __name__ == "__main__":
    input_str = sys.stdin.read()

    # 입력 예시
    # READY 1234567890.1234567 (입력시간)
    # "OK" 를 출력하세요.
    if input_str.startswith("READY"):
        # 출력
        sys.stdout.write("OK")
    
    # 입력 예시
    # PLAY
    # 2 0 0 0 0 0 1
    # 0 0 0 0 0 0 0
    # 0 0 0 0 0 0 0
    # 0 0 0 0 0 0 0
    # 0 0 0 0 0 0 0
    # 0 0 0 0 0 0 0
    # 1 0 0 0 0 0 2
    # 1234567890.1234567 (입력시간)
    
    # AI의 액션을 출력하세요.
    # 출력 예시 : "0 0 2 2"
    elif input_str.startswith("PLAY"):
        startTime = time.time()
        #print("aw3das")
        player = int(__file__[2])
        board = Board()
        board.readBoard(player, input_str, other(player))
        #print(board)
        #print("2bqae")
        mcts = MCTS(player, Node(0, board))
        #print("5b3a")
        
        while True:
            mcts.explore()
            elapsed = time.time()-startTime
            if elapsed > 0.3: break

        bestMove = mcts.getBestMove()
        sys.stdout.write(f"{bestMove[0]} {bestMove[1]} {bestMove[2]} {bestMove[3]}")



        

        
        




