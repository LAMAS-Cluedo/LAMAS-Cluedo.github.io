from mesa import Model
from mesa.time import RandomActivation
from models.agent_model import Player

from models.logic_model import initializeKripke
from models.mlsolver.kripke import KripkeStructure


class CluedoGameModel(Model):

    def __init__(self: Model, names_agents: list[str], n_weapons: int, n_people: int, n_rooms: int) -> Model:
        self.schedule = RandomActivation(self)
        self.ks = []
        self.target_cards = []
        
        for agent_name in names_agents:
            agent = Player(agent_name, self)
            self.schedule.add(agent)

        self.initializeLogicStructure(
            self.schedule.agents, 
            n_weapons, 
            n_people, 
            n_rooms
            )
    

    def setCardsOnTable(self: Model, weapon: int, person: int, room: int):
        self.target_cards = [weapon, person, room]


    def initializeLogicStructure(self: Model, names_agents: list[str], n_weapons: int, n_people: int, n_rooms: int) -> KripkeStructure:
        self.ks = initializeKripke(
            agents=names_agents, 
            n_weapons=n_weapons, 
            n_people=n_people, 
            n_rooms=n_rooms
            )
