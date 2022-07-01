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


# Function that performs 1 game turn 
def nextMove(model: CluedoGameModel, current_agent: Player, base_on_knowledge: bool):
    # Saving all possible solutions left for the agent that takes the turn
    possible_solutions = model.getPossibleSolutions(current_agent)

    # If the agent cosiders only one solution, the agent accuses
    if len(possible_solutions) == 1:
        cards = list(possible_solutions)[0].split()

        # Checking if the accused cards are correct or not
        # If correct game over
        # If wrong agent is removed
        model.checkGameOver(str(current_agent), cards[0], cards[1], cards[2])

    # If the agent has multiple possible solutions a normal game turn happens
    else:
        # Selecting which cards the agent should ask for
        if base_on_knowledge:
            cards = decideQuestionWithKnowledge(model, current_agent, possible_solutions)
        else:
            cards = decideRandomQuestion(model, current_agent)

        # If the game is not yet in progress (started) the question asking is skipped
        if model.turn > -1:
            # Turn message saved
            model.movesHistory.append('Turn ' + str(model.turn) + ': Agent ' + str(current_agent) + ' asks for cards: ' + cards[0] + ' ' + cards[1] + ' ' + cards[2])
            
            # Agent asks for cards
            cards_showed = askForCards(current_agent, model.agents, cards, model)

            # If no agents responde corresponding message is saved
            if (len(cards_showed) == 0):
                model.movesHistory.append('No agents responded')
            
            # Message for other agents showing cards saved
            model.movesHistory += cards_showed

        # Redrawing the knowledge and the actions
        model.drawKnowledge()
        model.drawActions()


# Function used for an agent to ask other agents about cards
def askForCards(agent: Player, other_players, cards: list[str], model: CluedoGameModel) -> list[str]:
        question = Question(str(agent), int(cards[0][-1]), int(cards[1][-1]), int(cards[2][-1]))
        cards_showed = []

        # Cycling through the other agents agents
        for i_player in range(0, len(other_players)-1):
            player = other_players[(model.turn+1+i_player)%len(other_players)]
            cards_to_show = []

            if player != agent:
                # If one of the other agents has one or more of the cards asked for those cards are saved
                for card in cards:
                    if ((int(card[-1]) in player.weapons) and card[0] == 'w') or \
                         ((int(card[-1]) in player.people) and card[0] == 'p') or \
                              ((int(card[-1]) in player.rooms) and card[0] == 'r'):
                        cards_to_show.append(card)
                if cards_to_show:
                    # If the other agent has multiple cards to show, it will show just one to the current agent
                    show = random.choice(cards_to_show)

                    # First order knowledge is updated and higher order knowledge is updated for all higher order (smart) agents
                    agent.updateKnowledge(show)
                    model.agentResponds(str(player), question, model.turn)

                    # Message for the action is saved
                    cards_showed.append('Agent ' + str(player) + ' showed card ' + show + ' to Agent ' + str(agent))
                    if len(cards_to_show) > 1:
                        model.trueWorld.shownCardChoices.append(AgentShownChoice((show[0]), int(show[1]), str(player), model.turn)) 
                    break
                # If another agent does not have the cards asked for the higher order agents' knowledge is updated correspondingly
                else:
                    model.agentSaysNo(player, question)
        # The action message is returned
        return cards_showed


# Function used to run Game
def runGame(model, base_on_knowledge):
    while True:
        # Reseting the mouse
        buttonClicked = False
        model.mouse['click'] = -1

        # Checks all events that happen in the pygame
        model.checkInterfaceAction(pygame.event.get())

        # Checks for click in buttons' zones
        buttonClicked = model.clickCheck()

        # If a button has been clicked and the game is not in the game over state, turns are executed
        if buttonClicked:
            if model.gameInProgress != -1:
                nextMove(model, model.agents[model.turn % len(model.agents)], base_on_knowledge)
                model.turn += 1
        
        # Display of the game is updated.
        pygame.display.update()