import numpy as np
from random import randint, random
from params import *
import operator
import matplotlib.pyplot as plt

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

        # Qlearning
        self.state = "" 
        self.action = 0
        self.epsilon = 0.3
        self.alpha = 0.5
        self.gamma = 0.9
        self.Q = {} # type: np.ndarray 
        

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
        pieceTM = None
        #Chose action/piece based on state and policy
        moveablePieces = self.moveablePieces().flatten()
        # Get random number for epsilon greedy stat
        rnd = random()

        if moveablePieces.size:
            if rnd<self.epsilon:
                pieceTM = np.random.choice(moveablePieces)
            else:          
                # Get the index/action/pieceI of max q   
                try:
                    qs = self.Q[self.state]
                except KeyError:
                    qs = [0,0,0,0]  
                    self.Q[self.state] = qs 
                maxq = 0        
                for i in moveablePieces:
                    q = self.Q[self.state][i]
                    if q > maxq:
                        maxq = q
                        pieceTM = i        

        self.action = pieceTM
        return pieceTM

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

    def updateQ(self,reward, newState):
        try:
            maxQNewState = max(self.Q[newState])
        except KeyError:
            self.Q[newState]=[0,0,0,0]
            maxQNewState = 0

        try:
            self.Q[self.state][self.action] += self.alpha*(reward +  self.gamma*maxQNewState-self.Q[self.state][self.action])
        except KeyError:
            self.Q[self.state] = [0,0,0,0]
            self.Q[self.state][self.action] += self.alpha*(reward +  self.gamma*maxQNewState-self.Q[self.state][self.action])


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
        self.rewards = [0,0,0,0]

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
            
    def handleCollision(self,n_col ,player, pieceI, newPieceP, enemy, colPos, colPieceIds):
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
    
    def handleMove(self,player: Player,pieceI,moveEval):
        n_col, newPieceP,enemy, colPos, colPieceIds = moveEval
        colEvent = None
        prevPieceP = player.pieces[pieceI]
        if newPieceP == startI:
            player.allPiecesAtHome = False
    
        if n_col == 0: # if no collision move ask player to move piece
            player.movePiece(pieceI,newPieceP)
        elif n_col > 0:  # Evaluate collision
            colEvent =  self.handleCollision(n_col,player,pieceI,newPieceP,enemy, colPos, colPieceIds)
        
        return prevPieceP, newPieceP, colEvent

    def getReward(self,prevPieceP, newPieceP, colEvent,state):
        reward = 0.0
        dPieceP = newPieceP - prevPieceP

        # Collision Reward
        if colEvent == None:
            reward+=dPieceP
        elif colEvent == sentHomeEnemy:
            reward+=dPieceP
        elif colEvent == sentHomePlayer:
            reward-=dPieceP
        
        # Safe Reward
        if state[2] or state[4]:# if on safe globe or goal area
            reward+=4
        
        # Move piece into goal 
        if newPieceP == goalI:
            reward+=10

        # Move player to start 
        if newPieceP == startI:
            reward += 6

        return reward

    def getState(self,player):
        moveablePieces = player.moveablePieces()
        stateVals = []
        colInfo = [] 
        for pieceI in range(4):
            if pieceI in moveablePieces:
                newPieceP = player.getNewPiecePos(pieceI)
                if newPieceP in starI:
                    newPieceP = self.handleStar(player,newPieceP,pieceI)

                n_col, enemy, colPos, colPieceIds = self.getCollisions(player,newPieceP) # TODO take advantage of calculated collisions
                colInfo.append([n_col, newPieceP,enemy, colPos, colPieceIds])
                
                enemyCol = n_col
                start = int(newPieceP == 0)
                globe = int(newPieceP in globeSafeI)
                star = int(newPieceP in starI)
                goalA = int(newPieceP >= goalAreaStartI)
                stuck =  0
                stateVals.extend([enemyCol,start,globe,star,goalA,stuck])
            else:
                stateVals.extend([0,0,0,0,0,1])
                colInfo.append([0,None,None,None,[]])

    
        state =  "".join(map(str,stateVals))
         

        return state, stateVals ,colInfo 

       
    #np.savetxt(f,a,fmt='%i',newline=' ')#
    def run(self,saveReplay=False,replayPath='ludoReplay.txt'):
        replayFile = None
        if saveReplay:
            replayFile = open(replayPath,'w+')


        for player in self.players:
            newState, stateVals ,colInfo  = self.getState(player)
            player.state =  newState

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

                # Note die needs to be rolled before state CALC
                newState, stateVals ,colInfo  = self.getState(player)
                if player.action is not None:
                    player.updateQ(self.rewards[player.playerI],newState) # used the reward from last time
                player.state = newState # First update player state after Q update

                pieceI = player.pieceToMove()

                if saveReplay:
                    self.writeStateToFile(player.playerI,player.die,pieceI,replayFile)

                if pieceI != None:
                    prevPieceP, newPieceP, colEvent = self.handleMove(player,pieceI,colInfo[pieceI])
                    #---Qlearning---
                    reward = self.getReward(prevPieceP, newPieceP, colEvent, state=stateVals[pieceI*6:pieceI*6+6])
                    self.rewards[player.playerI] = reward
                    #---------------
                    if self.checkForWinner(player):
                        break

        if saveReplay:
            replayFile.close()


if __name__ == "__main__":
    import time
    itt =1000
    game = Game(verbose=False)
    game.players[1].epsilon = 1.0
    game.players[2].epsilon = 1.0
    game.players[3].epsilon = 1.0
    winners = [-1 for i in range(itt)]

    starttime = time.time()
    print('')
    for i in range(itt):
        print("Game number \t"+str(i), end='\r')
        game.run(saveReplay=False)
        winners[i]=game.winner.playerI
        game.reset()
    endtime = time.time()
    print("Games/sec {}".format(1/((endtime-starttime)/itt)))
    
    winners = np.array(winners)
    winnersHist = np.histogram(winners,[0,1,2,3,4])
    print(winnersHist)
    print("Wins {}".format(winnersHist[0]))

    fig, (ax1, ax2) = plt.subplots(2, 1)

    num_bins = 5
    n, bins, patches = ax1.hist(winners, 4, facecolor='blue', alpha=0.5)

    windowSize = 100
    winFreq = np.zeros((itt-windowSize,4),dtype=int)
    for i in range(itt-windowSize):
        for pi in range(4):
           # print(winners[i:i+windowSize])
            winFreq[i,:]=np.histogram(winners[i:i+windowSize],[0,1,2,3,4])[0]
    
    for i in range(4):
        ax2.plot(winFreq[:,i]*(100.0/windowSize),label="Player {}".format(i))
        ax2.legend()
    plt.show()
