import pickle
import random
from itertools import cycle

import pygame
from pygame.locals import USEREVENT
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
    except:
        print('invalid input')
agents = listAgents(n_agents)

n_weapons = 0
while n_weapons > 10 or n_weapons < 1:
    try:
        n_weapons = int(input('Number of weapons (must be 1-10): '))
    except:
        print('invalid input')

n_people = 0
while n_people > 10 or n_people < 1:
    try:
        n_people = int(input('Number of people (must be 1-10): '))
    except:
        print('invalid input')

n_rooms = 0
while n_rooms > 10 or n_rooms < 1:
    try:
        n_rooms = int(input('Number of rooms (must be 1-10): '))
    except:
        print('invalid input')


def initializeGame(agents: list[str], n_weapons: int, n_people: int, n_rooms: int) -> CluedoGameModel:
    model = CluedoGameModel(agents, n_weapons, n_people, n_rooms)
    model.dealCards(n_weapons, n_people, n_rooms)
    return model

def nextMove(model: CluedoGameModel, current_agent: Player):
    
    # right now the cards the agent asks for are based on random choosing (this might not be correct)
    # TODO: update cards selection based on knowledge in case it is needed
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
    cards = ['w' + str(weapon), 'p' + str(person), 'r' + str(room)]

    if model.turn > -1:
        model.movesHistory.append('Turn ' + str(model.turn) + ': Agent ' + str(current_agent) + ' asks for cards: ' + cards[0] + ' ' + cards[1] + ' ' + cards[2])
        cards_showed = askForCards(current_agent, model.schedule.agents, cards, model)
        if (len(cards_showed) == 0):
            model.movesHistory.append('No agents responded')
        model.movesHistory += cards_showed
        # model.movesHistory.append('Next Move')# delete when actions implemented
        model.drawKnowledge()
        model.drawActions()
    else:
        model.drawKnowledge()
        model.drawActions()

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
                    break
                else:
                    model.agentSaysNo(player, question)
        return cards_showed

def runGame(model):
    #TICK = USEREVENT + 1
    #pygame.time.set_timer(TICK, 1000)
    while True:
        buttonClicked = False
        model.mouse['click'] = -1
        model.checkInterfaceAction(pygame.event.get())
        buttonClicked = model.clickCheck()
        if buttonClicked:
            #model.checkGameOver('a', 'w' + str(model.target_cards['weapon']), 'p' + str(model.target_cards['person']), 'r' + str(model.target_cards['room']))
            if model.gameInProgress != -1:
                nextMove(model, model.schedule.agents[model.turn % len(model.schedule.agents)])
                model.turn += 1
        pygame.display.update()

# After this point the kripke structure, model and agents are initialized, but the agents do not have cards in thier hands

"""kripke_structure = initializeKripke(
    agents=agents,
    n_weapons=n_weapons,
    n_people=n_people,
    n_rooms=n_rooms
    )"""


# TODO: (DONE) find a way to update the hands of each agent so that they stay in line with the relations in the kripke structure
# an agents hand is updated using model.schedule.agent[i].setAtributes(weapon, person, room), i is the number of the agent so: a -> 0 and so on
# Not all atributes have to be given in the function setAtributes().


model = initializeGame(agents, n_weapons, n_people, n_rooms)
# TODO: Make mouse inputs work, at the moment the game doesn't work properly, 
# it has to be shut down by force, to see results in terminal and not game interface 
# comment out runGame(Model) 

runGame(model)