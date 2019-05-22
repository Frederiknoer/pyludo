import numpy as np
import math
import os
import sys
import random
import csv


class Qludo:
    def __init__(self):
        print("QLUDO OBJECT CREATED")

        self.playerId = 0
        self.name = 'qludo'
        self.id = 0
        self.goalLineStartPos = (52 + (self.playerId*5))

        self.Qstate = 1


        self.Q = np.zeros((7,10), dtype=int)


        self.R = np.array([
                            [ 150, -1,  -1,   -1,   -1, -1,  -1,  -1, -200, -1 ], #HOME
                            [ -1, 140, 175,  250,  200,  1, 170, 220, -200, 15 ], #@ SAFE GLOBE
                            [ -1, 140, 175,  250,  200,  1, 170, 220, -200, 15 ], #@ RISKY GLOBE
                            [ -1,  70, 175,  250,  100,  1, 100,  50, -200,  1 ], #@ DOUBLE PLAYER SAFE HOME
                            [ -1,  -1,  -1,  250,   -1, -1,  -1,  -1, -200, 15 ], #IN GOAL LINE
                            [ -1,  -1,  -1,   -1,   -1, -1,  -1,  -1, -200, -1 ], #IN GOAL
                            [ -1, 140, 175,  250,  200,  1, 170, 220, -200, 15 ]  #OTHER
                            ])

        self.Action = -1
        self.epsilon = 1

        self.learning_rate = 0.01
        self.discount_rate = 0.005

        self.Qactions = [None]*4
        self.Qstates = [None]*4

    def loadQtable(self):
        with open('Qtablefile.csv', mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            linecount = 0
            for i, row in enumerate(csv_reader):
                self.Q[i][:] = row

    def saveQtable(self, filename):
        with open(filename, mode='w') as q_file:
            q_writer = csv.writer(q_file, delimiter=',')
            for i in range(7):
                q_writer.writerow(self.Q[i][:])

    def updateQTable(self, state, action, next_state):
        self.Q[state][action] = self.Q[state][action] + self.learning_rate * (self.R[state][action] + self.discount_rate * max(self.Q[next_state][:] - self.Q[state][action]))

    def is_safe_globe_pos(self, pos):
        if pos % 13 == 1:
            return True
        return False

    def is_risky_globe_pos(self, pos):
        if pos % 13 == 9:
            return True
        return False

    def is_star(self, pos):
        if pos == -1 or pos > 51:
            return False
        if pos % 13 == 6:
            return True
        if pos % 13 == 12:
            return True

    def checkPossibleActions(self, diceRoll, playerPositions, rel_next_states):
        self.Qactions = [None]*4
        opponents = []

        for i in range(1,4):
            for j in range(4):
                opponents.append(playerPositions[i][j])

        for next_state in rel_next_states:
            if next_state is not False:
                #print("next state: ", next_state[0])
                for i, n_state in enumerate(next_state[0]):
                    #CHECK IF ANY TOKEN IS FORCED TO DO SUICIDE
                    if n_state == -1 and playerPositions[0][i] != -1:
                        self.Qactions[i] = 8
                    #CONTINUE IF NEXT STATE IS IN HOME OR CURRENT STATE IS IN GOAL
                    if n_state == -1 or playerPositions[0][i] == 99:
                        continue
                    #CHECK IF ANY HOMED TOKEN CAN GO OUT:
                    if n_state == 1 and playerPositions[0][i] == -1:
                        self.Qactions[i] = 0
                    #CHECK IF ANY ANY OPPONENT CAN BE KILLED:
                    elif any(x == n_state for x in opponents) and not self.is_risky_globe_pos(n_state) and not self.is_safe_globe_pos(n_state) and playerPositions[0][i] < 52 and not any(x == 99 for x in opponents):
                        self.Qactions[i] = 1
                    #CHECK IF ANY TOKEN CAN ENTER GOALLINE
                    elif n_state >= 52 and n_state < 57 and playerPositions[0][i] < 52:
                        self.Qactions[i] = 2
                    #CHECK IF ANY TOKEN CAN ENTER GOAL
                    elif n_state == 99:
                        self.Qactions[i] = 3
                    #CHECK IF ANY TOKEN CAN BE PLACED ON A SAFE GLOBE
                    elif self.is_safe_globe_pos(n_state):
                        self.Qactions[i] = 4
                    #CHECK IF ANY TOKEN CAN BE PLACED ON A RISKY GLOBE
                    elif self.is_risky_globe_pos(n_state):
                        self.Qactions[i] = 5
                    #CHECK IF TOKEN CAN BE MOVED TO A STAR
                    elif self.is_star(n_state):
                        self.Qactions[i] = 6
                    #CHECK IS TWO TOKENS CAN MAKE A SAFE PLACE
                    elif not self.is_risky_globe_pos(n_state) and not self.is_safe_globe_pos(n_state):
                        for j, nx_state in enumerate(next_state[0]):
                            if nx_state == n_state and j != i:
                                self.Qactions[i] = 7
                            else:
                                self.Qactions[i] = 9


    def getActullyState(self, playerPos):
        self.Qstates = [None]*4
        for i, pos in enumerate(playerPos):
            if pos == -1:
                self.Qstates[i] = 0
            elif self.is_safe_globe_pos(pos):
                self.Qstates[i] = 1
            elif self.is_risky_globe_pos(pos):
                self.Qstates[i] = 2
            elif not self.is_risky_globe_pos(pos) and not self.is_safe_globe_pos(pos):
                for j, xpos in enumerate(playerPos):
                    if xpos == pos and j != i and pos != 99:
                        self.Qstates[i] = 3
                    elif pos > 51 and pos < 57:
                        self.Qstates[i] = 4
                    elif pos == 99:
                        self.Qstates[i] = 5
                    else:
                        self.Qstates[i] = 6

    def getNextState(self, rel_next_states):
        for next_state in rel_next_states:
            if next_state is not False:
                for i, n_state in enumerate(next_state[0]):
                    if n_state == -1:
                        state = 0
                    elif self.is_safe_globe_pos(n_state):
                        state = 1
                    elif self.is_risky_globe_pos(n_state):
                        state = 2
                    elif  not self.is_risky_globe_pos(n_state) and not self.is_safe_globe_pos(n_state):
                        for j, nx_state in enumerate(next_state[0]):
                            if nx_state == n_state and j != i and n_state != 99:
                                state = 3
                            elif n_state > 51 and n_state < 57:
                                state = 4
                            elif n_state == 99:
                                state = 5
                            else:
                                state = 6
        return state

    def makeDecision(self):
        IdxList = []
        self.Action = -1
        actionsList = []

        for i in range(4):
            if self.Qactions[i] != None:
                IdxList.append(i)

        if len(IdxList) > 0:
            for i in range(len(IdxList)):
                actionsList.append(self.Qactions[IdxList[i]])
            self.Action = IdxList[random.randint(0,len(IdxList)-1)]

    def makeQtableDecision(self):
        max_value = -999
        idx = -1

        for i in range(4):
            if self.Qactions[i] != None:
                #print("I: ", i , "  Q-value: ", self.Q[self.Qstates[i]][self.Qactions[i]])
                if self.Q[self.Qstates[i]][self.Qactions[i]] > max_value:
                    max_value = self.Q[self.Qstates[i]][self.Qactions[i]]
                    idx = i

        self.Action = idx

    def chooseAction(self, rel_next_states):
        if self.epsilon == 0 or (random.randint(1,1000) / 1000) > self.epsilon:
            self.makeQtableDecision()
        else:
            self.makeDecision()
            nextState = self.getNextState(rel_next_states)
            self.updateQTable(self.Qstates[self.Action], self.Qactions[self.Action], nextState)
        pass

    def play(self, relative_state, diceRoll, rel_next_states):
        #print("\n")
        self.getActullyState(relative_state[0])
        self.checkPossibleActions(diceRoll, relative_state, rel_next_states)
        self.chooseAction(rel_next_states)

        #print("diceRoll: ", diceRoll)
        #print("relative_state: ", relative_state[0])
        #print("Qstates: ", self.Qstates)
        #print("Qactions:", self.Qactions)
        #print("Action: ", self.Action)

        return self.Action

    def save_q_stats(self, filename, games_played, wins):
        with open(filename, mode='a') as stat_file:
            stat_writer = csv.writer(stat_file, delimiter=';')
            stat_writer.writerow([games_played, (wins/games_played)*100, self.epsilon])

'''
    def save_stats(self, is_training, games_trained, games_played, wins):
        if not is_training:
            with open('ludoStats_usingQtable.csv', mode='a') as stat_file1:
                stat_writer1 = csv.writer(stat_file1, delimiter=',')
                stat_writer1.writerow([games_trained, (wins/games_played)*100])
        else:
            with open('ludoStats_training.csv', mode='a') as stat_file2:
                stat_writer2 = csv.writer(stat_file2, delimiter=',')
                stat_writer2.writerow([games_played, wins])
'''

if __name__ == '__main__':
    print("Running Q Ludo")
