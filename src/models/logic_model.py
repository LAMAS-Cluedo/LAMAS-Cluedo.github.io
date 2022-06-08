from mlsolver.kripke import *
from mlsolver.formula import *

from agent_model import Player

agents = ['a','b']
n_weapons = 3
n_people = 3
n_rooms = 3

worlds = []
for i_weapon in range(0,n_weapons):
  for i_person in range(0,n_people):
    for i_room in range(0,n_rooms):
      worlds.append(World(
        ("("+str(i_weapon)+","+str(i_person)+","+str(i_room)+")"),
        {("w"+str(i_weapon)): True, ("p"+str(i_person)): True, ("r"+str(i_room)): True})
      )

relations = {('(0,0,0)', '(0,0,0)')}

agent = Player(1, 75)
agent.setAtributes(2, 7, 5)
agent.weapon = 5
agent.askPlayer(1, "weapon")

print(agent.weapon)

#ks = KripkeStructure(worlds, relations)
#print(ks.solve(And(And(Atom('w1'),Atom('p1')),Atom('r1'))))
