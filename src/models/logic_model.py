from bisect import insort
from mlsolver.kripke import *
from mlsolver.formula import *
from cluedoClasses import SolAtom, AgentCard, CluedoWorld

def buildWorlds(weapons, people, rooms, agents, type, nextAgent, dealt):
  print(type, nextAgent, dealt)

  if len(dealt) == len(weapons) + len(people) + len(rooms):
    assignment = {}
    for i_atom in range(0, len(dealt)):
      assignment[str(dealt[i_atom])] = True;
    return [World(str(CluedoWorld(dealt)), assignment)]

  worlds = []

  if type == 'w':
    
    if nextAgent < 0:
      for weapon in weapons:
        dealt.append(SolAtom('w', weapon))
        worlds += buildWorlds(weapons, people, rooms, agents, 'p', -1, dealt)
        dealt.pop()
      return worlds

    else:
      for weapon in weapons:
        weapons.remove(weapon)
        dealt.append(AgentCard('w', weapon, nextAgent))
        worlds += buildWorlds(weapons, people, rooms, agents, 'p', (nextAgent + 1) % len(agents), dealt)
        insort(weapons, weapon)
      return worlds

  if type == 'p':

    if nextAgent < 0:
      for person in people:
        dealt.append(SolAtom('p', person))
        worlds += buildWorlds(weapons, people, rooms, agents, 'r', -1, dealt)
        dealt.pop()
      return worlds

    else:
      for person in people:
        people.remove(person)
        dealt.append(AgentCard('p', person, nextAgent))
        worlds += buildWorlds(weapons, people, rooms, agents, 'r', (nextAgent + 1) % len(agents), dealt)
        insort(people, person)
      return worlds
      
  if type == 'r':

    if nextAgent < 0:
      for room in rooms:
        dealt.append(SolAtom('r', room))
        worlds += buildWorlds(weapons, people, rooms, agents, 'w', 0, dealt)
        dealt.pop()
      return worlds

    else:
      for room in rooms:
        rooms.remove(room)
        dealt.append(AgentCard('r', room, nextAgent))
        worlds += buildWorlds(weapons, people, rooms, agents, 'w', (nextAgent + 1) % len(agents), dealt)
        insort(rooms, room)
      return worlds

# from agent_model import Player

n_agents = 3
agents = ['a','b','c']
n_weapons = 2
weapons = list(range(0, n_weapons))
n_people = 2
people = list(range(0, n_people))
n_rooms = 2
rooms = list(range(0, n_rooms))

worlds = buildWorlds(weapons, people, rooms, agents, 'w', -1, [])
print(worlds)

# agent = Player(1, 75)
# agent.setAtributes(2, 7, 5)
# agent.weapon = 5
# agent.askPlayer(1, "weapon")

# print(agent.weapon)

# ks = KripkeStructure(worlds, relations)
# print(len(ks.worlds))
# print(ks.solve(And(And(Atom('w1'),Atom('p1')),Atom('r1'))))
