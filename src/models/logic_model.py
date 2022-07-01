import pickle
from os import listdir
from bisect import insort
from tqdm import tqdm
from models.mlsolver.kripke import *
from models.mlsolver.formula import *
from models.cluedo import *

def buildWorlds(weapons, people, rooms, agents, type, nextAgent, dealt):
  """
  Recursive function to generate all possible worlds based on all orders the cards can be
  dealt out
  """

  if 0 == len(weapons) + len(people) + len(rooms): # All cards have been dealt
    assignment = {}
    for i_atom in range(0, len(dealt)):
      assignment[str(dealt[i_atom])] = True
    world = World(str(CluedoWorld(dealt)), assignment)
    return [world]

  worlds = []

  if type == 'w': 

    if nextAgent < 0: # Dealing weapon to middle
      for weapon in weapons:
        weapons.remove(weapon)
        dealt.append(SolAtom('w', weapon))
        worlds += buildWorlds(weapons, people, rooms, agents, 'p', -1, dealt)
        insort(weapons, weapon)
        dealt.pop()
      return worlds

    else: # Dealing weapons to players
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

    if nextAgent < 0: # Dealing person to middle
      for person in people:
        people.remove(person)
        dealt.append(SolAtom('p', person))
        worlds += buildWorlds(weapons, people, rooms, agents, 'r', -1, dealt)
        insort(people, person)
        dealt.pop()
      return worlds

    else: # Dealing people to players
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

    if nextAgent < 0: # Dealing room to middle
      for room in rooms:
        rooms.remove(room)
        dealt.append(SolAtom('r', room))
        worlds += buildWorlds(weapons, people, rooms, agents, 'w', 0, dealt)
        insort(rooms, room)
        dealt.pop()
      return worlds

    else: # Dealing rooms to players
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

# Check if, given a certain world, a given agent would consider another world possible
def isPossWorld(world, possWorld, agent):
  for atom in world.assignment.keys():
    if atom[:-2] == agent.unique_id: # Only check using this agent's cards
      possAtoms = possWorld.assignment.keys()
      if atom not in possAtoms: # If the agent does not have the same card in the other world then not possible
        return False
      for possAtom in possAtoms:
        if possAtom[:-2] != agent.unique_id and possAtom[-2:] == atom[-2:]:
          return False
  return True

# Generate all accessibility relations from a given world for a given agent
def buildRelationsFromWorld(world, worlds, agent):
  return [(world.name, possWorld.name) for possWorld in worlds if isPossWorld(world, possWorld, agent)]

# Load an existing initial kripke structure from a file
def loadStructure(ks_name):
  print("~~~\nLoading " + ks_name + '\n~~~')

  with open('src/models/saved_models/' + ks_name, 'rb') as modelFile:
    kripke_structure = pickle.load(modelFile)
  return kripke_structure

# Save an inital kripke structure to a file
def saveStructure(kripke_structure, ks_name):
  print('~~~\nSaving Kripke Structure with name: ' + ks_name + '\n~~~')

  filename = 'src/models/saved_models/' + ks_name
  with open(filename, 'wb') as modelFile:
    pickle.dump(kripke_structure, modelFile)

# Initialise the kripke structure at the start of a game of Cluedo (after the cards are dealt).
# Will use a file if one exists and will otherwise generate the structure and save it to a file
def initializeKripke(agents = listAgents(3), n_weapons=3, n_people=3, n_rooms=3):
  ks_name ='CluedoModel_a=' + str(len(agents)) + '_w=' + str(n_weapons) + '_p=' + str(n_people) + '_r=' + str(n_rooms) + '.pkl'

  for model in listdir('src/models/saved_models/'):
    if model == ks_name:
      return loadStructure(ks_name)

  weapons = list(range(0, n_weapons))
  people = list(range(0, n_people))
  rooms = list(range(0, n_rooms))

  worlds = buildWorlds(weapons, people, rooms, agents, 'w', -1, [])

  relations = {}
  for agent in tqdm(agents):
    relations[agent.unique_id] = []
    for world in tqdm(worlds):
      relations[agent.unique_id] += buildRelationsFromWorld(world, worlds, agent)

  kripke_structure = KripkeStructure(worlds, relations)
  saveStructure(kripke_structure, ks_name)
  
  return kripke_structure
