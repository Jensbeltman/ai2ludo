from typing import List, Set, Dict, Tuple, Optional
import numpy as np
from random import randint
from params import *

class Player():
    def __init__(self,playerI):
        self.playerI = playerI
        self.nrS = n_pieces*n_pieceParams+1
        self.pieces = np.zeros(n_pieces) # type: np.ndarray
        self.state = np.zeros(n_pieceParams) # type: type: np.ndarray 
        self.qTable = np.zeros(n_pieces,n_pieceParams) # type: type: np.ndarray 

        self.die = 0 # type: int
        self.dieStateI = 1 # type: int

        self.enemyIds = [i for i in range(4) if i is not self-playerI]
        self.cvtTable = [[self.cvtPiecePos(i,self.playerI,ei) for ei in self.enemyIds] for i in range(58)]
       
    def rollDie(self):
        self.die = randint(1,6)
        self.state[:,self.dieStateI]

    def moveablePieces(self):
        if self.die==6:
            return np.argwhere(self.pieces<goalI)
        else:    
            return np.argwhere((0<self.pieces) & (self.pieces<goalI))

    def vulnerablePieces(self):
        return np.argwhere((0 < self.pieces) & (self.pieces < goalAreaStartI))

    def allPiecesAtStart(self):
        return np.any(self.pieces != 0)

    def getNoneSafePieces(self):
        idxs = np.argwhere(0<self.pieces<54) # not in home or goal area
        return self.pieces[idxs]

    def pieceToMove(self):
        #Chose action/piece based on state and policy
        return np.random.choice(self.moveablePieces())

    def cvtPiecePos(self,pieceP,playerI,playerJ):
        if pieceP == 0:
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
        self.players = [Player() for _ in range(nrPlayers)] # type: List[Player]
        self.winner = None

    def getCloseEnemys(playerI,pieceI):
        pass
        # for player in self.players[playerI]:
        #     for pi

        # return enemyIds, pieceIds

    def getLocalPiece():
        pass

    
    def getCollisions(self,player: Player,pieceP):
        for enemyId in player.enemyIds:
            enemy = self.players(enemyId)
            cvtPieceP = player.cvtTable[pieceP,enemyId]
            if cvtPieceP is not None:
                enemyPieceIInCollision = [epi for epi,ep in enumerate(enemy.piece) if ep==cvtPieceP]
                if enemyPieceIInCollision:
                    return cvtPieceP, enemyPieceIInCollision
                
                

    def movePlayerPiece(self,player: Player,pieceI):
        pos, enemyColPieceIds = self.getCollisions(player,pieceP=player.pieces[pieceI])
        if enemyColPieceIds >1:
            print("Player {} Piece {} was sent home".format(player.playerI,pieceI))
        else:
            pass

    
    def updateState(self,playerI):
        pass


    def start(self):
        while winner is None:
            for playerI,player in enumerate(self.players):
                player.rollDie()
                pieceI = player.pieceToMove()
                movePlayerPiece(player,pieceI)

                


        





if __name__ == "__main__":
    player = Player()
    print(player.__dict__)
