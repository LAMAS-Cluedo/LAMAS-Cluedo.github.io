import pickle
from mlsolver.kripke import *
from mlsolver.formula import *
from cluedoClasses import SolAtom, AgentCard, CluedoWorld

with open('saved_models/CluedoModel_a=3_w=3_p=3_r=3.pkl', 'rb') as modelFile:
    model = pickle.load(modelFile)

print(len(model.worlds))
print(len(model.relations['a']))
print(len(model.relations['b']))
print(len(model.relations['c']))