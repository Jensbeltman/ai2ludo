##Local indexes
homeI = 0

# Goal area
goalI = 57 # local goal index
goalAreaStartI = 52 # local index where goal are starts
#Stars
starI = [6,12,19,25,32,38,45,51] # start indexes
starAtGoalI = 51 # star infront of goal area
#Globes
globeAtStartI = [1]
globeEnemy = [14,27,40]
globeSafeI = [1,9,22,35,48] 
globeI = [1,9,14,22,27,35,40,48]

#Global indexes
# number of players,pieces,params etc
n_players = 4 
n_pieces = 4
n_pieceParams = 10

globeDie = 3
starDie = 5

#Move events
#None
#EnemyPiece -> Home
#MovedPiece -> Home (two enemys)
#MovedPiece -> Home (enemy on globe)
#MovedPiece -> Goal Area
#MovedPiece -> Goal
#MovedPiece -> Goal(Goal start was hit)
#Start was hit MovedPiece -> Next start
