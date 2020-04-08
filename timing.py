import time
import numpy as np
from random import randint

def cvtPiecePos(pieceI,playerI,playerJ):
    piece=pieceI
    if playerI<playerJ:
        d = playerJ-playerI
        if pieceI<d*13:
            piece = pieceI+50-13*d
        else:
            piece = pieceI-13*d
    else:
        d = playerI-playerJ
        if pieceI<d*13:
            piece = pieceI-50+13*d
        else:
            piece = pieceI+13*d
    return piece

if __name__ == "__main__":


    ri = randint(0,57)
    time_start = time.time()
    for i in range(1000000):
        x=cvtPiecePos(ri,1,1)
    time_end = time.time()
    print(time_end-time_start)

    table = [[i for i in range(580)] for _ in range(3)]
    time_start = time.time()
    for i in range(1000000):
        x=table[ri]
    time_end = time.time()
    print(time_end-time_start)


