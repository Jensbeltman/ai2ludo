def cvtPiecePos(pieceI,playerI,playerJ):
    if pieceI == 0:
        return None
    if playerI<playerJ:
        d = playerJ-playerI
        if pieceI<d*13:
            return pieceI+52-13*d
        elif pieceI>d*13:
            return pieceI-13*d
    else:
        d = playerI-playerJ
        if pieceI<52-d*13:
            return pieceI+13*d
        elif pieceI>52-d*13:
            return pieceI-(52-d*13)
    return None
        

idx1 = [i for i in range(58)]   
idx12 = [cvtPiecePos(i,1,2) for i in range(58)] 
idx13 = [cvtPiecePos(i,1,3) for i in range(58)] 
idx14 = [cvtPiecePos(i,1,4) for i in range(58)] 
idx21 = [cvtPiecePos(i,2,1) for i in range(58)] 
idx31 = [cvtPiecePos(i,3,1) for i in range(58)] 
idx41 = [cvtPiecePos(i,4,1) for i in range(58)] 



for i in range(58):
    print(idx1[i],idx12[i],idx13[i],idx14[i],idx1[i],idx21[i],idx31[i],idx41[i],sep='\t')

import multiprocessing

    def multiprocessing_func():
        game = Game(verbose=False)
        for _ in range(itt):
            game.run(saveReplay=False)
            game.reset()
            

    processes = []
    nMp= 4*4
    for i in range(nMp):
        p = multiprocessing.Process(target=multiprocessing_func, args=())
        processes.append(p)
        p.start()

    starttime = time.time()
    for process in processes:
        process.join()
    endtime = time.time()
    print("No Mp\t",(endtimeNoMp-starttimeNoMp)/itt)
    print("Mp \t",(endtime-starttime)/(itt*nMp))