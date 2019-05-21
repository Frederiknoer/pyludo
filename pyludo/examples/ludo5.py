from pyludo import LudoGame
from pyludo.StandardLudoPlayers import LudoPlayerRandom, LudoPlayerFast, LudoPlayerAggressive, LudoPlayerDefensive
import random
import time

import sys
sys.path.append('pyludo/')
from Qludo import Qludo
myplayer = Qludo()

players = [
    myplayer,
    LudoPlayerRandom(),
    LudoPlayerRandom(),
    LudoPlayerRandom()
    #LudoPlayerFast(),
    #LudoPlayerAggressive(),
    #LudoPlayerDefensive(),
]

myplayer.learning_rate = 0.01
myplayer.discount_rate = 0.005

scores = {}
for player in players:
    scores[player.name] = 0

n = 200
m = 1000

for j in range(m):
    for i in range(n):
        random.shuffle(players)
        ludoGame = LudoGame(players)
        winner = ludoGame.play_full_game()
        scores[players[winner].name] += 1
        print('Game ', i+j*n, ' done')
        #print(myplayer.Q)

    myplayer.save_q_stats(filename='ludoStats5.csv', games_played=((j+1)*n), wins=(float(scores['qludo'])))
    if myplayer.epsilon != 0:
        myplayer.epsilon -= 0.0075
myplayer.saveQtable()

print('win distribution:', scores)
