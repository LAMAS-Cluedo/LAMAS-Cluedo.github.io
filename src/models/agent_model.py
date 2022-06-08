from mesa import Agent
from mlsolver.formula import Atom
import random

class Player(Agent):
    def __init__(self, agent_number, model):

        super().__init__(agent_number, model)
        self.knowledge_base = {}
        self.weapon = 0
        self.room = 0
        self.personCard = 0

    def setAtributes(self, weapon, room, person):
        self.weapon = weapon
        self.room = room
        self.person_card = person

    def updateKnowledge(self, smart_player = False):
        pass


    def askPlayer(self, other_player, card_type):
        print(str(self) + " asks to see one of the " + card_type + " cards from " + str(other_player) + "'s hand")
        self.updateKnowledge()

    def __repr__(self):
        return "Player " + str(self.unique_id)