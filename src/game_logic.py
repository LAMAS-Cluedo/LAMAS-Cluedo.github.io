import pickle
from models.logic_model import initializeKripke
from models.mlsolver.kripke import *
from models.mlsolver.formula import *
from models.cluedo import *

agents = 3
n_weapons = 4
n_people = 4
n_rooms = 4


kripke_structure = initializeKripke(
    agents=agents,
    n_weapons=n_weapons,
    n_people=n_people,
    n_rooms=n_rooms
    )


print(len(kripke_structure.worlds))
for agent in listAgents(agents):
    print(agent + ':', len(kripke_structure.relations[agent]))

#agent = Player(1, 75)
#print(agent)
# agent.setAtributes(2, 7, 5)
# agent.weapon = 5
# agent.askPlayer(1, "weapon")

# print(agent.weapon)
