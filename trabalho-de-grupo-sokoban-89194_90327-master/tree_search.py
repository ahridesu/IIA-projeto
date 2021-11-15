import agent
from copy import deepcopy
from deadlock import DeadlockAgent

class PathFindingNode:                      
    grid = []

    def __init__(self, symbol, position):
        self.position = position
        self.symbol = symbol
        self.previous = None 
        self.g = 0
        self.h = 0
    
    def __eq__(self, other):
        return self.position == other.position and self.symbol == other.symbol

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return str((self.position, self.symbol))

    def is_deadlock(self, adjacents, unwanted_symbols, gamestate):
        return DeadlockAgent(self.position, adjacents, unwanted_symbols, gamestate).check_all_deadlocks() if self.symbol not in ["#", ".", "*", "+"] and adjacents != None else False

    def children(self, all_children=False):
        x,y = self.position
        return [n for n in [self.grid[l][c] for c in range(len(self.grid[0])) for l in range(len(self.grid)) if self.grid[l][c].position in [(x-1, y),(x,y - 1),(x,y + 1),(x+1,y)]] if n.symbol in ['-', '@', '.', '+']] if not all_children else [n for n in [self.grid[l][c] for c in range(len(self.grid[0])) for l in range(len(self.grid)) if self.grid[l][c].position in [(x-1, y),(x,y - 1),(x,y + 1),(x+1,y)]]]

    #distance between each node and goal node (manhattan distance)
    def heuristics(self, node):
        x1, y1 = self.position
        x2, y2 = node.position
        return abs(x2 - x1) + abs(y2 - y1)

class GameStateNode:
    def __init__(self, gridstate=None, movement=None):
        self.gridstate = deepcopy(gridstate)
        self.movement = movement
        if movement != None:
            boxpos, nextboxpos = movement
            self.move(boxpos, nextboxpos, self.get_keeper())
        self.goals = self.get_goals()
        self.boxes = self.get_boxes()
        self.keeper = self.get_keeper()
        self.previous = None
        self.g = 0
        self.h = 0
        self.final = False

    def __eq__(self, other):
        if self.final or other.final:
            return self.boxes == other.get_boxes()
        return self.movement == other.movement and self.boxes == other.boxes 

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        string = ""
        for line in self.gridstate:
            for node in line:
                string += node.symbol
            string += "\n"
        
        return string

    def opposite(self, box, node):
        x_box, y_box = box.position
        x_node, y_node = node.position
        return self.gridstate[x_box + (x_box - x_node)][y_box + (y_box - y_node)]

    def get_keeper(self):
        lines = len(self.gridstate)
        cols = len(self.gridstate[0])
        for l in range(lines):
            for c in range(cols):
                if self.gridstate[l][c].symbol == '@' or self.gridstate[l][c].symbol == '+':
                    return self.gridstate[l][c]

    def get_goals(self):
        return [self.gridstate[l][c] for c in range(len(self.gridstate[0])) for l in range(len(self.gridstate)) if self.gridstate[l][c].symbol in ['.', '*', '+']]
    
    def get_boxes(self):
        return [self.gridstate[l][c] for c in range(len(self.gridstate[0])) for l in range(len(self.gridstate)) if self.gridstate[l][c].symbol in ['$', '*']]

    def legal_move(self, box, node):
        return False if TreeSearch(self.keeper, self.opposite(box, node), "greedy").search() == None else True

    def children(self):
        PathFindingNode.grid = self.gridstate
        return [GameStateNode(self.gridstate, (box.position, child.position)) for box in self.boxes for child in [n for n in [self.gridstate[l][c] for c in range(len(self.gridstate[0])) for l in range(len(self.gridstate)) if self.gridstate[l][c].position in [(box.position[0]-1, box.position[1]),(box.position[0],box.position[1] - 1),(box.position[0],box.position[1] + 1),(box.position[0]+1,box.position[1])]] if n.symbol not in ['#', '$', '*'] and self.opposite(box, n).symbol not in ['#','$',"*"] and self.legal_move(box, n) and not n.is_deadlock(n.children(True), ['#'], self)]]

    def move(self, posbox, poschild, keeper):
        #keeper
        if keeper.symbol == '+':
            keeper.symbol = '.'
        elif keeper.symbol == '@':
            keeper.symbol = '-'
        # boxes
        x_box, y_box = posbox
        x_child, y_child = poschild
        node_box = self.gridstate[x_box][y_box]
        node_child = self.gridstate[x_child][y_child]
        if node_child.symbol == '-':

            if node_box.symbol == '$':
                node_child.symbol = '$'
                node_box.symbol = '@'

            elif node_box.symbol == '*':
                node_box.symbol = '+'
                node_child.symbol = '$'

        elif node_child.symbol == '.':

            if node_box.symbol == '$':
                node_child.symbol = '*' 
                node_box.symbol = '@'

            elif node_box.symbol == '*':
                node_child.symbol = '*' 
                node_box.symbol = '+'

    def heuristics(self, node):
        h = {}
        boxes = self.boxes
        for i in range(0, len(self.boxes)):
            h[i] = []
            for j in range(0, len(self.boxes)):
                goal = self.goals[j]
                box = boxes[j]
                h[i].append(abs(goal.position[0]-box.position[0]) + abs(goal.position[1]-box.position[1]))
            boxes = boxes[1::] + [boxes[0]]
        return min([sum(box) for (index, box) in h.items()])

class TreeSearch:
    def __init__(self, start, goal, strategy):
        self.start = start 
        self.goal = goal
        self.strategy = strategy

    def search(self):
        #not seen nodes
        openset = set()
        #seen nodes
        closedset = set()

        curr_node = self.start
        curr_node.g = 0

        openset.add(curr_node)

        #finds the node with the lowest f function
        if self.strategy == "uniform":
            k = lambda n: n.g
        elif self.strategy == "greedy":
            k = lambda n: n.h
        elif self.strategy == "a*":
            k = lambda n: n.g+n.h

        while openset:
            curr_node = min(openset, key=k)

            #if node is goal box
            if curr_node == self.goal:
                path = []
                while curr_node != self.start:
                    path.append(curr_node)
                    curr_node = curr_node.previous
                path.append(self.start)
                return path[::-1]
        
            #if node is not goal box
            #check node as seen
            openset.remove(curr_node)
            closedset.add(curr_node)

            for n in curr_node.children():
                #if its already seen, skip it
                if n in closedset:
                    continue

                if n in openset: 
                    #compare if the new path g cost is lower than the current
                    try_g = curr_node.g + 1
                    if try_g < n.g:
                        # give the new g_cost
                        n.g = try_g
                        if n != self.start:
                            n.previous = curr_node
                else:
                    #calculate the g and h value for remaining nodes
                    n.g = curr_node.g + 1
                    n.h = n.heuristics(self.goal)
                    if n != self.start:
                        n.previous = curr_node
                    openset.add(n)




