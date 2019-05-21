from pyludo import LudoGame
from pyludo.StandardLudoPlayers import LudoPlayerRandom, LudoPlayerFast, LudoPlayerAggressive, LudoPlayerDefensive
import random
import time
import math

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

training_scores = {}
q_scores = {}
for player in players:
    q_scores[player.name] = 0
for player in players:
    training_scores[player.name] = 0

m = 200
n = 100
t = 5
#start_time = time.time()
q_gms_played = 0
t_gms_played = 0

myplayer.TRAINING = False
print('Ludo started...')
for j in range(m):
    for player in players:
        q_scores[player.name] = 0

    q_gms_played = 0
    if myplayer.TRAINING:
        int = t
    else:
        int = n

    for i in range(int):
        random.shuffle(players)
        ludoGame = LudoGame(players)
        winner = ludoGame.play_full_game()
        if myplayer.TRAINING:
            training_scores[players[winner].name] += 1
            t_gms_played += 1
        else:
            q_scores[players[winner].name] += 1
            q_gms_played += 1


    if myplayer.TRAINING == False:
        print('Training games played: ', t_gms_played)

        q_score = float(q_scores['qludo'])
        win_pct = (q_score/q_gms_played)*100
        print('Win %: ', win_pct)
        #print(myplayer.Q)

        myplayer.save_stats(is_training=False, games_trained=t_gms_played, games_played=q_gms_played, wins=q_scores['qludo'])
        myplayer.TRAINING = True

    elif myplayer.TRAINING == True:
        myplayer.saveQtable()
        myplayer.save_stats(is_training=True, games_trained=0, games_played=t_gms_played, wins=training_scores['qludo'])
        myplayer.TRAINING = False


    #duration = time.time() - start_time
    #print('win distribution:', scores)
    #print('games per second:', n / duration)
