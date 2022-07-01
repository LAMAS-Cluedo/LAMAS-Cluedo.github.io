import random

import pygame
from models.agent_model import Player

from models.game_model import CluedoGameModel
from models.mlsolver.kripke import *
from models.mlsolver.formula import *
from models.cluedo import *


# Function that intializes the game, it generates a game model (CluedoGameModel) and deals the initial cards
def initializeGame(agents: list[str], n_weapons: int, n_people: int, n_rooms: int, n_high_order: int) -> CluedoGameModel:
    model = CluedoGameModel(agents, n_weapons, n_people, n_rooms, n_high_order)
    model.dealCards(n_weapons, n_people, n_rooms)
    return model

# Function to choose a question at random for an agent
def decideRandomQuestion(model: CluedoGameModel, current_agent: Player) -> list:
    weapon = random.choice(list(range(0, model.n_weapons)))
    person = random.choice(list(range(0, model.n_people)))
    room = random.choice(list(range(0, model.n_rooms)))
    return ['w' + str(weapon), 'p' + str(person), 'r' + str(room)]

# Function to choose a question for an agent based on their current knowledge
def decideQuestionWithKnowledge(model: CluedoGameModel, current_agent: Player, possible_solutions: list):
    weapons = set(range(0, model.n_weapons))
    people = set(range(0, model.n_people))
    rooms = set(range(0, model.n_rooms))
    for possibilities in possible_solutions:
        possibilitiesSplit = possibilities.split()
        weapons = weapons.difference({int(possibilitiesSplit[0][1])})
        people = people.difference({int(possibilitiesSplit[1][1])})
        rooms = rooms.difference({int(possibilitiesSplit[2][1])})
    weapons = weapons.difference(set(current_agent.weapons))
    people = people.difference(set(current_agent.people))
    rooms = rooms.difference(set(current_agent.rooms))
    weapon = random.choice(list(set(range(0, model.n_weapons)).difference(weapons)))
    person = random.choice(list(set(range(0, model.n_people)).difference(people)))
    room = random.choice(list(set(range(0, model.n_rooms)).difference(rooms)))
    return ['w' + str(weapon), 'p' + str(person), 'r' + str(room)]


# Function performs 1 turn
def nextMove(model: CluedoGameModel, current_agent: Player, base_on_knowledge: bool):
    possible_solutions = model.getPossibleSolutions(current_agent)

    if len(possible_solutions) == 1:
        cards = list(possible_solutions)[0].split()
        model.checkGameOver(str(current_agent), cards[0], cards[1], cards[2])

    else:
        if base_on_knowledge:
            cards = decideQuestionWithKnowledge(model, current_agent, possible_solutions)
        else:
            cards = decideRandomQuestion(model, current_agent)

        if model.turn > -1:
            model.movesHistory.append('Turn ' + str(model.turn) + ': Agent ' + str(current_agent) + ' asks for cards: ' + cards[0] + ' ' + cards[1] + ' ' + cards[2])
            cards_showed = askForCards(current_agent, model.agents, cards, model)
            if (len(cards_showed) == 0):
                model.movesHistory.append('No agents responded')
            model.movesHistory += cards_showed

        model.drawKnowledge()
        model.drawActions()

def askForCards(agent: Player, other_players, cards: list[str], model: CluedoGameModel) -> list[str]:
        question = Question(str(agent), int(cards[0][-1]), int(cards[1][-1]), int(cards[2][-1]))
        cards_showed = []
        for i_player in range(0, len(other_players)-1):
            player = other_players[(model.turn+1+i_player)%len(other_players)]
            cards_to_show = []
            if player != agent:
                for card in cards:
                    if ((int(card[-1]) in player.weapons) and card[0] == 'w') or \
                         ((int(card[-1]) in player.people) and card[0] == 'p') or \
                              ((int(card[-1]) in player.rooms) and card[0] == 'r'):
                        cards_to_show.append(card)
                if cards_to_show:
                    show = random.choice(cards_to_show)
                    agent.updateKnowledge(show)
                    model.agentResponds(str(player), question, model.turn)
                    cards_showed.append('Agent ' + str(player) + ' showed card ' + show + ' to Agent ' + str(agent))
                    if len(cards_to_show) > 1:
                        model.trueWorld.shownCardChoices.append(AgentShownChoice((show[0]), int(show[1]), str(player), model.turn)) 
                    break
                else:
                    model.agentSaysNo(player, question)
        return cards_showed

def runGame(model, base_on_knowledge):
    while True:
        buttonClicked = False
        model.mouse['click'] = -1

        model.checkInterfaceAction(pygame.event.get())
        buttonClicked = model.clickCheck()

        if buttonClicked:
            if model.gameInProgress != -1:
                nextMove(model, model.agents[model.turn % len(model.agents)], base_on_knowledge)
                model.turn += 1
        pygame.display.update()