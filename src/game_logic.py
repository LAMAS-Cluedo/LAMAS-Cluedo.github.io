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

n_agents = int(input())
n_weapons = int(input())
n_people = int(input())
n_rooms = int(input())
agents = listAgents(n_agents)


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
    
    model.movesHistory.append('Agent ' + str(current_agent) + ' asks for cards: ' + cards[0] + ' ' + cards[1] + ' ' + cards[2])
    model.drawActions()

    cards_showed = current_agent.askForCards(model.schedule.agents, cards)# needs changing
    model.movesHistory += cards_showed
    #model.movesHistory.append('Next Move')# delete when actions implemented
    model.drawKnowledge()
    model.drawActions()
    pass

def runGame(model):
    #TICK = USEREVENT + 1
    #pygame.time.set_timer(TICK, 1000)
    while True:
        buttonClicked = False
        model.mouse['click'] = -1
        model.parse_events(pygame.event.get())
        buttonClicked = model.clickCheck()
        if buttonClicked:
            nextMove(model, model.schedule.agents[0])#needs changing
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
for i in range(len(model.schedule.agents)):
    print(model.schedule.agents[i].weapons, model.schedule.agents[i].people, model.schedule.agents[i].rooms)

model.agentSaysNo('a', Question('b', 0, 0, 0))

for w in model.ks.worlds:
    print(w.name)