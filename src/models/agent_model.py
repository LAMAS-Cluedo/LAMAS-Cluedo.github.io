from typing import Any
from mesa import Agent, Model
from models.cluedo import Question
from models.mlsolver.formula import Atom, Not
import random

# Creating Player class to be used as agents/players in the game
class Player(Agent):
    def __init__(self: Agent, agent_name: str, model: Model, high_order: bool) -> Agent:
        super().__init__(agent_name, model)
        self.high_order = high_order
        self.knowledge_base = []
        self.weapons = []
        self.rooms = []
        self.people = []

    # Sets intial cards dealt for each agent and updates the agent's first order knowledge base, based on those cards
    def setAtributes(self: Agent, weapon: int = None, person: int = None, room: int = None) -> None:
        if weapon != None:# Agent receives initial weapon and updates first order knowledge
            self.weapons.append(weapon)
            self.updateKnowledge(card="w"+str(weapon))
        
        if room != None:# Agent receives intial room and updates first order knowledge
            self.rooms.append(room)
            self.updateKnowledge(card="r"+str(room))
        
        if person != None:# Agent receives intial person and updates first order knowledge
            self.people.append(person)
            self.updateKnowledge(card="p"+str(person))

    # Following function adds first order knowledge to the player/agents knowledge base
    def updateKnowledge(self: Agent, card: any) -> None:
        if type(card) is str:
            self.knowledge_base.append(str(card))
            self.knowledge_base = list(set(self.knowledge_base))
        else:
            for item in card:
                self.knowledge_base.append(str(item))
            self.knowledge_base = list(set(self.knowledge_base))
        pass

    # When calling just the agent it's name should be returned
    def __repr__(self: Agent) -> str:
        return str(self.unique_id)