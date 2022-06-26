import pickle
import random
from itertools import cycle

from pygame import display
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


def runGame(model):
    quit = False
    while not quit:
        display.update()
        model.mouse['l_down'] = -1
        model.mouse['l_up'] = -1
        model.key = None
        # so the model doesn't get stuck
        # pygame.quit()

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
# runGame(model)
for i in range(len(model.schedule.agents)):
    print(model.schedule.agents[i].weapons, model.schedule.agents[i].people, model.schedule.agents[i].rooms)

model.agentSaysNo('a', Question('b', 0, 0, 0))

for w in model.ks.worlds:
    print(w.name)