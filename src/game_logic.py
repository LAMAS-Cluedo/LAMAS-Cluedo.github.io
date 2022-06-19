import pickle
import random
from models.logic_model import initializeKripke
from models.game_model import CluedoGameModel
from models.mlsolver.kripke import *
from models.mlsolver.formula import *
from models.cluedoClasses import SolAtom, AgentCard, CluedoWorld

agents = ['a','b','c']
n_weapons = 3
n_people = 3
n_rooms = 3

weapons = list(range(0, n_weapons))
people = list(range(0, n_people))
rooms = list(range(0, n_rooms))

model = CluedoGameModel(agents, n_weapons, n_people, n_rooms)

# After this point the kripke structure, model and agents are initialized, but the agents do not have cards in thier hands

"""kripke_structure = initializeKripke(
    agents=agents,
    n_weapons=n_weapons,
    n_people=n_people,
    n_rooms=n_rooms
    )"""


# TODO: find a way to update the hands of each agent so that they stay in line with the relations in the kripke structure
# an agents hand is updated using model.schedule.agent[i].setAtributes(weapon, person, room), i is the number of the agent so: a -> 0 and so on
# Not all atributes have to be given in the function setAtributes().
print(len(model.ks.worlds))
print(model.schedule.agents[0].rooms)


#agent = Player(1, 75)
#print(agent)
# agent.setAtributes(2, 7, 5)
# agent.weapon = 5
# agent.askPlayer(1, "weapon")

# print(agent.weapon)
