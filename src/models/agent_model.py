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
            self.knowledge_base.append(str(self)+str(card))
        else:
            for item in card:
                self.knowledge_base.append(str(self)+str(item))
        pass


    def askPlayer(self: Agent, other_player: Agent, card_type: str) -> None:
        print(str(self) + " asks to see one of the " + card_type + " cards from " + str(other_player) + "'s hand")
        #self.updateKnowledge()

    def __repr__(self: Agent) -> str:
        return str(self.unique_id)