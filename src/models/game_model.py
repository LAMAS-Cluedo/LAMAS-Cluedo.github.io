from ast import Mod
import enum
import sys
from turtle import st
from matplotlib.pyplot import streamplot

import pygame
from pygame.locals import *
import random

from mesa.time import RandomActivation
from tqdm import tqdm
from models.agent_model import Player

from tqdm import tqdm
from itertools import cycle
from models.cluedo import *

from models.logic_model import initializeKripke
from models.mlsolver.kripke import KripkeStructure, World
from models.mlsolver.formula import *


class CluedoGameModel():

    def __init__(self, names_agents: list[str], n_weapons: int, n_people: int, n_rooms: int, n_high_order: int):
        pygame.init()
        self.n_weapons = n_weapons
        self.n_people = n_people
        self.n_rooms = n_rooms
        self.n_high_order = n_high_order
        self.schedule = RandomActivation(self)
        self.ks = None
        self.target_cards = {}
        self.gameInProgress = False
        self.movesHistory = []
        self.trueWorld = CluedoWorld([])
        self.turn = -1
        
        for i, agent_name in enumerate(names_agents):
            agent = Player(agent_name, i >= (len(names_agents) - self.n_high_order))
            self.schedule.add(agent)

        self.initializeLogicStructure(
            self.schedule.agents, 
            n_weapons, 
            n_people, 
            n_rooms
            )
        self.font = pygame.font.SysFont(None, 40)
        self.fontSmall = pygame.font.SysFont(None, 20)
        self.initializeDisplay()
        super()


    def setCardsOnTable(self, weapon: int, person: int, room: int) -> None:
        if self.target_cards:
            print("Cards already set")
        else:    
            self.target_cards['weapon'] = weapon
            self.target_cards['person'] = person
            self.target_cards['room'] = room

    def dealCards(self, n_weapons: int, n_people: int, n_rooms: int) -> None:
        weapons = list(range(0, self.n_weapons))
        people = list(range(0, self.n_people))
        rooms = list(range(0, self.n_rooms))
        weapon = random.choice(weapons)
        self.trueWorld.atoms.append(SolAtom('w', weapon))
        person = random.choice(people)
        self.trueWorld.atoms.append(SolAtom('p', person))
        room = random.choice(rooms)
        self.trueWorld.atoms.append(SolAtom('r', room))
        self.setCardsOnTable(weapon, person, room)
        weapons.remove(weapon)
        people.remove(person)
        rooms.remove(room)

        for agent in cycle(self.schedule.agents):
            if weapons:
                weapon = random.choice(weapons)
                agent.setAtributes(weapon=weapon)
                self.trueWorld.atoms.append(AgentCard('w', weapon, str(agent)))
                weapons.remove(weapon)
            elif people:
                person = random.choice(people)
                agent.setAtributes(person=person)
                self.trueWorld.atoms.append(AgentCard('p', person, str(agent)))
                people.remove(person)
            elif rooms:
                room = random.choice(rooms)
                agent.setAtributes(room=room)
                self.trueWorld.atoms.append(AgentCard('r', room, str(agent)))
                rooms.remove(room)
            else:
                break


    def initializeLogicStructure(self, names_agents: list[str], n_weapons: int, n_people: int, n_rooms: int) -> KripkeStructure:
        self.ks = initializeKripke(
            agents=names_agents, 
            n_weapons=n_weapons, 
            n_people=n_people, 
            n_rooms=n_rooms
            )

    def createZones(self) -> None:
        self.zone_gameProgress = Rect(
            self.dim_img, 
            0, 
            self.dim_display - self.dim_img, 
            self.dim_img
        )
        self.zone_knowledge = Rect(
            0, 
            self.dim_img, 
            self.dim_display, 
            self.dim_display - self.dim_img - 100
        )
        self.zone_buttons = Rect(
            0, 
            self.dim_display - 100,
            self.dim_display,
            100
        )
        self.zone_playButton = Rect(
            0, 
            self.dim_display - 100,
            self.dim_display/2,
            100
        )
        self.zone_nextButton = Rect(
            self.dim_display/2, 
            self.dim_display - 100,
            self.dim_display/2,
            100
        )


    def drawInterface(self)-> None:
        self.game_theme_color = [165, 205, 210]
        self.color_edge = [100, 150, 150]

        self.display.fill(self.game_theme_color)
        self.display.blit(self.game_img, (0, 0))

        pygame.draw.rect(self.display, self.color_edge, self.zone_knowledge, 2)
        pygame.draw.rect(self.display, self.color_edge, self.zone_gameProgress, 2)

        pygame.draw.rect(self.display, self.color_edge, self.zone_playButton, 2)
        pygame.draw.rect(self.display, self.color_edge, self.zone_nextButton, 2)

        self.display.blit(
            self.font.render("Play", True, [0,0,0]), 
            ((self.zone_playButton.x + (self.zone_playButton.w/2) - 20), (self.zone_playButton.y + (self.zone_playButton.h/2) - 20))
        )
        self.display.blit(
            self.font.render("Next", True, [0,0,0]), 
            ((self.zone_nextButton.x + (self.zone_nextButton.w/2) - 20), (self.zone_nextButton.y + (self.zone_nextButton.h/2) - 20))
        )
    
    def drawActions(self):
        self.display.fill(self.game_theme_color, self.zone_gameProgress)
        pygame.draw.rect(self.display, self.color_edge, self.zone_knowledge, 2)
        for i in range(len(self.movesHistory), 0, -1):
            self.display.blit(
                self.fontSmall.render(self.movesHistory[i-1], True, [0,0,0]), 
                ((self.zone_gameProgress.x + 10), (self.zone_gameProgress.y + self.zone_gameProgress.h - 20 - (len(self.movesHistory)-i)*25))
                )

    def drawKnowledge(self):
        self.display.fill(self.game_theme_color, self.zone_knowledge)
        pygame.draw.rect(self.display, self.color_edge, self.zone_knowledge, 2)
        self.display.blit(
            self.fontSmall.render(
                'Knowledge cards not on table:',
                True, [0,0,0]), 
            ((self.zone_knowledge.w/2 +60), (self.zone_knowledge.y + 10))
            )
        for i in range(len(self.schedule.agents)):
            if self.schedule.agents[i].high_order:
                order_string = 'high'
            else:
                order_string = 'first'
            self.display.blit(
                self.fontSmall.render(
                    'Agent "' + str(self.schedule.agents[i]) + '" (Using '+ order_string +' order knowledge) possible solutions: ' + str(len(self.getPossibleSolutions(self.schedule.agents[i]))),
                    True, [0,0,0]), 
                ((self.zone_knowledge.x +10), (self.zone_knowledge.y + 10 + i*25))
                )
            for_print = ''
            for card in self.schedule.agents[i].knowledge_base:
                if card not in for_print:
                    for_print += (card + ', ')
            self.display.blit(
                self.fontSmall.render(
                    str(self.schedule.agents[i]) + ': ' + for_print[:-1],
                    True, [0,0,0]), 
                ((self.zone_knowledge.w/2 + 60), (self.zone_knowledge.y + 10 + (i+1)*25))
                )
        self.display.blit(
            self.fontSmall.render(
                'Correct world: ' + self.trueWorld.noTurnAtoms(),
                True, [0,0,0]), 
            ((self.zone_knowledge.x +10), (self.zone_knowledge.y - 25 + self.zone_knowledge.h))
            )

    def initializeDisplay(self):
        pygame.mouse.set_visible
        self.mouse = {'click': -1, 'coordinates': (0,0)}

        self.dim_img = 360
        self.game_img = pygame.transform.scale(
            pygame.image.load('./img/cluedoBoard.jpeg'),
            (self.dim_img, self.dim_img)
            )
        
        self.dim_display = 720
        self.display = pygame.display.set_mode((self.dim_display, self.dim_display))
        pygame.display.set_caption('Cluedo')

        self.createZones()
        self.drawInterface()

    def agentSaysNo(self, agent: str, question: Question) -> None:
        for world in tqdm(self.ks.worlds):
            keys = world.assignment.keys()
            if (str(AgentCard('w', question.weapon, agent)) in keys or 
                    str(AgentCard('p', question.person, agent)) in keys or
                    str(AgentCard('r', question.room, agent)) in keys):
                self.ks.remove_node_by_name(world.name)

    def agentShownPossibleWorld(self, agent: str, shownAtom: str, possibleWorld: str):
        for possAtom in possibleWorld.split():
            if possAtom[:-2] != agent and possAtom[-2:] == shownAtom:
                return False
        return True

    def notConflictingShownCard(self, worldFrom: str, worldTo: str, turn: int):
        for atom in worldFrom.split():
            if atom[5:] == str(turn):
                for atom2 in worldTo.split():
                    if atom2[5:] == str(turn) and atom2[1:2] != atom[1:2]:
                        return False
        return True

    def agentResponds(self, agent: str, question: Question, turn: int) -> None:
        agents = self.ks.relations.keys()
        
        for world in tqdm(self.ks.worlds.copy()):
            cardsToShow = []
            atoms = world.assignment.keys()
            for atom in atoms:
                if atom == agent + question.wAtom():
                    cardsToShow.append(question.wAtom())
                if atom == agent + question.pAtom():
                    cardsToShow.append(question.pAtom())
                if atom == agent + question.rAtom():
                    cardsToShow.append(question.rAtom())
            
            if len(cardsToShow) == 0:
                self.ks.remove_node_by_name(world.name)
                
            elif len(cardsToShow) == 1:
                newRelation = []
                cardToShow = cardsToShow[0]
                for (worldFrom, worldTo) in self.ks.relations[question.agent]:
                    if worldFrom != world.name or self.agentShownPossibleWorld(agent, cardToShow, worldTo):
                        newRelation.append((worldFrom, worldTo))
                self.ks.relations[question.agent] = newRelation
            
            else:
                newWorlds = []
                self.ks.worlds.remove(world)
                for i, cardToShow in enumerate(cardsToShow):
                    newWorlds.append(World(world.name, world.assignment))
                    newAtom = agent + cardToShow + '_t' + str(turn)
                    newWorlds[i].name = newWorlds[i].name + ' ' + newAtom
                    newWorlds[i].assignment[newAtom] = True
                    self.ks.worlds.append(newWorlds[i])
                newRelation = {}
                for oneAgent in agents:
                    newRelation[oneAgent] = []
                    if question.agent != oneAgent and agent != oneAgent:
                        for worldFrom in newWorlds:
                            newRelation[oneAgent] = [(worldFrom.name, worldTo.name) for worldTo in newWorlds]

                    for (worldFrom, worldTo) in self.ks.relations[oneAgent]:
                        if worldFrom == world.name:
                            for i, cardToShow in enumerate(cardsToShow):
                                if question.agent != oneAgent or self.agentShownPossibleWorld(agent, cardToShow, worldTo):
                                    newRelation[oneAgent].append((newWorlds[i].name, worldTo))
                        elif worldTo == world.name:
                            newRelation[oneAgent].append((worldFrom, newWorlds[i].name))
                        else:
                            newRelation[oneAgent].append((worldFrom, worldTo))
                
                self.ks.relations = newRelation

    def getPossibleSolutions(self, agent: Player) -> set:
        worlds = set([])

        if agent.high_order:
            for (worldFrom, worldTo) in self.ks.relations[str(agent)]:
                if worldFrom == str(self.trueWorld):
                    worlds.add((worldTo[:8]))
            return worlds

        weapons = list(range(0, self.n_weapons))
        people = list(range(0, self.n_people))
        rooms = list(range(0, self.n_rooms))
        for atom in agent.knowledge_base:
            if atom[0] == 'w':
                weapons.remove(int(atom[1]))
            if atom[0] == 'p':
                people.remove(int(atom[1]))
            if atom[0] == 'r':
                rooms.remove(int(atom[1]))

        for weapon in weapons:
            for person in people:
                for room in rooms:
                    worlds.add(str(CluedoWorld(['w'+str(weapon), 'p'+str(person), 'r'+str(room)])))
        
        return worlds

    def checkZone(self, zone: Rect) -> bool:
        if (self.mouse['click'] == 1) and \
            (
                (zone.x <= self.mouse['coordinates'][0] <= zone.x + zone.w) and \
                (zone.y <= self.mouse['coordinates'][1] <= zone.y + zone.h)
            ):
            return True
        else:
            return False

    def clickCheck(self) -> bool:
        if self.checkZone(self.zone_playButton) and not self.gameInProgress:
            self.gameInProgress = True
            print('The Game starts now!')
            self.movesHistory.append('Game Initialized')
            self.movesHistory.append('Cards dealt')
            return True
        if self.checkZone(self.zone_nextButton) and self.gameInProgress:
            print('Next move!')
            return True


# TODO: change this function
    def parse_events(self, event_handle):
        # Handle input events
        for event in event_handle:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            else:
                try:
                    self.mouse['coordinates'] = event.dict['pos']
                except:
                    self.mouse['coordinates'] = (0,0)
                if event.type == MOUSEBUTTONDOWN:
                    if event.dict['button'] == 1:
                        self.mouse['click'] = 1
