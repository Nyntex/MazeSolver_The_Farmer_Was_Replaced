import Utility
import MazeSolver

#assuming we know nothing, this is the best algorithm
#everything in the MarkingsMap is a container so we always pass references and can change the global state from everywhere
MarkingsMap = {} # MarkingsMap[CurrentPos] = Node | Node = [Mark1, Mark2, Mark3, Mark4] | Mark = [Direction, Status]
MovingDirection = North
InverseDirections = {North:South, East:West, South:North, West:East}
CurrentNode = {}
CurrentPos = Utility.GetCurrentPosPair() 
GoalPos = [0,0]
WrapAround = False

#Maze Move To using Trémaux's algorithm
#has additional 
def MoveTo(PosX, PosY, UseWrapAround = False, StopAfterMoves = get_world_size()**2):
	global WrapAround
	WrapAround = UseWrapAround
	
	global MarkingsMap
	MarkingsMap = {}
	
	WorldSizeMinus1 = get_world_size()-1
	global GoalPos
	GoalPos[0] = min(PosX, WorldSizeMinus1)
	GoalPos[1] = min(PosY, WorldSizeMinus1)
	
	global MovingDirection
	MovingDirection = Utility.ChooseBestDirection(Utility.GetAvailableDirections(), GoalPos[0], GoalPos[1], WrapAround)
	
	
	TreasureLocation = measure()
	if TreasureLocation == None:
		return {}
	
	CurrentPosX = get_pos_x()
	CurrentPosY = get_pos_y()
	Moves = 0
	UpdatedNodes = {}
	while (CurrentPosX != GoalPos[0] or CurrentPosY != GoalPos[1]) and Moves < StopAfterMoves:
		move(MovingDirection)
		
		MazeSolver.AddNode(UpdatedNodes)
		
		NewTreasureLocation = measure()
		if NewTreasureLocation == None or NewTreasureLocation != TreasureLocation:
			return UpdatedNodes
		
		Moves += 1
		CurrentPosX = get_pos_x()
		CurrentPosY = get_pos_y()
		NewAvailableDirections = Utility.GetAvailableDirections()
		#if len(NewAvailableDirections) > 2: # found junction
		if not can_move(MovingDirection) or len(NewAvailableDirections) > 2:
			MarkJunctionAndSetDirection()
	
	return UpdatedNodes
	

#only call in context of AdvancedMoveTo
def MarkJunctionAndSetDirection():
	global MarkingsMap
	global InverseDirections
	global CurrentNode
	global CurrentPos
	
	CurrentPos = Utility.GetCurrentPosPair() 
	if CurrentPos in MarkingsMap:
		CurrentNode = MarkingsMap[CurrentPos]
		AvailableDirections = Utility.GetAvailableDirections()
		
		#check if junction might have a valid direction we can move to
		if DoesJunctionHaveUnmarkedDirection(): 	
			UpdateUnmarkedJunctionAndSetDirection()
			return
		#since its not unmarked it has to be marked
		UpdateMarkedJunctionAndSetDirection()
	else:
		MakeNewNodeAndSetDirection()

def DoesJunctionHaveInvalidMark():
	global CurrentNode

	for Mark in CurrentNode:
		if Mark[1] == -1:
			return True
	return False
	
def DoesJunctionHaveMark():
	global CurrentNode
	
	for Mark in CurrentNode:
		if Mark[1] == 1:
			return True
	return False

def DoesJunctionHaveUnmarkedDirection():
	global CurrentNode
	
	for Mark in CurrentNode:
		if Mark[1] == 0:
			return True
	return False

def UpdateMarkedJunctionAndSetDirection():
	#modifies our global current node
	global MovingDirection
	global InverseDirections
	global CurrentNode
	global CurrentPos
	
	#valid check
	if len(CurrentNode) == 0:
		#called without a valid current node
		return
	
	if len(CurrentNode) == 2:
		NewDirection = North
		for Mark in CurrentNode:
			Mark[1] = -1
			if Mark[0] != InverseDirections[MovingDirection]:
				NewDirection = Mark[0]
		MovingDirection = NewDirection
		return
	
	#called with all paths either marked or invalid
	MarkedDirections = 0
	for Mark in CurrentNode:
		if Mark[0] == InverseDirections[MovingDirection]:
			Mark[1] = -1
		if Mark[1] == 1:
			MarkedDirections += 1
	
	if MarkedDirections == 1:
		for Mark in CurrentNode:
			if Mark[1] == 1:
				Mark[1] = -1
				MovingDirection = Mark[0]
				return
	
	MovingDirection = InverseDirections[MovingDirection]


def UpdateUnmarkedJunctionAndSetDirection():
	#modifies our global current node
	global MovingDirection
	global InverseDirections
	global CurrentNode
	global CurrentPos
	global GoalPos
	global WrapAround
	
	#valid check
	if len(CurrentNode) == 0:
		#called without a valid current node
		return
	
	AreAllOtherDirectionsMarked = True
	UnmarkedDirections = []
	for Mark in CurrentNode:
		if Mark[1] == 0 and Mark[0] != InverseDirections[MovingDirection]:
			AreAllOtherDirectionsMarked = False
			UnmarkedDirections.append(Mark)
			
	# invalidate our direction if it was marked before
	for Mark in CurrentNode:
		if Mark[0] == InverseDirections[MovingDirection] and Mark[1] == 1:
			Mark[1] = -1
			break
		elif Mark[0] == InverseDirections[MovingDirection] and Mark[1] == 0:
			Mark[1] = -1
			MovingDirection = Mark[0]
			return
	
	 
	if AreAllOtherDirectionsMarked:
		for Mark in CurrentNode:
			if Mark[1] == 1:
				Mark[1] = -1
				MovingDirection = Mark[0]
				return
	else:
		BestDirection = UnmarkedDirections[0][0]
		Directions = []
		for Direction in UnmarkedDirections:
			Directions.append(Direction[0])
		
		BestDirection = Utility.ChooseBestDirection(Directions, GoalPos[0], GoalPos[1], WrapAround)
		
		for Unmarked in UnmarkedDirections:
			if Unmarked[0] == BestDirection:
				MovingDirection = Unmarked[0]
				Unmarked[1] = 1
				return
	

def MakeNewNodeAndSetDirection():
	global MarkingsMap
	global CurrentPos
	global MovingDirection
	global InverseDirections
	global WrapAround
	
	NewNode = []
	
	NewAvailableDirections = Utility.GetAvailableDirections()
	
	if len(NewAvailableDirections) == 1:
		NewNode.append([NewAvailableDirections[0], -1])
		MarkingsMap[CurrentPos] = NewNode
		MovingDirection = NewAvailableDirections[0]
		return
	
	for Direction in NewAvailableDirections:
		if Direction == InverseDirections[MovingDirection]:
			NewNode.append([Direction, 1])
		else:
			NewNode.append([Direction, 0])
	
	NewAvailableDirections.remove(InverseDirections[MovingDirection])
	BestDirection = Utility.ChooseBestDirection(NewAvailableDirections, GoalPos[0], GoalPos[1], WrapAround)
	for Mark in NewNode:
		if Mark[0] == BestDirection:
			Mark[1] = 1
			MovingDirection = Mark[0]
			break
	
	MarkingsMap[CurrentPos] = NewNode
	
	

#GetInvalidMarkJunctionDirection()