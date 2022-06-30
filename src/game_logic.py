from email.mime import base
import pickle
import random
from itertools import cycle
from turtle import pos
from black import Set
from numpy import true_divide

import pygame
from pygame.locals import USEREVENT
from pyparsing import null_debug_action
from models.agent_model import Player

from models.logic_model import initializeKripke
from models.game_model import CluedoGameModel
from models.mlsolver.kripke import *
from models.mlsolver.formula import *
from models.cluedo import *

n_agents = 0
while n_agents > 6 or n_agents < 2:
    try:
        n_agents = int(input('Number of players (must be 2-6): '))
    except ValueError:
        print('invalid input')
agents = listAgents(n_agents)

n_high_order = -1
while n_high_order > n_agents or n_high_order < 0:
    try:
        n_high_order = int(input('Number of players using high order knowledge: '))
        if n_high_order > n_agents:
            print('Number cannot be higher than the number of players')
        if n_high_order < 0:
            print('Number cannot be negative')
    except ValueError:
        print('invalid input')

n_weapons = 0
while n_weapons > 10 or n_weapons < 1:
    try:
        n_weapons = int(input('Number of weapons (must be 1-10): '))
    except ValueError:
        print('invalid input')

n_people = 0
while n_people > 10 or n_people < 1:
    try:
        n_people = int(input('Number of people (must be 1-10): '))
    except ValueError:
        print('invalid input')

n_rooms = 0
while n_rooms > 10 or n_rooms < 1:
    try:
        n_rooms = int(input('Number of rooms (must be 1-10): '))
    except ValueError:
        print('invalid input')

base_on_knowledge = None
while base_on_knowledge != 'y' and base_on_knowledge != 'n':
    try:
        base_on_knowledge = input("Base questions on agent's knowledge? (respond with y/n): ")
    except ValueError:
        print('invalid input')
if base_on_knowledge == 'y':
    base_on_knowledge = True
else:
    base_on_knowledge = False
    print('Questions will be chosen randomly')

def initializeGame(agents: list[str], n_weapons: int, n_people: int, n_rooms: int, n_high_order: int) -> CluedoGameModel:
    model = CluedoGameModel(agents, n_weapons, n_people, n_rooms, n_high_order)
    model.dealCards(n_weapons, n_people, n_rooms)
    return model

def decideRandomQuestion(model: CluedoGameModel, current_agent: Player) -> list:
    try:
        weapon = random.choice(list(range(0, model.n_weapons)).remove(int(current_agent.weapons[-1])))
    except (TypeError, IndexError):
        weapon = random.choice(list(range(0, model.n_weapons)))
    try:    
        person = random.choice(list(range(0, model.n_people)).remove(int(current_agent.people[-1])))
    except (TypeError, IndexError):
        person = random.choice(list(range(0, model.n_people)))
    try:
        room = random.choice(list(range(0, model.n_rooms)).remove(int(current_agent.rooms[-1])))
    except (TypeError, IndexError):
        room = random.choice(list(range(0, model.n_rooms)))
    return ['w' + str(weapon), 'p' + str(person), 'r' + str(room)]

def decideQuestionWithKnowledge(model: CluedoGameModel, current_agent: Player):
    weapons = set(range(0, model.n_weapons))
    people = set(range(0, model.n_people))
    rooms = set(range(0, model.n_rooms))
    for possibilities in model.getPossibleSolutions(current_agent):
        possibilitiesSplit = possibilities.split()
        weapons = weapons.difference({int(possibilitiesSplit[0][1])})
        people = people.difference({int(possibilitiesSplit[1][1])})
        rooms = rooms.difference({int(possibilitiesSplit[2][1])})
    weapons = weapons.difference(set(current_agent.weapons))
    people = people.difference(set(current_agent.people))
    rooms = rooms.difference(set(current_agent.rooms))
    weapon = random.choice(list(set(range(0, model.n_weapons)).difference(weapons)))
    person = random.choice(list(set(range(0, model.n_people)).difference(people)))
    room = random.choice(list(set(range(0, model.n_rooms)).difference(rooms)))
    return ['w' + str(weapon), 'p' + str(person), 'r' + str(room)]

def nextMove(model: CluedoGameModel, current_agent: Player, base_on_knowledge: bool):
    if base_on_knowledge:
        cards = decideQuestionWithKnowledge(model, current_agent)
    else:
        cards = decideRandomQuestion(model, current_agent)
    
    model.movesHistory.append('Turn ' + str(model.turn) + ': Agent ' + str(current_agent) + ' asks for cards: ' + cards[0] + ' ' + cards[1] + ' ' + cards[2])
    model.drawActions()

    cards_showed = askForCards(current_agent, model.schedule.agents, cards, model)
    if (len(cards_showed) == 0):
        model.movesHistory.append('No agents responded')
    model.movesHistory += cards_showed
    # model.movesHistory.append('Next Move')# delete when actions implemented
    model.drawKnowledge()
    model.drawActions()
    pass

def askForCards(agent: Player, other_players, cards: list[str], model: CluedoGameModel) -> list[str]:
        question = Question(str(agent), int(cards[0][-1]), int(cards[1][-1]), int(cards[2][-1]))
        cards_showed = []
        for i_player in range(0, len(other_players)-1):
            player = other_players[(model.turn+1+i_player)%len(other_players)]
            cards_to_show = []
            if player != agent:
                for card in cards:
                    if ((int(card[-1]) in player.weapons) and card[0] == 'w') or \
                         ((int(card[-1]) in player.people) and card[0] == 'p') or \
                              ((int(card[-1]) in player.rooms) and card[0] == 'r'):
                        cards_to_show.append(card)
                if cards_to_show:
                    show = random.choice(cards_to_show)
                    agent.updateKnowledge(show)
                    model.agentResponds(str(player), question, model.turn)
                    cards_showed.append('Agent ' + str(player) + ' showed card ' + show + ' to Agent ' + str(agent))
                    if len(cards_to_show) > 1:
                        model.trueWorld.shownCardChoices.append(AgentShownChoice((show[0]), int(show[1]), str(player), model.turn)) 
                    break
                else:
                    model.agentSaysNo(player, question)
        return cards_showed

def runGame(model, base_on_knowledge):
    #TICK = USEREVENT + 1
    #pygame.time.set_timer(TICK, 1000)
    while True:
        buttonClicked = False
        model.mouse['click'] = -1
        model.parse_events(pygame.event.get())
        buttonClicked = model.clickCheck()
        if buttonClicked:
            model.turn += 1
            nextMove(model, model.schedule.agents[model.turn % len(model.schedule.agents)], base_on_knowledge)
        pygame.display.update()

# After this point the kripke structure, model and agents are initialized, but the agents do not have cards in thier hands

model = initializeGame(agents, n_weapons, n_people, n_rooms, n_high_order)

runGame(model, base_on_knowledge)