import enum
import sys
from turtle import st
from matplotlib.pyplot import streamplot

import pygame
from pygame.locals import *
import random

from mesa import Model
from mesa.time import RandomActivation
from tqdm import tqdm
from models.agent_model import Player

from tqdm import tqdm
from itertools import cycle
from models.cluedo import AgentCard, AgentShownChoice, Question

from models.logic_model import initializeKripke
from models.mlsolver.kripke import KripkeStructure, World
from models.mlsolver.formula import *


class CluedoGameModel(Model):

    def __init__(self: Model, names_agents: list[str], n_weapons: int, n_people: int, n_rooms: int) -> Model:
        pygame.init()
        self.n_weapons = n_weapons
        self.n_people = n_people
        self.n_rooms = n_rooms
        self.schedule = RandomActivation(self)
        self.ks = None
        self.target_cards = {}
        self.gameInProgress = False
        self.movesHistory = []
        self.turn = -1
        
        for agent_name in names_agents:
            agent = Player(agent_name, self)
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


    def setCardsOnTable(self: Model, weapon: int, person: int, room: int) -> None:
        if self.target_cards:
            print("Cards already set")
        else:    
            self.target_cards['weapon'] = weapon
            self.target_cards['person'] = person
            self.target_cards['room'] = room

    def dealCards(self: Model, n_weapons: int, n_people: int, n_rooms: int) -> None:
        weapons = list(range(0, self.n_weapons))
        people = list(range(0, self.n_people))
        rooms = list(range(0, self.n_rooms))
        weapon = random.choice(weapons)
        person = random.choice(people)
        room = random.choice(rooms)
        self.setCardsOnTable(weapon, person, room)
        weapons.remove(weapon)
        people.remove(person)
        rooms.remove(room)

        for agent in cycle(self.schedule.agents):
            if weapons:
                weapon = random.choice(weapons)
                agent.setAtributes(weapon=weapon)
                weapons.remove(weapon)
            elif people:
                person = random.choice(people)
                agent.setAtributes(person=person)
                people.remove(person)
            elif rooms:
                room = random.choice(rooms)
                agent.setAtributes(room=room)
                rooms.remove(room)
            else:
                break


    def initializeLogicStructure(self: Model, names_agents: list[str], n_weapons: int, n_people: int, n_rooms: int) -> KripkeStructure:
        self.ks = initializeKripke(
            agents=names_agents, 
            n_weapons=n_weapons, 
            n_people=n_people, 
            n_rooms=n_rooms
            )

    def createZones(self: Model) -> None:
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
        self.zone_gameOver = Rect(
            20,
            20,
            self.dim_display - 40,
            self.dim_display - 40
        )
        self.zone_quitButton = Rect(
            self.zone_gameOver.x + self.zone_gameOver.w/2 - 40,
            self.zone_gameOver.y + self.zone_gameOver.h/2 - 20,
            80,
            40
        )


    def drawInterface(self: Model)-> None:
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
    
    def drawActions(self: Model):
        self.display.fill(self.game_theme_color, self.zone_gameProgress)
        pygame.draw.rect(self.display, self.color_edge, self.zone_knowledge, 2)
        for i in range(len(self.movesHistory), 0, -1):
            self.display.blit(
                self.fontSmall.render(self.movesHistory[i-1], True, [0,0,0]), 
                ((self.zone_gameProgress.x + 10), (self.zone_gameProgress.y + self.zone_gameProgress.h - 20 - (len(self.movesHistory)-i)*25))
                )

    def drawKnowledge(self: Model):
        self.display.fill(self.game_theme_color, self.zone_knowledge)
        pygame.draw.rect(self.display, self.color_edge, self.zone_knowledge, 2)
        self.display.blit(
            self.fontSmall.render(
                'Knowledge cards not on table:',
                True, [0,0,0]), 
            ((self.zone_knowledge.w/2 +10), (self.zone_knowledge.y + 10))
            )
        for i in range(len(self.schedule.agents)):
            self.display.blit(
                self.fontSmall.render(
                    'Agent "' + str(self.schedule.agents[i]) + '" worlds: ' + str(len(self.ks.worlds)),
                    True, [0,0,0]), 
                ((self.zone_knowledge.x +10), (self.zone_knowledge.y + 10 + i*25))
                )
            self.display.blit(
                self.fontSmall.render(
                    str(self.schedule.agents[i]) + ': ' + 'Function for ' + str(len(self.ks.relations[str(self.schedule.agents[i])])) + ' relations',
                    True, [0,0,0]), 
                ((self.zone_knowledge.x + 175), (self.zone_knowledge.y + 10 + i*25))
                )
            for_print = ''
            for card in self.schedule.agents[i].knowledge_base:
                if card not in for_print:
                    for_print += (card + ', ')
            self.display.blit(
                self.fontSmall.render(
                    str(self.schedule.agents[i]) + ': ' + for_print[:-1],
                    True, [0,0,0]), 
                ((self.zone_knowledge.w/2 + 10), (self.zone_knowledge.y + 10 + (i+1)*25))
                )

    def drawGameOver(self: Model, winning_agent: str, weapon: str, person: str, room: str):
        self.display.fill(self.game_theme_color)
        pygame.draw.rect(self.display, self.color_edge, self.zone_gameOver, 10)
        self.display.blit(
            self.font.render(
                'Game Ended',
                True, [0,0,0]), 
            ((self.zone_gameOver.x + self.zone_gameOver.w/2 - 80), (self.zone_gameOver.y + 30))
            )
        self.display.blit(
            self.fontSmall.render(
                'Cards on Table: w' + 
                str(self.target_cards['weapon']) + ' p' + 
                str(self.target_cards['person'])+ ' r' +
                str(self.target_cards['room']),
                True, [0,0,0]), 
            ((self.zone_gameOver.x +self.zone_gameOver.w/2 - 70), (self.zone_gameOver.y + 80))
            )

        self.display.blit(
            self.fontSmall.render(
                'Agent ' + str(winning_agent) + 
                ' chose the following cards: ' + 
                weapon + ' ' + 
                person + ' ' +
                room,
                True, [0,0,0]), 
            ((self.zone_gameOver.x +self.zone_gameOver.w/2 - 125), (self.zone_gameOver.y + 120))
            )

        pygame.draw.rect(self.display, self.color_edge, self.zone_quitButton, 2)
        self.display.blit(
            self.font.render(
                'Quit',
                True, [0,0,0]), 
            ((self.zone_quitButton.x + 10), (self.zone_quitButton.y + 8))
            )
            


    def initializeDisplay(self: Model):
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

    def agentSaysNo(self: Model, agent: str, question: Question) -> None:
        for world in tqdm(self.ks.worlds):
            keys = world.assignment.keys()
            if (str(AgentCard('w', question.weapon, agent)) in keys or 
                    str(AgentCard('p', question.person, agent)) in keys or
                    str(AgentCard('r', question.room, agent)) in keys):
                self.ks.remove_node_by_name(world.name)

    def agentShownPossibleWorld(self: Model, agent: str, shownAtom: str, possibleWorld: str):
        for possAtom in possibleWorld.split():
            if possAtom[:-2] != agent and possAtom[-2:] == shownAtom:
                return False
        return True

    def notConflictingShownCard(self: Model, worldFrom: str, worldTo: str, turn: int):
        for atom in worldFrom.split():
            if atom[5:] == str(turn):
                for atom2 in worldTo.split():
                    if atom2[5:] == str(turn) and atom2[1:2] != atom[1:2]:
                        return False
        return True

    def agentResponds(self: Model, agent: str, question: Question, turn: int) -> None:
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

                # newRelation = {}
                # for oneAgent in agents:
                #     newRelation[oneAgent] = []
                #     for (worldFrom, worldTo) in self.ks.relations[oneAgent]:
                #         if self.notConflictingShownCard(worldFrom, worldTo, turn):
                #             newRelation[oneAgent].append((worldFrom, worldTo))
                # self.ks.relations = newRelation

    def removeAgent(self: Model, remove_agent: str):
        for agent in self.schedule.agents:
            if str(agent) == remove_agent:
                self.schedule.agents.remove(agent)
                for a1 in self.schedule.agents:
                    print(str(a1))

    def checkGameOver(self: Model, agent: str, weapon: str, person: str, room: str):
        self.movesHistory.append('Agent ' + agent + ' acuses cards: ' + weapon + ' ' + person + ' ' + room)
        if weapon == 'w' + str(self.target_cards['weapon']) and \
             person == 'p' + str(self.target_cards['person']) and \
                 room == 'r' + str(self.target_cards['room']):
                 self.gameInProgress = -1
                 self.drawGameOver(agent, weapon, person, room)
        else:
            self.movesHistory.append('Agent ' + agent + ' is wrong and removed')
            self.removeAgent(agent)

    def checkZone(self: Model, zone: Rect) -> bool:
        if (self.mouse['click'] == 1) and \
            (
                (zone.x <= self.mouse['coordinates'][0] <= zone.x + zone.w) and \
                (zone.y <= self.mouse['coordinates'][1] <= zone.y + zone.h)
            ):
            return True
        else:
            return False

    def clickCheck(self: Model) -> bool:
        if self.checkZone(self.zone_quitButton) and self.gameInProgress == -1:
            pygame.quit()
            sys.exit()
        if self.checkZone(self.zone_playButton) and self.gameInProgress == 0:
            self.gameInProgress = 1
            print('The Game starts now!')
            self.movesHistory.append('Game Initialized')
            self.movesHistory.append('Cards dealt')
            return True
        if self.checkZone(self.zone_nextButton) and self.gameInProgress == 1:
            print('Next move!')
            return True


    def checkInterfaceAction(self: Model, interface_actions):
        for action in interface_actions:
            if action.type == QUIT:
                pygame.quit()
                sys.exit()
            else:
                try:
                    self.mouse['coordinates'] = action.dict['pos']
                except:
                    self.mouse['coordinates'] = (0,0)
                if action.type == MOUSEBUTTONDOWN:
                    if action.dict['button'] == 1:
                        self.mouse['click'] = 1
