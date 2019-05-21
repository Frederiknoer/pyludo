from pyludo import LudoGame, LudoPlayerRandom
import random
import time

import sys
sys.path.append('pyludo/')
from Qludo import Qludo

players = [LudoPlayerRandom() for _ in range(3)]
players.append(Qludo())
for i, player in enumerate(players):
    player.id = i

score = [0, 0, 0, 0]

n = 1000

start_time = time.time()
for i in range(n):
    random.shuffle(players)
    ludoGame = LudoGame(players)
    winner = ludoGame.play_full_game()
    score[players[winner].id] += 1
    print('Game ', i, ' done')
duration = time.time() - start_time

print('win distribution:', score)
print('games per second:', n / duration)
