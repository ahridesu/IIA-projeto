from tree_search import *
from copy import deepcopy

class Agent:

    def __init__(self, mapa):
        self.mapa = mapa
        self.starting_grid = grid(self.mapa)
        self.final_grid = self.final_state()
        self.path = self.decision()

    def key(self):
        keys = ""
        for i in range(len(self.path)-1):
            y, x = self.path[i]
            y_next, x_next = self.path[i+1]
            if (x - x_next, y - y_next) == (1,0):
                keys += 'a'
            elif (x - x_next, y - y_next) == (0,1):
                keys += 'w' 
            elif (x - x_next, y - y_next) == (-1,0):
                keys += 'd'
            elif (x - x_next, y - y_next) == (0,-1):
                keys += 's'
        return keys

    def decision(self):
        root = GameStateNode(self.starting_grid)
        goal = GameStateNode(self.final_grid)
        goal.final = True
        tree_boxes = TreeSearch(root, goal, "greedy")       
        tree_state = tree_boxes.search() 
        path = self.keeper_path(tree_state)
        return path

    def keeper_path(self, tree_state):
        path = []
        for i in range(len(tree_state)-1):
            childstate = tree_state[i]
            keeper = childstate.get_keeper()
            state = tree_state[i+1]
            boxpos, nextboxpos = state.movement
            x,y = boxpos
            x_next, y_next = nextboxpos
            box = state.gridstate[x][y]
            nextbox = state.gridstate[x_next][y_next]
            finish = state.opposite(box, nextbox)
            PathFindingNode.grid = childstate.gridstate
            tree_keeper = TreeSearch(keeper, finish, "greedy")
            aux = tree_keeper.search() 
            path += [node.position for node in aux] + [box.position] if aux != None else [keeper.position] + [box.position]
        return path

    def final_state(self):
        finalstate = deepcopy(self.starting_grid)
        lines = len(finalstate)
        cols = len(finalstate[0])
        for l in range(lines):
            for c in range(cols):
                if finalstate[l][c].symbol == '.' or finalstate[l][c].symbol == '+':
                    finalstate[l][c].symbol = '*'
                if finalstate[l][c].symbol == '$':
                    finalstate[l][c].symbol = '-'
        return finalstate 

def grid(mapa):
    # creates a grid of nodes from map
    mapa = str(mapa).split('\n')
    lines = len(mapa)
    cols = len(mapa[0])
    grid = [[0 for c in range(cols)] for l in range(lines)]
    for l in range(lines):
        for c in range(cols):
            grid[l][c] = PathFindingNode(mapa[l][c], (l,c))
    return grid


