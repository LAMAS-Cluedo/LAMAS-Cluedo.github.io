import pygame
from pygame.locals import Rect
import random

from mesa import Model
from mesa.time import RandomActivation
from models.agent_model import Player

from itertools import cycle

from models.logic_model import initializeKripke
from models.mlsolver.kripke import KripkeStructure


class CluedoGameModel(Model):

    def __init__(self: Model, names_agents: list[str], n_weapons: int, n_people: int, n_rooms: int) -> Model:
        pygame.init()
        self.schedule = RandomActivation(self)
        self.ks = []
        self.target_cards = {}
        self.font = pygame.font.SysFont(None, 40)
        
        for agent_name in names_agents:
            agent = Player(agent_name, self)
            self.schedule.add(agent)

        self.initializeLogicStructure(
            self.schedule.agents, 
            n_weapons, 
            n_people, 
            n_rooms
            )
        self.initializeDisplay()

        
    

    def setCardsOnTable(self: Model, weapon: int, person: int, room: int) -> None:
        if self.target_cards:
            print("Cards already set")
        else:    
            self.target_cards['weapon'] = weapon
            self.target_cards['person'] = person
            self.target_cards['room'] = room

    def dealCards(self: Model, n_weapons: int, n_people: int, n_rooms: int) -> None:
        weapons = list(range(0, n_weapons))
        people = list(range(0, n_people))
        rooms = list(range(0, n_rooms))
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
        self.zone_knowledge = Rect(
            self.dim_img, 
            0, 
            self.dim_display - self.dim_img, 
            self.dim_img
        )
        self.zone_gameProgress = Rect(
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


    def drawInterface(self: Model)-> None:
        game_theme_color = [165, 205, 210]
        color_edge = [100, 150, 150]

        self.display.fill(game_theme_color)
        self.display.blit(self.game_img, (0, 0))

        pygame.draw.rect(self.display, color_edge, self.zone_knowledge, 2)
        pygame.draw.rect(self.display, color_edge, self.zone_gameProgress, 2)

        pygame.draw.rect(self.display, color_edge, self.zone_playButton, 2)
        pygame.draw.rect(self.display, color_edge, self.zone_nextButton, 2)

        self.display.blit(
            self.font.render("Play", True, [0,0,0]), 
            ((self.zone_playButton.x + (self.zone_playButton.w/2) - 20), (self.zone_playButton.y + (self.zone_playButton.h/2) - 20))
        )
        self.display.blit(
            self.font.render("Next", True, [0,0,0]), 
            ((self.zone_nextButton.x + (self.zone_nextButton.w/2) - 20), (self.zone_nextButton.y + (self.zone_nextButton.h/2) - 20))
        )

    def initializeDisplay(self: Model):
        pygame.mouse.set_visible
        self.mouse = {'l_down': -1, 'l_up': -1, 'pos': (0,0)}

        self.dim_img = 300
        self.game_img = pygame.transform.scale(
            pygame.image.load('./img/cluedoBoard.jpeg'),
            (self.dim_img, self.dim_img)
            )
        
        self.dim_display = 720
        self.display = pygame.display.set_mode((self.dim_display, self.dim_display))
        pygame.display.set_caption('Cluedo')

        self.createZones()
        self.drawInterface()