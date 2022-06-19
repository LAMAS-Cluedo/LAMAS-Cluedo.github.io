import pickle
from models.logic_model import initializeKripke
from models.mlsolver.kripke import *
from models.mlsolver.formula import *
from models.cluedoClasses import SolAtom, AgentCard, CluedoWorld

agents = ['a','b','c']
n_weapons = 3
n_people = 3
n_rooms = 3


kripke_structure = initializeKripke(
    agents=agents,
    n_weapons=n_weapons,
    n_people=n_people,
    n_rooms=n_rooms
    )


print(len(kripke_structure.worlds))


#agent = Player(1, 75)
#print(agent)
# agent.setAtributes(2, 7, 5)
# agent.weapon = 5
# agent.askPlayer(1, "weapon")

# print(agent.weapon)
