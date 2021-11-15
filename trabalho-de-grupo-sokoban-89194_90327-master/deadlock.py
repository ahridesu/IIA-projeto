class DeadlockAgent:
	def __init__(self, position, adjacents, unwanted_symbols, gamestate):
		self.position = position
		self.obstacles = [adjacent for adjacent in adjacents if adjacent.symbol in unwanted_symbols]
		self.gamestate = gamestate

	def check_all_deadlocks(self):
		if self.deadlock_corner():
			return True
		
		if self.deadlock_next_to_walls_no_goal_in_path():
			return True
		
		return False

	def deadlock_corner(self):
		x, y = self.position
		return any([all(square in [obstacle.position for obstacle in self.obstacles] for square in pair) for pair in [[(x-1, y), (x, y+1)], [(x, y+1), (x+1, y)], [(x+1, y), (x, y-1)], [(x, y-1), (x-1, y)]]])
	
	def deadlock_next_to_walls_no_goal_in_path(self):
		x, y = self.position
		mapa = self.gamestate.gridstate
		map_limits = len(mapa)-1, len(mapa[0])-1
		checks = []
		# loop through the obstacles (children that are walls) of the square that is being tested for deadlock
		for obstacle in self.obstacles:
			xo, yo = obstacle.position
			# understand if the row of walls that make up the deadlock is horizontal or vertical
			direction = "vertical" if yo != y else "horizontal"

			# check if there is a goal in the same line of the position, depending on the direction of the row of walls
			# if there is a goal in that line, than it is not deadlock
			if direction == "horizontal":
				if any([goal.position[0] == x for goal in self.gamestate.goals]):
					return False
			else:
				if any([goal.position[1] == y for goal in self.gamestate.goals]):
					return False

			# check if the children on both sides of the obstacle are also walls
			# put true or false in the array checks
			checks.append(sides_are_walls(self, obstacle, mapa, obstacle.children(True), direction))
		# if there is atleast one obstacle that has sides_are_walls as true, then it is deadlock
		return any(checks)

def sides_are_walls(parent, current, mapa, adjacents, direction):
	x, y = current.position
	# choose which sides to check, depending on the direction of the deadlock
	sides = [(x-1,y), (x+1,y)] if direction == "vertical" else [(x,y-1), (x,y+1)]
	# get the nodes for those sides
	sides_nodes = [adjacent for adjacent in adjacents if adjacent.position in sides] 
	# go check with a recursive function if the rest of the squares until frame are walls (do this for both sides)
	# if it is true for both sides, then it is deadlock
	return all([side_is_wall(parent, current, side, mapa, side.children(True), direction) for side in sides_nodes])

def side_is_wall(origin, parent, current, mapa, adjacents, direction):
	x, y = current.position
	
	# index 0 of tuple is the direction to go if curr is wall, index 1 is if curr is not wall
	sides = ([(x-1,y), (x+1,y)], [(x,y-1), (x,y+1)]) if direction == "vertical" else ([(x,y-1), (x,y+1)], [(x-1,y) , (x+1,y)])

	# if the current symbol is not wall
	if current.symbol != "#":
		# if the square before the current was not wall either
		if parent.symbol != "#":
			# then 2 walls in a row and it is not deadlock
			return False

		obstacles = [adjacent.position for adjacent in adjacents if adjacent.symbol == "#"]
		# not being wall, if any of the squares adjacent to it, that is not in the direction of the row of walls being
		# checked, are walls, then it is a passage so it is not deadlock
		if all([side not in obstacles for side in sides[1]]):
			return False

	ox, oy = origin.position
	if direction == "horizontal":
			possible_blockage = ox, y
	else:
		possible_blockage = x, oy

	if mapa[possible_blockage[0]][possible_blockage[1]].symbol == "#":
		return True

	# choose side oposite to parent
	side = [side for side in sides[0] if side != parent.position][0]
	# get node
	side_node = mapa[side[0]][side[1]]
	return side_is_wall(origin, current, side_node, mapa, side_node.children(True), direction)