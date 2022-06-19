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

class CluedoWorld():
    def __init__(self, atoms):
        self.atoms = atoms
    
    def __str__(self):
        name = ''
        for atom in self.atoms:
            name += str(atom) + ' '
        return name[:-1]