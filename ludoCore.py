import numpy as np
from random import randint, random
from params import *

class Player():
    def __init__(self,playerI):
        self.playerI = playerI
        self.pieces = np.zeros(n_pieces,dtype=np.int64) # type: np.ndarray
        self.enemyIds = [i for i in range(4) if i != self.playerI]
        self.die = 0 # type: int

        # Conversion to other player coords. Includes conversion to itself for idexing reasons
        self.cvtTable = [[self.cvtPiecePos(i,self.playerI,ei) for i in range(58)] for ei in range(n_players)]

        # All pieces at home indicator. For efficient impl of 3 roll rule
        self.allPiecesAtHome = True

    def rollDie(self):
        self.die = randint(1,6)

    def allPiecesAtHomeUpdate(self): #TODO implement this so that player can roll die 3 times when all pieces are at start
        self.allPiecesAtHome = not np.any(self.pieces != 0)

    def getNewPiecePos(self,pieceI): 
        curPieceP = self.pieces[pieceI]
        if curPieceP == homeI and (self.die == 6 or self.die == globeDie):
            return 1
        elif self.die == globeDie:
            return self.getNextGlobe(curPieceP)
        elif self.die == starDie:
            return self.getNextStar(curPieceP)
        else:
            newPieceP = self.pieces[pieceI]+ self.die
            if newPieceP>57: # Handle stepback in goal area
                newPieceP=57-newPieceP%57
            return newPieceP
        
    def movePiece(self,pieceI,newPieceP=None): # TODO handle stepping over goal
        if newPieceP == None:
            self.pieces[pieceI]= self.getNewPiecePos(pieceI)
        else:
            self.pieces[pieceI]=newPieceP
    
    def movePieces(self,pieceIs,newPieceP):
        for pieceI in pieceIs:
            self.movePiece(pieceI,newPieceP) 

    def moveablePieces(self):
        if self.die==6:
            return np.argwhere(self.pieces<goalI)
        elif self.die == globeDie:
            return np.argwhere(self.pieces<globeI[-1])
        elif self.die == starDie:
            return np.argwhere((0<self.pieces) & (self.pieces<starI[-1]))
        else:    
            return np.argwhere((0<self.pieces) & (self.pieces<goalI))

    def pieceToMove(self): # TODO dont evaluate twice
        moveablePieces = self.moveablePieces().flatten()
        if moveablePieces.size:
            return np.random.choice(moveablePieces)
        else:
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
    def __init__(self,verbose=False):
        self.nrPlayers = 4
        self.players = [Player(i) for i in range(n_players)] # type: List[Player]
        self.winner = None
        self.verbose = verbose
        

    def checkForWinner(self,player):
        for piece in player.pieces:
            if piece != goalI:
                return False
                
        self.winner = player
        if self.verbose:
            print("Player {} won the game".format(player.playerI))
        return True

    def reset(self):
        for player in self.players:
            player.pieces.fill(0)
        self.winner = None
        self.gameLen = 0

    def writeStateToFile(self,playerI,die,pieceI,f):
        if pieceI is None:
            pieceI = -1
        f.write("{} {} {} ".format(playerI,die,pieceI))
        for player in self.players:
            np.savetxt(f,player.pieces,fmt='%i',newline=' ')
        f.write('\n')
 
    def getCollisions(self,player: Player,newPieceP):
        if newPieceP >= goalAreaStartI:
            return 0, None, None, []

        for enemyI in player.enemyIds:
            enemy = self.players[enemyI]
            cvtPieceP = player.cvtTable[enemyI][newPieceP]            
            if cvtPieceP is not None:                
                enemyPieceIInCollision = [epi for epi,ep in enumerate(enemy.pieces) if ep==cvtPieceP]                
                if enemyPieceIInCollision:                    
                    return len(enemyPieceIInCollision), enemy, cvtPieceP, enemyPieceIInCollision
                
        return 0, None, None, []

    def handleStar(self,player: Player,newPieceP,pieceI):
        if newPieceP == starAtGoalI:
            return goalI
        else:
            return player.getNextStar(newPieceP)
            
    def handleCollision(self,n_col ,player, pieceI, newPieceP, enemy, colPos, colPieceIds)-> int:
        if n_col > 1:
            if newPieceP == startI:
                player.movePiece(pieceI,newPieceP)
                enemy.movePieces(colPieceIds,homeI)
                enemy.allPiecesAtHomeUpdate()
                return sentHomeEnemy
            else:
                player.movePiece(pieceI,homeI)
                player.allPiecesAtHomeUpdate()
                return sentHomePlayer
        else:
            if colPos in globeSafeI:
                player.movePiece(pieceI,homeI)
                player.allPiecesAtHomeUpdate()
                return sentHomePlayer
            else:
                enemy.movePiece(colPieceIds[0],homeI)
                enemy.allPiecesAtHomeUpdate()
                player.movePiece(pieceI,newPieceP)
                return sentHomeEnemy
        
    
    def handleMove(self,player: Player,pieceI, newPieceP, n_col, enemy, colPos, colPieceIds):
        colEvent = None
        prevPieceP = player.pieces[pieceI]
        if newPieceP == startI:
            player.allPiecesAtHome = False
    
        if n_col == 0: # if no collision move ask player to move piece
            player.movePiece(pieceI,newPieceP)
        elif n_col > 0:  # Evaluate collision
            colEvent =  self.handleCollision(n_col,player,pieceI,newPieceP,enemy, colPos, colPieceIds)
        
        if colEvent == sentHomePlayer:
            newPieceP = homeI
        return prevPieceP, newPieceP, colEvent

    
    def run(self,saveReplay=False,replayPath='ludoReplay.txt'):
        replayFile = None
        if saveReplay:
            replayFile = open(replayPath,'w+')

        while self.winner is None:
            for player in self.players:
                # Handle if all player pieces are home
                if player.allPiecesAtHome:  
                    for _ in range(3):
                        player.rollDie()
                        if player.die == 6 or player.die == globeDie:
                            break
                else:
                    player.rollDie()

                pieceI = player.pieceToMove()

                if saveReplay:
                    self.writeStateToFile(player.playerI,player.die,pieceI,replayFile)

                if pieceI != None:
                    newPieceP = player.getNewPiecePos(pieceI)
                    n_col, enemy, colPos, colPieceIds = self.getCollisions(player,newPieceP)
                    prevPiece,newPieceP, colEvent = self.handleMove(player,pieceI,newPieceP, n_col, enemy, colPos, colPieceIds)
                    
                    if self.checkForWinner(player):
                        break
                        
        if saveReplay:
            replayFile.close()


if __name__ == "__main__":
    import time
    import matplotlib.pyplot as plt

    # Read data from file:
    game = Game(verbose=False)
    itt =200
    winners = [-1 for i in range(itt)]
    starttime = time.time()
    for i in range(itt):
        game.run(saveReplay=False)
        winners[i]=game.winner.playerI
        game.reset()
        print(" Game number \t {}".format(i), end='\r')
        #print("Game number \t {} Qentrys\t {} \t Gamelen {} ".format(i,QSize[i],GameLen[i]), end='\r')
    endtime = time.time()

    print("Game number \t"+str(itt), end='\n')
    print("Games/sec {}".format(1/((endtime-starttime)/itt)))
    
    winners = np.array(winners)
    winnersHist = np.histogram(winners,[0,1,2,3,4])
    print(winnersHist)
    print("Wins {}".format(winnersHist[0]))
   
    fig, ax = plt.subplots(2, 1) 
    ax[0].bar([1,2,3,4],winnersHist[0])
    ax[0].tick_label = ["P{}".format(i+1) for i in range(4)]
    windowSize = 10
    winFreq = np.zeros((itt-windowSize,4),dtype=int)
    for i in range(itt-windowSize):
        for pi in range(4):
            winFreq[i,:]=np.histogram(winners[i:i+windowSize],[0,1,2,3,4])[0]
    
    ax[1].plot(winFreq*(100.0/windowSize))
    ax[1].legend(["P{}".format(i+1) for i in range(4)])


    plt.show()

