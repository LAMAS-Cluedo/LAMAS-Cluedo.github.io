import sys

import pygame
from pygame.locals import *
import random

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
        self.agents = []
        self.ks = None
        self.target_cards = {}
        self.gameInProgress = False
        self.movesHistory = []
        self.trueWorld = CluedoWorld([])
        self.turn = -1

        for i, agent_name in enumerate(names_agents):
            agent = Player(agent_name, self, i >= (len(names_agents) - self.n_high_order))
            self.agents.append(agent)

        self.initializeLogicStructure(
            self.agents, 
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

        for agent in cycle(self.agents):
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


    # Function that creates all the zones needed for the game, based on coordinates
    def createZones(self) -> None:
        # Game progress/Actions taken zone
        self.zone_gameProgress = Rect(
            self.dim_img, 
            0, 
            self.dim_display - self.dim_img, 
            self.dim_img
        )
        
        # Zone for printing agents' knowledge
        self.zone_knowledge = Rect(
            0, 
            self.dim_img, 
            self.dim_display, 
            self.dim_display - self.dim_img - 100
        )
        
        # Zone for buttons
        self.zone_buttons = Rect(
            0, 
            self.dim_display - 100,
            self.dim_display,
            100
        )

        # Zone for "play" button
        self.zone_playButton = Rect(
            0, 
            self.dim_display - 100,
            self.dim_display/2,
            100
        )

        # Zone for "next" button
        self.zone_nextButton = Rect(
            self.dim_display/2, 
            self.dim_display - 100,
            self.dim_display/2,
            100
        )

        # Zone for when game enters game over state
        self.zone_gameOver = Rect(
            20,
            20,
            self.dim_display - 40,
            self.dim_display - 40
        )

        # Zone for "quit" button, in game over state
        self.zone_quitButton = Rect(
            self.zone_gameOver.x + self.zone_gameOver.w/2 - 40,
            self.zone_gameOver.y + self.zone_gameOver.h/2 - 20,
            80,
            40
        )


    # Following function draws intial game interface
    def drawInterface(self)-> None:
        self.game_theme_color = [165, 205, 210] # Light blue color
        self.color_edge = [100, 150, 150] # Darker blue color

        # Setting game color and adding the cluedo game image
        self.display.fill(self.game_theme_color)
        self.display.blit(self.game_img, (0, 0))

        # Delimiting each of the zones of the game (knowledge, actions and both buttons)
        pygame.draw.rect(self.display, self.color_edge, self.zone_knowledge, 2)
        pygame.draw.rect(self.display, self.color_edge, self.zone_gameProgress, 2)

        pygame.draw.rect(self.display, self.color_edge, self.zone_playButton, 2)
        pygame.draw.rect(self.display, self.color_edge, self.zone_nextButton, 2)

        # Setting the text for each button (play and next) whilst the game is in progress
        self.display.blit(
            self.font.render("Play", True, [0,0,0]), 
            ((self.zone_playButton.x + (self.zone_playButton.w/2) - 20), (self.zone_playButton.y + (self.zone_playButton.h/2) - 20))
        )
        self.display.blit(
            self.font.render("Next", True, [0,0,0]), 
            ((self.zone_nextButton.x + (self.zone_nextButton.w/2) - 20), (self.zone_nextButton.y + (self.zone_nextButton.h/2) - 20))
        )
    

    # Function that draws all actions taken during the game
    def drawActions(self):
        # Reseting the action zone to plain light blue
        self.display.fill(self.game_theme_color, self.zone_gameProgress)
        pygame.draw.rect(self.display, self.color_edge, self.zone_knowledge, 2)
        
        # The actions' history list is parsed backwards.
        # Therefore last action will be drawn first at the bottom of the actions zone, 
        # following actions will be drawn above it incrementally.
        # This way oldest actions will not be seen, whilst the newer ones will
        for i in range(len(self.movesHistory), 0, -1):
            self.display.blit(
                self.fontSmall.render(self.movesHistory[i-1], True, [0,0,0]), 
                ((self.zone_gameProgress.x + 10), (self.zone_gameProgress.y + self.zone_gameProgress.h - 20 - (len(self.movesHistory)-i)*25))
                )


    # The function that draws the knowledge for each turn
    def drawKnowledge(self):
        # Reseting the knowledge zone to plain light blue
        self.display.fill(self.game_theme_color, self.zone_knowledge)
        pygame.draw.rect(self.display, self.color_edge, self.zone_knowledge, 2)
        
        # Draw title for information on the right of the knowledge zone
        self.display.blit(
            self.fontSmall.render(
                'Knowledge cards not on table (first-order):',
                True, [0,0,0]), 
            ((self.zone_knowledge.w/2 +60), (self.zone_knowledge.y + 10))
            )
        
        # Draw all knowledge information from the top of the knowledge zone, incrementaly.
        # First it draws knowledge for the first agent, below it for the second and so on
        for i in range(len(self.agents)):
            # Specifying agent type 
            if self.agents[i].high_order:
                order_string = 'high'
            else:
                order_string = 'first'
            
            # Draw number of solutions still considered, on the left of knowledge zone, based on the agents type 
            self.display.blit(
                self.fontSmall.render(
                    'Agent "' + str(self.agents[i]) + '" (Using '+ order_string +' order knowledge) possible solutions: ' + str(len(self.getPossibleSolutions(self.agents[i]))),
                    True, [0,0,0]), 
                ((self.zone_knowledge.x +10), (self.zone_knowledge.y + 10 + i*25))
                )
            
            # Construct string with all first order knowledge of each agent, from their knowledge base 
            for_print = ''
            for card in self.agents[i].knowledge_base:
                if card not in for_print:
                    for_print += (card + ', ')
            
            # Draw first order knowledge of each agent, on the right of the knowledge zone
            self.display.blit(
                self.fontSmall.render(
                    str(self.agents[i]) + ': ' + for_print[:-1],
                    True, [0,0,0]), 
                ((self.zone_knowledge.w/2 + 60), (self.zone_knowledge.y + 10 + (i+1)*25))
                )

        # Draw the correct world (the cards on the table) at the botttom of the knowledge zone
        self.display.blit(
            self.fontSmall.render(
                'Correct world: ' + self.trueWorld.noTurnAtoms(),
                True, [0,0,0]), 
            ((self.zone_knowledge.x +10), (self.zone_knowledge.y - 25 + self.zone_knowledge.h))
            )


    # Following function draws entire game over screen
    def drawGameOver(self, winning_agent: str, weapon: str, person: str, room: str):
        # Reset entire screen back to light blue
        self.display.fill(self.game_theme_color)
        # Draw rectangle for game over zone, in darker blue
        pygame.draw.rect(self.display, self.color_edge, self.zone_gameOver, 10)

        # Draws game over message at top of the zone
        self.display.blit(
            self.font.render(
                'Game Ended',
                True, [0,0,0]), 
            ((self.zone_gameOver.x + self.zone_gameOver.w/2 - 80), (self.zone_gameOver.y + 30))
            )

        # Draws the actual cards which were on the table, below the game over message
        self.display.blit(
            self.fontSmall.render(
                'Cards on Table: w' + 
                str(self.target_cards['weapon']) + ' p' + 
                str(self.target_cards['person'])+ ' r' +
                str(self.target_cards['room']),
                True, [0,0,0]), 
            ((self.zone_gameOver.x +self.zone_gameOver.w/2 - 70), (self.zone_gameOver.y + 80))
            )

        # Draws what cards did the winning agent choose (most likely the same as the cards on the table)
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

        # Draws the 'quit' button
        pygame.draw.rect(self.display, self.color_edge, self.zone_quitButton, 2)
        self.display.blit(
            self.font.render(
                'Quit',
                True, [0,0,0]), 
            ((self.zone_quitButton.x + 10), (self.zone_quitButton.y + 8))
            )

    # Function that intializes the game screen
    def initializeDisplay(self):
        # Mouse is reseted and visible
        pygame.mouse.set_visible
        self.mouse = {'click': -1, 'coordinates': (0,0)}

        # Set cluedo game image dimensions and loading the image
        self.dim_img = 360
        self.game_img = pygame.transform.scale(
            pygame.image.load('./img/cluedoBoard.jpeg'),
            (self.dim_img, self.dim_img)
            )
        
        # Set dimensions for display and create the display
        self.dim_display = 720
        self.display = pygame.display.set_mode((self.dim_display, self.dim_display))
        pygame.display.set_caption('Cluedo')

        # Create all interaction zones and draw the interface
        self.createZones()
        self.drawInterface()

    # Function to update the model when an agent says they have none of the cards in a question
    def agentSaysNo(self, agent: str, question: Question) -> None:
        for world in tqdm(self.ks.worlds):
            keys = world.assignment.keys()
            if (str(AgentCard('w', question.weapon, agent)) in keys or 
                    str(AgentCard('p', question.person, agent)) in keys or
                    str(AgentCard('r', question.room, agent)) in keys):
                self.ks.remove_node_by_name(world.name) # World removed when agent has any of the questioned cards

    # Function to check if an agent would still consider a given world possible after being shown a card 
    def agentShownPossibleWorld(self, agent: str, shownAtom: str, possibleWorld: str):
        for possAtom in possibleWorld.split():
            if possAtom[:-2] != agent and possAtom[-2:] == shownAtom:
                return False
        return True

    # Function to update the model when an agent shows a card to another agent
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
            
            if len(cardsToShow) == 0: # Agent has none of the given cards so the world is removed
                self.ks.remove_node_by_name(world.name)
                
            elif len(cardsToShow) == 1: # Agent has one of the cards so relations are updated for that card
                newRelation = []
                cardToShow = cardsToShow[0]
                for (worldFrom, worldTo) in self.ks.relations[question.agent]:
                    if worldFrom != world.name or self.agentShownPossibleWorld(agent, cardToShow, worldTo):
                        newRelation.append((worldFrom, worldTo))
                self.ks.relations[question.agent] = newRelation
            
            else: # Agent has multiple cards they could show so multiple worlds are created for each possibility
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

    # Get the possible combinations of solution cards an agent considers possible
    def getPossibleSolutions(self, agent: Player) -> set:
        worlds = set([])

        if agent.high_order: # If agent is high order their possibilites are found in the kripke structure
            for (worldFrom, worldTo) in self.ks.relations[str(agent)]:
                if worldFrom == str(self.trueWorld):
                    worlds.add((worldTo[:8]))
            return worlds

        # If an agent is first order their possibilities are found from their simple knowledge base of cards they've seen
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

    # Function used for removing an agent if the agent has guessed the wrong cards on the table
    def removeAgent(self, remove_agent: str):
        for agent in self.agents:
            if str(agent) == remove_agent:
                self.agents.remove(agent)


    # Function that checks to see whether an agent has guessed the correct cards on the table or the wrong ones
    # If the guessed cards are correct agent wins and game over screen appears.
    # If guess is wrong agent loses and it is removed.
    def checkGameOver(self, agent: str, weapon: str, person: str, room: str):
        # Adding guess/accuse message to the action history (to be printed later)
        self.movesHistory.append('Agent ' + agent + ' acuses cards: ' + weapon + ' ' + person + ' ' + room)
        
        # If cards guessed/accused are the same as those on the table (target cards) agent wins
        if weapon == 'w' + str(self.target_cards['weapon']) and \
             person == 'p' + str(self.target_cards['person']) and \
                 room == 'r' + str(self.target_cards['room']):
                 # Enter game over state
                 self.gameInProgress = -1
                 self.drawGameOver(agent, weapon, person, room)
        
        # If the guessed cards are wrong agent looses and it is removed
        else:
            self.movesHistory.append('Agent ' + agent + ' is wrong and removed')
            self.removeAgent(agent)

    # Checks if a click has occured in a certain zone
    def checkZone(self, zone: Rect) -> bool:
        if (self.mouse['click'] == 1) and \
            (
                (zone.x <= self.mouse['coordinates'][0] <= zone.x + zone.w) and \
                (zone.y <= self.mouse['coordinates'][1] <= zone.y + zone.h)
            ):
            return True
        else:
            return False

    # Checks if a click occurs in one of the button zones and performs actions based on the button
    def clickCheck(self) -> bool:
        # If a click occurs in the 'quit' button zone and the game is in game over state the game quits
        if self.checkZone(self.zone_quitButton) and self.gameInProgress == -1:
            pygame.quit()
            sys.exit()

        # If a click occurs in the 'play' button zone the game will start 
        # (initial knowledge of the agents will be drawn and allows the use of the 'next' button)
        # Also returns that a button has been clicked
        if self.checkZone(self.zone_playButton) and self.gameInProgress == 0:
            self.gameInProgress = 1
            print('The Game starts now!')
            self.movesHistory.append('Game Initialized')
            self.movesHistory.append('Cards dealt')
            return True
        
        # If a click occurs in the 'next' button zone and the game started (is in progress)
        # it will return that the button has been clicked
        if self.checkZone(self.zone_nextButton) and self.gameInProgress == 1:
            print('Next move!')
            return True

    # Checks all interface events that happen
    def checkInterfaceAction(self, interface_actions):
        for action in interface_actions:
            # If default 'quit' button (x button on top corner right) is pressed the game ends
            if action.type == QUIT:
                pygame.quit()
                sys.exit()
            
            # For all other events the coordinates of the mouse pointer are taken
            else:
                try:
                    self.mouse['coordinates'] = action.dict['pos']
                except:
                    self.mouse['coordinates'] = (0,0)
                # If the left mouse button is pressed the model's mouse variable is set to 1 which signals a click 
                if action.type == MOUSEBUTTONDOWN:
                    if action.dict['button'] == 1:
                        self.mouse['click'] = 1
