from mesa import Agent
from models.mlsolver.formula import Atom
import random

class Player(Agent):
    def __init__(self: Agent, agent_name: str, model) -> Agent:

        super().__init__(agent_name, model)
        self.knowledge_base = {}
        self.weapons = []
        self.rooms = []
        self.personCards = []

    def setAtributes(self: Agent, weapon: int = None, room: int = None, person: int = None) -> None:
        if weapon != None:
            self.weapons.append(weapon)
        if room != None:
            self.rooms.append(room)
        if person != None:
            self.personCards.append(person)

    def updateKnowledge(self: Agent, smart_player: bool = False):
        pass


    def askPlayer(self: Agent, other_player: Agent, card_type: str) -> None:
        print(str(self) + " asks to see one of the " + card_type + " cards from " + str(other_player) + "'s hand")
        self.updateKnowledge()

    def __repr__(self: Agent) -> str:
        return str(self.unique_id)