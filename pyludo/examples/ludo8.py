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

myplayer.learning_rate = 0.2
myplayer.discount_rate = 0.1

scores = {}
for player in players:
    scores[player.name] = 0

n = 200
m = 500

for j in range(m):
    for i in range(n):
        random.shuffle(players)
        ludoGame = LudoGame(players)
        winner = ludoGame.play_full_game()
        scores[players[winner].name] += 1
        print('Game ', i+j*n, ' done')
        #print(myplayer.Q)

    myplayer.save_q_stats(filename='ludoStats8.csv', games_played=((j+1)*n), wins=(float(scores['qludo'])))
    myplayer.epsilon /= 1.01
    myplayer.learning_rate /= 1.015
    myplayer.discount_rate /= 1.025

myplayer.saveQtable('Qtablefile8.csv')

print('win distribution:', scores)
