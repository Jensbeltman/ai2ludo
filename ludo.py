from typing import List, Set, Dict, Tuple, Optional
import numpy as np
from random import randint
from params import *

class Player():
    def __init__(self,playerI):
        self.playerI = playerI
        self.nrS = n_pieces*n_pieceParams+1
        self.piece = np.zeros(pieces) # type: np.ndarray
        self.state = np.zeros(nrS) # type: type: np.ndarray 
        self.qTable = np.zeros(pieces,nrS) # type: type: np.ndarray 

        self.die = 0 # type: int
        self.dieStateI = 1 # type: int
       
    def rollDie(self):
        self.die = randint(1,6)
        self.state[:,self.dieStateI]

    def moveablePieces(self):
        if self.die==6:
            return np.argwhere(self.piece<goalI)
        else:    
            return np.argwhere((0<self.piece) & (self.piece<goalI))

    def vulnerablePieces(self):
        return np.argwhere((0 < self.piece) & (self.piece < goalAreaStartI))

    def allPiecesAtStart(self):
        return np.any(self.piece != 0)

    def getNoneSafePieces(self):
        idxs = np.argwhere(0<self.piece<54) # not in home or goal area
        np.find

    def pieceToMove(self):
        #Chose action/piece based on state and policy
        return randint(0,4)


        

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

    def cvtPiecePos(self,pieceI,playerI,playerJ):
        pieceJ=pieceI
        if playerI<playerJ:
            d = playerJ-playerI
            if pieceI<d*13:
                pieceJ = pieceI+50-13*d
            elif pieceI>d*13:
                pieceJ = pieceI-13*d
        else:
            d = playerI-playerJ
            if pieceI<d*13:
                pieceI = pieceJ-50+13*d
            elif pieceI>d*13:
                pieceI = pieceJ+13*d

        
        
        

    def getLocalPiece():
        pass

    def movePlayerPiece(self,playerI,pieceI):
        piecesInCollision = [[i,piece] for piece in self.players[i].piece for i in range(n_players) if (i is not playerI) & self.cvtPiecePos(piece,playerI,i) is not pieceI]
        
        
        
        

    def updateState(self,playerI):
        pass


    def start(self):
        while winner is None:
            for playerI,player in enumerate(self.players):
                player.rollDie()
                pieceI = player.pieceToMove()
                movePlayerPiece(playerI,pieceI)

                


        





if __name__ == "__main__":
    player = Player()
    print(player.__dict__)
