# LAMAS-Cluedo.github.io
LAMAS Modelling Cluedo Project


# Project Structure

The project contains the website version of the assignment (report), a "requirements.txt" file, "img" folder with the images necessary for the website and the pygame and a "src" folder with all the necessary scripts necessary for running the models

## src Folder

Includes:
- **models Folder** : includes files related to all the models for the game

- **game_logic.py** : script containing all the function necessary for playing the game. Used in **run.py**

- **run.py** : script that takes the input from the terminal and runs the game from the user's input

## models Folder

Includes:
- **mlsolver Folder** : includes all files necessary for running the package "mlsolver"

- **saved_models Folder** : includes files which represent presaved game models, for different user inputs (files saved using pickle)

- **agent_model.py** : script that defines the Player class which represent the agents of the game and their related functions. Used in **game_model.py**

- **cluedo.py** : script that contains utilitary classes used across the other scripts

- **game_model.py** : script that defines the CluedoGameModel class (outline of the game) and its related functions. Used in **game_logic.py**

- **logic_model.py** : script that constructs the Kripke model for the game and all the functions related to it. Used in **game_model.py**

## Requirements

Mesa==0.9.0

pygame==2.1.2

tqdm==4.63.0

## The Report
The report is implemented in the form of a website which can be found under the following URL: https://lamas-cluedo.github.io/

# Running The Game

## Starting the Game

1. Directly run the script **run.py** or having the working directory set as the "LAMAS-Cluedo.github.io" folder run the script from the terminal by using **python src/run.py**

2. Input in the terminal all values necessary, as per the instruction in the terminal.

3. Game Launches

## Game Running

1. First press the "Play" button so the intial knowledge and actions will apear on the screen.

2. Continue pressing "Next" button to perform steps in the Game.

3. When the Game Over screen appears press "Quit" to exit the Game

# Copyright
Scripts created by:

Chris Worthington s3715086 && Leonidas Zotos s3396991 && Paul Pintea s3593673