import numpy as np
import math
import os
import sys
import random
import csv


class Qludo:
    def __init__(self):
        print("QLUDO OBJECT CREATED")
        self.TRAINING = True

        self.playerId = 0
        self.name = 'qludo'
        self.id = 0
        self.goalLineStartPos = (52 + (self.playerId*5))

        self.Qstate = 1


        self.Q = np.zeros((6,8), dtype=int)
        if not self.TRAINING:
            self.loadQtable()

        self.R = np.array([
                            [ 150, -1, -1,   -1,   -1, -1, -1,  -1 ], #HOME
                            [ -1, 120, 175,  250,  350, 1, 270, 15 ], #@ SAFE GLOBE
                            [ -1, 120, 175,  250,  350, 1, 270, 15 ], #@ RISKY GLOBE
                            [ -1, -1,  -1,   250,  -1, -1,  -1, 15 ], #IN GOAL LINE
                            [ -1, -1,  -1,   -1,   -1, -1,  -1, -1 ], #IN GOAL
                            [ -1, 120, 175,  250,  350, 1, 270, 15 ]  #OTHER
                            ])
        self.Gamma = 0.5
        self.Action = -1

        self.Qactions = [None]*4
        self.Qstates = [None]*4

    def loadQtable(self):
        with open('Qtablefile.csv', mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            linecount = 0
            for i, row in enumerate(csv_reader):
                self.Q[i][:] = row
                #print (row)

    def saveQtable(self):
        with open('Qtablefile.csv', mode='w') as q_file:
            q_writer = csv.writer(q_file, delimiter=',')
            for i in range(6):
                q_writer.writerow(self.Q[i][:])
                #print(self.Q[i][:])

    def updateQTable(self, state, action, next_state):
        self.Q[state][action] = self.R[state][action] + self.Gamma * max(self.Q[next_state][:])

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
        #print("Positions: ", playerPositions[self.playerId])

        for i in range(1,4):
            for j in range(4):
                opponents.append(playerPositions[i][j])

        for i, pos in enumerate(playerPositions[self.playerId]):
            #CHECK IF ANY HOMED TOKEN CAN GO OUT:
            if pos == -1 and diceRoll == 6 and not any(x == 1 for x in playerPositions[self.playerId]):
                self.Qactions[i] = 0
            elif pos != -1 and pos < 52:
                #CHECK IF ANY ANY OPPONENT CAN BE KILLED:
                if any(x == pos+diceRoll for x in opponents) and not self.is_risky_globe_pos(pos+diceRoll) and not self.is_safe_globe_pos(pos+diceRoll):
                    self.Qactions[i] = 1
                #CHECK IF ANY TOKEN CAN BE MOVED IN TO GOAL LINE
                elif (pos+diceRoll >= self.goalLineStartPos) and (pos+diceRoll < self.goalLineStartPos+5): ##THIS IS WRONG!
                    self.Qactions[i] = 2
                #CHECK IF ANY TOKEN CAN ENTER GOAL:
                elif (pos+diceRoll == 57): #THIS IS WRONG!
                    self.Qactions[i] = 3
                #CHECK IF ANY TOKEN CAN BE PLACED ON A SAFE GLOBE
                elif self.is_safe_globe_pos(pos+diceRoll):
                    self.Qactions[i] = 4
                #CHECK IF ANY TOKEN CAN BE PLACED ON A RISKY GLOBE
                elif self.is_risky_globe_pos(pos+diceRoll):
                    self.Qactions[i] = 5
                #CHECK IF TOKEN CAN BE MOVED TO A STAR
                elif self.is_star(pos+diceRoll):
                    self.Qactions[i] = 6
                #CHECK IF ANY CAN DO ANY MOVE:
                elif pos != -1 and pos+diceRoll < 99:
                    self.Qactions[i] = 7
            elif pos > 51 and pos < 57:
                #CHECK IF ANY TOKEN CAN ENTER GOAL:
                if (pos+diceRoll == 57): #THIS IS WRONG
                    self.Qactions[i] = 3
                #CHECK IF ANY CAN DO ANY MOVE:
                else:
                    self.Qactions[i] = 7


    def getActullyState(self, playerPos):
        self.Qstates = [None]*4
        for i, pos in enumerate(playerPos):
            if pos == -1:
                self.Qstates[i] = 0
            elif self.is_safe_globe_pos(pos):
                self.Qstates[i] = 1
            elif self.is_risky_globe_pos(pos):
                self.Qstates[i] = 2
            elif pos > 51 and pos < 57:
                self.Qstates[i] = 3
            elif pos == 99:
                self.Qstates[i] = 4
            else:
                self.Qstates[i] = 5

    def getState(self, pos):
        state = -1
        if pos == -1:
            state = 0
        elif self.is_safe_globe_pos(pos):
            state = 1
        elif self.is_risky_globe_pos(pos):
            state = 2
        elif pos > 51 and pos < 57:
            state = 3
        elif pos == 99:
            state = 4
        else:
            state = 5
        return state

    def makeDecision(self, diceRoll):
        #print ("DiceRoll: ",diceRoll)
        #print("Qstates: ",self.Qstates)
        #print("Qactions ",self.Qactions)
        IdxList = []
        self.Action = -1
        actionsList = []

        for i in range(4):
            if self.Qactions[i] != None and self.Qactions[i] != -1:
                IdxList.append(i)

        if len(IdxList) > 0:
            for i in range(len(IdxList)):
                actionsList.append(self.Qactions[IdxList[i]])
            self.Action = IdxList[random.randint(0,len(IdxList)-1)]

        #print("Action: ", self.Action)


    def makeQtableDecision(self):
        max_value = 0
        idx = -1

        for i in range(4):
            #print("Qstate", self.Qstates[i])
            if self.Qactions[i] != None:
                if self.Q[self.Qstates[i]][self.Qactions[i]] > max_value:
                    max_value = self.Q[self.Qstates[i]][self.Qactions[i]]
                    idx = i

        #print("Token: ", idx)
        self.Action = idx

    def play(self, relative_state, diceRoll, rel_next_states):
        if self.TRAINING:
            self.getActullyState(relative_state[0])
            self.checkPossibleActions(diceRoll, relative_state, rel_next_states)
            self.makeDecision(diceRoll)
            #print("Current state: ", relative_state[0], "\n")
            #print("Chosen state: ", )
            nextState = self.getState(rel_next_states[self.Action][0][self.Action])
            #print("Token: ", self.Action)
            if self.Action != -1:
                #print("State: ", self.Qstates[self.Action], "  Action: ", self.Qactions[self.Action])
                self.updateQTable(self.Qstates[self.Action], self.Qactions[self.Action], nextState)
                #print("\n", self.Q)
            else:
                print('T: DiceRoll', diceRoll, '  token states: ', relative_state[0], '  Action: ', self.Action)
                print('State: ', self.Qstates, '  Action: ', self.Qactions)
            return self.Action
        else:
            #print("DiceRoll: ", diceRoll)
            self.getActullyState(relative_state[0])
            self.checkPossibleActions(diceRoll, relative_state, rel_next_states)
            self.makeQtableDecision()
            if self.Action == -1:
                print('NT: DiceRoll', diceRoll, '  token states: ', relative_state[0], '  Action: ', self.Action)
                print('State: ', self.Qstates, '  Action: ', self.Qactions)
            return self.Action

    def save_stats(self, is_training, games_trained, games_played, wins):
        if is_training:
            with open('ludoStats_usingQtable.csv', mode='a') as stat_file1:
                stat_writer1 = csv.writer(stat_file1, delimiter=',')
                stat_writer1.writerow([games_trained, games_played, wins])
        else:
            with open('ludoStats_training.csv', mode='a') as stat_file2:
                stat_writer2 = csv.writer(stat_file2, delimiter=',')
                stat_writer2.writerow([games_played, wins])


if __name__ == '__main__':
    print("Running Q Ludo")
