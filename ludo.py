from typing import List, Set, Dict, Tuple, Optional
import numpy as np
from random import randint
from params import *

class Player():
    def __init__(self,playerI):
        self.playerI = playerI
        self.nrS = n_pieces*n_pieceParams+1
        self.pieces = np.zeros(n_pieces,dtype=np.int64) # type: np.ndarray
        self.state = np.zeros(n_pieceParams,dtype=np.int64) # type: type: np.ndarray 
        self.qTable = np.zeros((n_pieces,n_pieceParams)) # type: np.ndarray 
        
        self.die = 0 # type: int
        self.dieStateI = 1 # type: int

        self.enemyIds = [i for i in range(4) if i != self.playerI]
     
        # Include conversion to itself for idexing reasons
        self.cvtTable = [[self.cvtPiecePos(i,self.playerI,ei) for i in range(58)] for ei in range(n_players)]
       
    def rollDie(self):
        self.die = randint(1,6)
        

    def movePiece(self,pieceI,newPieceP=None): # TODO handle stepping over goal
        if newPieceP == None:
            self.pieces[pieceI]+= self.die
            if self.pieces[pieceI]>57: # Handle stepback in goal area
                self.pieces[pieceI]=57-self.pieces[pieceI]%57
        else:
            self.pieces[pieceI]=newPieceP
    
    def movePieces(self,pieceIs,newPieceP):
        for pieceI in pieceIs:
            self.movePiece(pieceI,newPieceP) 

    def moveablePieces(self):
        if self.die==6:
            return np.argwhere(self.pieces<goalI)
        else:    
            return np.argwhere((0<self.pieces) & (self.pieces<goalI))

    def vulnerablePieces(self): # TODO needs to be updated to inlcude globes and double piece information
        return np.argwhere((0 < self.pieces) & (self.pieces < goalAreaStartI))

    def allPiecesAtStart(self):
        return np.any(self.pieces != 0)

    def getNoneSafePieces(self):
        idxs = np.argwhere(0<self.pieces<54) # not in home or goal area
        return self.pieces[idxs]

    def pieceToMove(self): # TODO dont evaluate twice
        #Chose action/piece based on state and policy
        moveablePieces = self.moveablePieces().flatten()
        if moveablePieces.shape[0]>0:
            return np.random.choice(moveablePieces)
        return None

    def getNextGlobe(self,pieceP):
        for globePos in globeI:
            if globePos > pieceP:
                return globePos
        return None
    
    def getNextStar(self,pieceP):
        for starPos in starI:
            if starPos > pieceP:
                return starPos
        return None

    def updateQ(self,reward):
        pass # TODO

    def cvtPiecePos(self,pieceP,playerI,playerJ):
        if pieceP == 0 or playerI == playerJ:
            return None
        if playerI<playerJ:
            d = playerJ-playerI
            if pieceP<d*13:
                return pieceP+52-13*d
            elif pieceP>d*13:
                return pieceP-13*d
        else:
            d = playerI-playerJ
            if pieceP<52-d*13:
                return pieceP+13*d
            elif pieceP>52-d*13:
                return pieceP-(52-d*13)
        return None
            

    
        

class Game():
    def __init__(self):
        self.nrPlayers = 4
        self.players = [Player(i) for i in range(n_players)] # type: List[Player]
        self.winner = None

    def checkForWinner(self,player):
        for piece in player.pieces:
            if piece != goalI:
                return
                
        self.winner = player
        print("Player {} won the game".format(player.playerI))
        return True

    def getCloseEnemys(self,playerI,pieceI):
        pass # TODO
 
    
    def getCollisions(self,player: Player,newPieceP):
        for enemyI in player.enemyIds:
            enemy = self.players[enemyI]
            cvtPieceP = player.cvtTable[enemyI][newPieceP]            
            if cvtPieceP is not None:                
                enemyPieceIInCollision = [epi for epi,ep in enumerate(enemy.pieces) if ep==cvtPieceP]                
                if enemyPieceIInCollision:                    
                    return enemy, cvtPieceP, enemyPieceIInCollision
                
        return None, None, []


    def handleStar(self,player: Player,newPieceP,pieceI):
        if newPieceP == starAtGoalI:
            player.movePiece(pieceI,goalI)
        else:
            nextStartP = player.getNextStar(newPieceP)
            enemy, colPos, colPieceIds = self.getCollisions(player,nextStartP)
            n_col = len(colPieceIds)
            if n_col == 0:
                player.movePiece(pieceI,nextStartP)    
            else:
                self.handleCollision(n_col ,player, pieceI, nextStartP, enemy, colPos, colPieceIds)

   

        

    def handleCollision(self,n_col ,player, pieceI, newPieceP, enemy, colPos, colPieceIds):
        if n_col > 1:
            player.movePiece(pieceI,homeI)
        else:
            if colPos in globeSafeI:
                player.movePiece(pieceI,homeI)
            else:
                enemy.movePiece(colPieceIds[0],homeI)
                player.movePiece(pieceI,newPieceP)

            
    def handleMove(self,player: Player,pieceI):
        curPieceP = player.pieces[pieceI] 
           
        if curPieceP<goalAreaStartI: # Only check for collisions ,start and globes if piece is not in the goal area
            if curPieceP == homeI and player.die == 6:
                newPieceP = 1
            elif player.die == globeDie:
                newPieceP = player.getNextGlobe(curPieceP)
            elif player.die == starDie:
                newPieceP = player.getNextStar(curPieceP)
            else:
                newPieceP = player.pieces[pieceI]+player.die
            
            if newPieceP is not None:
                enemy, colPos, colPieceIds = self.getCollisions(player,newPieceP)
                n_col = len(colPieceIds)

                if n_col == 0: # if no collision move ask player to move piece
                    if newPieceP in starI:
                        self.handleStar(player,newPieceP,pieceI)
                    else:
                        player.movePiece(pieceI,newPieceP)
                elif n_col > 0:  # Evaluate collision
                    self.handleCollision(n_col,player,pieceI,newPieceP,enemy, colPos, colPieceIds)
        else:# If piece in goal area just move
            player.movePiece(pieceI)

        return randint(-10,10) # TODO Evaluate reward

    
    def updateState(self,player):
        pass # TODO

    def reset(self):
        for player in self.players:
            player.pieces.fill(0)
        self.winner = None

    def writeStateToFile(self,playerI,die,pieceI,f):
        if pieceI is None:
            pieceI = -1
        f.write("{} {} {} ".format(playerI,die,pieceI))
        for player in self.players:
            np.savetxt(f,player.pieces,fmt='%i',newline=' ')
        f.write('\n')
       

    #np.savetxt(f,a,fmt='%i',newline=' ')#
    def run(self,saveReplay=False,replayPath='ludoReplay.txt'):
        playerMoves = np.zeros(4)

        replayFile = None
        if saveReplay:
            replayFile = open(replayPath,'w+')

        while self.winner is None:
            for player in self.players:
                self.updateState(player)
                player.rollDie()
                pieceI = player.pieceToMove()

                if saveReplay:
                    self.writeStateToFile(player.playerI,player.die,pieceI,replayFile)

                if pieceI != None:
                    reward = self.handleMove(player,pieceI)
                    player.updateQ(reward)
                    if self.checkForWinner(player):
                        break

            playerMoves+=1


        if saveReplay:
            replayFile.close()



if __name__ == "__main__":
    import time
    itt =1
    game = Game()
    times = [0 for i in range(itt)]
    for i in range(itt):
        start = time.time()
        game.run(True)
        game.reset()
        end = time.time()
        times[i]=end-start
    print(sum(times)/itt)