from models.cluedo import listAgents
from game_logic import runGame, initializeGame

# The following function gives information to the user about what is expected
# It also takes the input of the user (from the terminal) and it processes it
def takeInput():
    # Number of Agents taken from input and list of agents created
    # Agents' names are created in alphabetical order (a, b, c, ...)
    n_agents = 0
    while n_agents > 6 or n_agents < 2:
        try:
            n_agents = int(input('Number of players (must be 2-6): '))
        except ValueError:
            print('invalid input')
    agents = listAgents(n_agents)

    # Desired number of higher order knowledge agents taken from user input
    n_high_order = -1
    while n_high_order > n_agents or n_high_order < 0:
        try:
            n_high_order = int(input('Number of players using high order knowledge: '))
            if n_high_order > n_agents:
                print('Number cannot be higher than the number of players')
            if n_high_order < 0:
                print('Number cannot be negative')
        except ValueError:
            print('invalid input')

    # Number of weapon cards to be implemented in the game, taken from user input
    n_weapons = 0
    while n_weapons > 10 or n_weapons < 1:
        try:
            n_weapons = int(input('Number of weapons (must be 1-10): '))
        except ValueError:
            print('invalid input')

    # Number of people cards to be implemented in the game, taken from user input
    n_people = 0
    while n_people > 10 or n_people < 1:
        try:
            n_people = int(input('Number of people (must be 1-10): '))
        except ValueError:
            print('invalid input')

    # Number of room cards to be implemented in the game, taken from user input
    n_rooms = 0
    while n_rooms > 10 or n_rooms < 1:
        try:
            n_rooms = int(input('Number of rooms (must be 1-10): '))
        except ValueError:
            print('invalid input')

    # Flag to see whether agents should base their in-game questions on knowledge, taken from user input
    base_on_knowledge = None
    while base_on_knowledge != 'y' and base_on_knowledge != 'n':
        try:
            base_on_knowledge = input("Base questions on agent's knowledge? (respond with y/n): ")
        except ValueError:
            print('invalid input')
    if base_on_knowledge == 'y':
        base_on_knowledge = True
    else:
        base_on_knowledge = False
        print('Questions will be chosen randomly')

    # Returning all user Inputs
    return agents, n_weapons, n_people, n_rooms, n_high_order, base_on_knowledge


if __name__ == "__main__":
    # Processing the input from the terminal
    agents, n_weapons, n_people, n_rooms, n_high_order, base_on_knowledge = takeInput()

    # Initializing the game
    model = initializeGame(agents, n_weapons, n_people, n_rooms, n_high_order)
    
    # Running the game
    runGame(model, base_on_knowledge)