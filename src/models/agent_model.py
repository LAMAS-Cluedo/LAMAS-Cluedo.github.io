from typing import Any
from mesa import Agent
from models.mlsolver.formula import Atom, Not
import random

class Player(Agent):
    def __init__(self: Agent, agent_name: str, model) -> Agent:

        super().__init__(agent_name, model)
        self.knowledge_base = []
        self.weapons = []
        self.rooms = []
        self.people = []

    def setAtributes(self: Agent, weapon: int = None, person: int = None, room: int = None) -> None:
        if weapon != None:
            self.weapons.append(weapon)
            self.updateKnowledge(card="w"+str(weapon))
        if room != None:
            self.rooms.append(room)
            self.updateKnowledge(card="r"+str(room))
        if person != None:
            self.people.append(person)
            self.updateKnowledge(card="p"+str(person))

    def updateKnowledge(self: Agent, card: any, smart_player: bool = False) -> None:
        if type(card) is str:
            self.knowledge_base.append(str(card))
        else:
            for item in card:
                self.knowledge_base.append(str(item))
        pass


    def askForCards(self: Agent, other_players, cards: list[str]) -> list[str]:
        cards_to_show = []
        cards_showed = []
        for player in other_players:
            if player != self:
                for card in cards:
                    if (int(card[-1]) in player.weapons) or (int(card[-1]) in player.people) or (int(card[-1]) in player.rooms):
                        cards_to_show.append(card)
                if cards_to_show:
                    show = random.choice(cards_to_show)
                    self.updateKnowledge(show)
                    cards_showed.append('Agent ' + str(player) + ' showed card ' + show + ' to Agent ' + str(self))
        return cards_showed

        #print(str(self) + " asks to see one of the " + card_type + " cards from " + str(other_player) + "'s hand")
        #self.updateKnowledge()

    def __repr__(self: Agent) -> str:
        return str(self.unique_id)