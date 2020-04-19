from ludoCore import Game, Player
import numpy as np
from random import randint, random
from params import *

class QPlayer(Player):
    def __init__(self,playerI,action = 0, epsilon = 0.3, alpha = 0.5, gamma = 0.9):
        super().__init__(playerI)
        self.action = action
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.Q = {}
        self.state = ''
        self.action = 0

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

                nMovablePieces = moveablePieces.size
                if nMovablePieces>1:
                    maxq = self.Q[self.state][moveablePieces[0]]
                    maxi = [moveablePieces[0]]    
                    for i in moveablePieces[1:]:
                        q = self.Q[self.state][i]
                        if q > maxq:
                            maxq = q
                            maxi = [i]
                        elif q == maxq:
                            maxi.append(i)
                    if len(maxi)>1:
                        pieceTM = int(np.random.choice(maxi))
                    else:
                        pieceTM = maxi[0]
                elif nMovablePieces==1:
                    pieceTM = moveablePieces[0]
                else: 
                    print("No movable pieces something is wrong")

        self.action = pieceTM
        return pieceTM

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

class QGame(Game):
    def __init__(self,verbose=False):
        super().__init__(verbose)
        self.players = [QPlayer(i) for i in range(self.nrPlayers)] # type: List[Player]
        self.rewards = [0,0,0,0]
        self.gameLen = 0

    def getReward(self,prevPieceP, newPieceP, colEvent,stateVal):
        reward = 0.0
        dPieceP = newPieceP - prevPieceP

        # Collision Reward
        if colEvent == None:
            reward+=dPieceP
        elif colEvent == sentHomeEnemy:
            reward+=dPieceP*2
        elif colEvent == sentHomePlayer:
            reward-=dPieceP
        
        # Safe Reward
        if stateVal[2] or stateVal[4]:# if on safe globe or goal area
            reward+=dPieceP*2
        
        # Move piece into goal 
        if newPieceP == goalI:
            reward+=20+dPieceP

        # Move player to start 
        if newPieceP == startI:
            reward += 12

        return reward

    def getState(self,player):
        moveablePieces = player.moveablePieces().flatten()
        stateVals = []
        colInfo = [] 
        for pieceI in range(4):
            if pieceI in moveablePieces:
                newPieceP = player.getNewPiecePos(pieceI)
                if newPieceP in starI:
                    newPieceP = self.handleStar(player,newPieceP,pieceI)

                n_col, enemy, colPos, colPieceIds = self.getCollisions(player,newPieceP) # TODO take advantage of calculated collisions
                colInfo.append([newPieceP,n_col,enemy, colPos, colPieceIds])
                
                enemyCol = n_col
                start = int(newPieceP == 0)
                globe = int(newPieceP in globeSafeI)
                star = int(newPieceP in starI)
                goalA = int(newPieceP >= goalAreaStartI)
                stuck =  0
                stateVals.extend([enemyCol,start,globe,star,goalA,stuck])
            else:
                stateVals.extend([0,0,0,0,0,1])
                colInfo.append([None,0,None,None,[]])
    
        state =  "".join(map(str,stateVals))
         
        return state, stateVals ,colInfo 

    def run(self,saveReplay=False,replayPath='ludoReplay.txt'):
        replayFile = None
        if saveReplay:
            replayFile = open(replayPath,'w+')


        for player in self.players:
            newState, stateVals ,colInfo  = self.getState(player)
            player.state =  newState
        
        while self.winner is None:
            self.gameLen+=1
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
                    newPieceP,n_col,enemy, colPos, colPieceIds = colInfo[pieceI]
                    prevPieceP,newPieceP, colEvent = self.handleMove(player,pieceI,newPieceP, n_col, enemy, colPos, colPieceIds)
                                                                    #(player,pieceI,newPieceP, n_col, enemy, colPos, colPieceIds
                    #---Qlearning---
                    reward = self.getReward(prevPieceP, newPieceP, colEvent, stateVal=stateVals[pieceI*6:pieceI*6+6])
                    self.rewards[player.playerI] = reward
                    #---------------
                    if self.checkForWinner(player):
                        break
                        
        if saveReplay:
            replayFile.close()

if __name__ == "__main__":
    import time
    import json
    import matplotlib.pyplot as plt

    # Read data from file:
    bestQ = json.load( open( "bestQ.json" ) )
    game = QGame(verbose=False)
    game.players[0].Q =bestQ
    game.players[0].epsilon = 0.01
    game.players[1].epsilon = 1
    game.players[2].epsilon = 1
    game.players[3].epsilon = 1
    game.players[0].alpha = 0.1
    game.players[1].alpha = 0.4
    game.players[2].alpha = 0.6
    game.players[3].alpha = 0.8
    itt =1000
    winners = [-1 for i in range(itt)]
    QSize = []
    GameLen = []
    starttime = time.time()
    print('')

    for i in range(itt):
        game.run(saveReplay=False)
        QSize.append([len(p.Q) for p in game.players])
        GameLen.append(game.gameLen)
        winners[i]=game.winner.playerI
        game.reset()
        print(" Game number \t {}".format(i), end='\r')
        #print("Game number \t {} Qentrys\t {} \t Gamelen {} ".format(i,QSize[i],GameLen[i]), end='\r')
    endtime = time.time()
    for player in game.players:
        print(len(player.Q))
    print("Game number \t"+str(itt), end='\n')
    print("Games/sec {}".format(1/((endtime-starttime)/itt)))
    
    winners = np.array(winners)
    winnersHist = np.histogram(winners,[0,1,2,3,4])
    print(winnersHist)
    print("Wins {}".format(winnersHist[0]))
   

    fig, ax = plt.subplots(4, 1) 
    

    num_bins = 5
    #n, bins, patches = ax[0].hist(winners, 4, facecolor='blue', alpha=0.5)
    ax[0].bar([1,2,3,4],winnersHist[0])
    ax[0].tick_label = ["P{}".format(i+1) for i in range(4)]
    windowSize = 10
    winFreq = np.zeros((itt-windowSize,4),dtype=int)
    for i in range(itt-windowSize):
        for pi in range(4):
           # print(winners[i:i+windowSize])
            winFreq[i,:]=np.histogram(winners[i:i+windowSize],[0,1,2,3,4])[0]
    
    ax[1].plot(winFreq*(100.0/windowSize))
    ax[2].plot(QSize)
    ax[3].plot(GameLen)


    ax[1].legend(["P{}".format(i+1) for i in range(4)])
    ax[2].legend(["P{}".format(i+1) for i in range(4)])

    

    # Serialize data into file:
    json.dump( game.players[0].Q, open( "bestQ.json", 'w' ) )

    plt.show()
