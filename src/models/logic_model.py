import pickle
from bisect import insort
from functools import reduce
from mlsolver.kripke import *
from mlsolver.formula import *
from cluedoClasses import SolAtom, AgentCard, CluedoWorld

def buildWorlds(weapons, people, rooms, agents, type, nextAgent, dealt):
  if 0 == len(weapons) + len(people) + len(rooms):
    assignment = {}
    for i_atom in range(0, len(dealt)):
      assignment[str(dealt[i_atom])] = True;
    world = World(str(CluedoWorld(dealt)), assignment)
    return [world]

  worlds = []

  if type == 'w':
    
    if nextAgent < 0:
      for weapon in weapons:
        weapons.remove(weapon)
        dealt.append(SolAtom('w', weapon))
        worlds += buildWorlds(weapons, people, rooms, agents, 'p', -1, dealt)
        insort(weapons, weapon)
        dealt.pop()
      return worlds

    else:
      if len(weapons) == 1:
        nextType = 'p'
      else:
        nextType = 'w'

      for weapon in weapons:
        weapons.remove(weapon)
        dealt.append(AgentCard('w', weapon, agents[nextAgent]))
        worlds += buildWorlds(weapons, people, rooms, agents, nextType, (nextAgent + 1) % len(agents), dealt)
        insort(weapons, weapon)
        dealt.pop()
      return worlds

  if type == 'p':

    if nextAgent < 0:
      for person in people:
        people.remove(person)
        dealt.append(SolAtom('p', person))
        worlds += buildWorlds(weapons, people, rooms, agents, 'r', -1, dealt)
        insort(people, person)
        dealt.pop()
      return worlds

    else:
      if len(people) == 1:
        nextType = 'r'
      else:
        nextType = 'p'

      for person in people:
        people.remove(person)
        dealt.append(AgentCard('p', person, agents[nextAgent]))
        worlds += buildWorlds(weapons, people, rooms, agents, nextType, (nextAgent + 1) % len(agents), dealt)
        insort(people, person)
        dealt.pop()
      return worlds
      
  if type == 'r':

    if nextAgent < 0:
      for room in rooms:
        rooms.remove(room)
        dealt.append(SolAtom('r', room))
        worlds += buildWorlds(weapons, people, rooms, agents, 'w', 0, dealt)
        insort(rooms, room)
        dealt.pop()
      return worlds

    else:
      if len(people) == 1:
        nextType = 'w'
      else:
        nextType = 'r'

      for room in rooms:
        rooms.remove(room)
        dealt.append(AgentCard('r', room, agents[nextAgent]))
        worlds += buildWorlds(weapons, people, rooms, agents, nextType, (nextAgent + 1) % len(agents), dealt)
        insort(rooms, room)
        dealt.pop()
      return worlds

def isPossWorld(world, possWorld, agent):
  for atom in world.assignment.keys():
    if atom[:-2] == agent:
      if atom[-2:] in possWorld.assignment.keys():
        return False
  return True

def buildRelationsFromWorld(world, worlds, agent):
  return [(world, possWorld) for possWorld in worlds if isPossWorld(world, possWorld, agent)]

# from agent_model import Player

agents = ['a','b','c']
n_weapons = 4
weapons = list(range(0, n_weapons))
n_people = 4
people = list(range(0, n_people))
n_rooms = 4
rooms = list(range(0, n_rooms))

worlds = buildWorlds(weapons, people, rooms, agents, 'w', -1, [])

relations = {}
for agent in agents:
  relations[agent] = reduce(lambda it, world: it + buildRelationsFromWorld(world, worlds, agent), worlds, [])

# agent = Player(1, 75)
# agent.setAtributes(2, 7, 5)
# agent.weapon = 5
# agent.askPlayer(1, "weapon")

# print(agent.weapon)

ks = KripkeStructure(worlds, relations)

filename = 'saved_models/CluedoModel_a=' + str(len(agents)) + '_w=' + str(n_weapons) + '_p=' + str(n_people) + '_r=' + str(n_rooms) + '.pkl';

with open(filename, 'wb') as modelFile:
  pickle.dump(ks, modelFile);