class SolAtom():
    def __init__(self, type, number):
        super().__init__()
        self.type = type
        self.number = number

    def __str__(self):
        return str(self.type) + str(self.number)
    
    def equalTo(self, type, number):
        return self.type == type and self.number == number


class AgentCard(SolAtom):
    def __init__(self, type, number, agent):
        super().__init__(type, number)
        self.agent = agent
    
    def __str__(self):
        return str(self.agent) + str(self.type) + str(self.number)
        
    def equalTo(self, type, number, agent):
        return self.type == type and self.number == number and self.agent == agent


class AgentShownChoice():
    def __init__(self, type, number, agent, turn):
        self.type = type
        self.number = number
        self.agent = agent
        self.turn = turn 
    
    def __str__(self):
        return str(self.agent) + str(self.type) + str(self.number) + '_t' + str(self.turn)
        
    def equalTo(self, type, number, agent):
        return self.type == type and self.number == number and self.agent == agent


class CluedoWorld():
    def __init__(self, atoms):
        self.atoms = atoms
        self.shownCardChoices = []
    
    def __str__(self):
        name = ''
        for atom in self.atoms:
            name += str(atom) + ' '
        for choice in self.shownCardChoices:
            name += str(choice) + ' '
        return name[:-1]
    
    def noTurnAtoms(self):
        name = ''
        for atom in self.atoms:
            name += str(atom) + ' '
        return name[:-1]

    def addShownCardChoice(self, choice):
        self.shownCardChoices.append(choice)


class Question():
    def __init__(self, agent, weapon, person, room):
        self.agent = agent
        self.weapon = weapon
        self.person = person
        self.room = room

    def wAtom(self):
        return 'w' + str(self.weapon);

    def pAtom(self):
        return 'p' + str(self.person);

    def rAtom(self):
        return 'r' + str(self.room);

def listAgents(n_agents):
    return [chr(agent) for agent in list(range(97, 97+n_agents))]