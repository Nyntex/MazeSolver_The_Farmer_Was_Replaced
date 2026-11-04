import Utility
import MazeTremauxMoveTo

Runs = 301
RunsMade = 0
MazeSize = num_unlocked(Unlocks.Mazes) 

def StartMazeRun(RunsToDo = 301, Size = num_unlocked(Unlocks.Mazes)):
	global Runs
	Runs = RunsToDo
	
	global RunsMade
	RunsMade = 0
	
	global MazeSize
	MazeSize = min(Size, num_unlocked(Unlocks.Mazes))
	
	#spawn first maze
	SpawnMaze()
	MasterBehavior()
	#for i in range(Runs):
	#while True:
	#	TreasureLocationX, TreasureLocationY = measure()
	#	AdvancedMoveTo.AdvancedMoveTo(TreasureLocationX, TreasureLocationY)
	#	RunsMade += 1
	#	if RunsMade < Runs:
	#		SpawnMaze()
	#	else:
	#		harvest()
	
	#Utility.SimpleMoveToLocation(0,0)
	return
	

def SpawnMaze():
	global RunsMade
	global MazeSize
	
	EntityType = get_entity_type()
	if EntityType == Entities.Treasure and RunsMade < 300:
		substance = get_world_size() * 2**(MazeSize - 1)
		use_item(Items.Weird_Substance, substance)
		return
		
	Utility.EnsurePlantConditions(Entities.Bush)
	substance = get_world_size() * 2**(MazeSize - 1)
	use_item(Items.Weird_Substance, substance)
	RunsMade = 0
	
def ReuseMaze():
	TreasureLocation = measure()
	if TreasureLocation == None:
		return
	
	EntityType = get_entity_type()
	if EntityType != Entities.Treasure:
		return
	
	substance = get_world_size() * 2**(MazeSize - 1)
	use_item(Items.Weird_Substance, substance)
	NewTreasureLocation = measure()
	if NewTreasureLocation == TreasureLocation:
		harvest()
	
	

#QueenPositions = {}
#NodeMap = {}
def MasterBehavior():
	global NodeMap
	NodeMap = {}
	WorldSize = get_world_size()
	S = WorldSize / 4
	Sp = S/2
	
	QueenPositions = [(Sp,Sp),(Sp+S,Sp),(Sp+S*2,Sp),(Sp+S*3,Sp), (Sp,Sp+S),(Sp+S,Sp+S),(Sp+S*2,Sp+S),(Sp+S*3,Sp+S), (Sp,Sp+S*2),(Sp+S,Sp+S*2),(Sp+S*2,Sp+S*2),(Sp+S*3,Sp+S*2), (Sp,Sp+S*3),(Sp+S,Sp+S*3),(Sp+S*2,Sp+S*3),(Sp+S*3,Sp+S*3)]
	#implement mapping stage
	#queens don't require full map because workers are spawned after the mapping stage causing each worker to have a full map
	#  Queens and Workers snapshot the map the moment they use the global keyword, so modifying the map before they snapshot it 
	#  on the main drone all Queens and Workers will have the correct full map
	#workers use a* to traverse the map and return an updated map when they encounter a new shortcut
	
	#map whole maze
	NodeMap = MapWorld()
		
	for x in range(WorldSize):
		for y in range(WorldSize):
			if (x,y) not in NodeMap:
				Utility.DoNothing()

	# spawn queens 
	Index = len(QueenPositions)-1
	Handles = []
	for num in range(len(QueenPositions)):
		NewHandle = None
		while NewHandle == None:
			NewHandle = spawn_drone(QueenPlacer, QueenPositions[Index], Sp*1.5)
		Handles.append(NewHandle)
		QueenPositions.remove(QueenPositions[Index])
		if len(QueenPositions) == 1:
			break
		Index -= 1
		
	#move to last available position
	for Pos in QueenPositions:
		MovesToMake = FindPath(Pos)
		FollowPathAndUpdateMap(MovesToMake)
		break
	
	for Handle in Handles:
		if Handle != None and not has_finished(Handle):
			wait_for(Handle)
		
	spawn_drone(Utility.Sleep, 1)
	spawn_drone(Utility.Sleep, 1)
	spawn_drone(Utility.Sleep, 1)
	QueenBehavior(S)
	
def QueenPlacer(Pos, SizeToConsider):
	global NodeMap
	
	MovesToMake = FindPath(Pos)
	FollowPathAndUpdateMap(MovesToMake)
	
	Handle = None
	while Handle == None:
		Handle = spawn_drone(QueenBehavior, SizeToConsider)
		

def QueenBehavior(SizeToConsider):
	global RunsMade 
	global NodeMap
		
	QueenLocation = Utility.GetCurrentPosPair()
	SpawnedWorkers = []
	LastTreasureLocation = None
	EntityType = get_entity_type()
	AlreadySpawnedDrone = False
	while EntityType == Entities.Hedge or EntityType == Entities.Treasure:
		#updated map if possible
		if len(SpawnedWorkers) > 0:
			HandlesToRemove = []
			for Worker in SpawnedWorkers:
				if has_finished(Worker):
					NodeMapChanges = wait_for(Worker)
					HandlesToRemove.append(Worker)
		
					for Change in NodeMapChanges:
						NodeMap[Change] = NodeMapChanges[Change]
		
			for ToRemove in HandlesToRemove:
				SpawnedWorkers.remove(ToRemove)
		
		# check treasure
		#  if no treasure exists: exit
		EntityType = get_entity_type()
		NewTreasureLocation = measure()
		if NewTreasureLocation == None:
			#kill if there is no more maze
			return
		
		
		if NewTreasureLocation != LastTreasureLocation and not AlreadySpawnedDrone:
			Distance = Utility.DistanceTo(QueenLocation, NewTreasureLocation)
			if Distance[0] < SizeToConsider and Distance[1] < SizeToConsider:
				Worker = spawn_drone(WorkerBehavior, NewTreasureLocation)
				if Worker != None:
					SpawnedWorkers.append(Worker)
		
		Handle = spawn_drone(WorkerBehavior, NewTreasureLocation, FindPath(NewTreasureLocation, True))
		if Handle != None:
			AlreadySpawnedDrone = True
			SpawnedWorkers.append(Handle)
		
		AlreadySpawnedDrone = False
		LastTreasureLocation = NewTreasureLocation
		
	return
	
def WorkerBehavior(Location, OptionalMoves = []):
	global NodeMap
	KillOnTreasureChange = True
	
	UpdatedMap = {}
	MovesToMake = OptionalMoves
	if len(MovesToMake) <= 0:
		UpdatedMap = MazeTremauxMoveTo.MoveTo(Location[0], Location[1], False, 32000)
	else:
		UpdatedMap = FollowPathAndUpdateMap(MovesToMake, KillOnTreasureChange)
	
	while get_entity_type() == Entities.Treasure:
		ReuseMaze()
	return UpdatedMap

def MoveFollowingRight(CurrentDirection):
	if can_move(GetRightOf(CurrentDirection)):
		CurrentDirection = GetRightOf(CurrentDirection)
	if not can_move(CurrentDirection):
		CurrentDirection = GetLeftOf(CurrentDirection)
	move(CurrentDirection)
	return CurrentDirection

def GetRightOf(Direction):
	RightOf = {North:East, East:South, South:West, West:North}
	return RightOf[Direction]

def GetLeftOf(Direction):
	LeftOf = {North:West, East:North, South:East, West:South}
	return LeftOf[Direction]
	
def MapWorld():
	CurrentDirection = North
	WorldSquared = get_world_size()**2
	NodeMap = {}
	while len(NodeMap) < WorldSquared:
		CurrentDirection = MoveFollowingRight(CurrentDirection)
		if Utility.GetCurrentPosPair() not in NodeMap:
			NodeMap = AddNode(NodeMap)
	return NodeMap
	
def AddNode(NodeMap):
	Pos = Utility.GetCurrentPosPair()
	AvailableDirections = Utility.GetAvailableDirections()
	NodeMap[Pos] = AvailableDirections
	return NodeMap
	
def FindPath(GoalPos, KillOnTreasureChange = False):
	global NodeMap
	
	if GoalPos == None:
		return []
	
	TreasureLocation = None
	if KillOnTreasureChange:
		TreasureLocation = measure()
		if TreasureLocation == None:
			return []
	
	
	CurrentDronePosition = Utility.GetCurrentPosPair()
	DistanceToGoal = Utility.DistanceTo(CurrentDronePosition, GoalPos)
	HeuristicDistance = (DistanceToGoal[0]**2) + (DistanceToGoal[1]**2)
	
	OpenList = []
	OpenList.append((CurrentDronePosition, [HeuristicDistance,0,HeuristicDistance, None])) # Node = ((PosX,PosY),TotalCost,DistanceToStart,HeuristicDistanceToGoal, ParentPosition)
	
	ClosedList = {}
	GoalNode = None
	CurrentPosition = CurrentDronePosition
	#PositionsChecked = []
	while len(OpenList) > 0:
		if KillOnTreasureChange:
			NewTreasureLocation = measure()
			if NewTreasureLocation == None or NewTreasureLocation != TreasureLocation:
				return []
		
		CurrentNode = OpenList[0]
		CurrentNodeG = CurrentNode[1][1]
		CurrentPosition = CurrentNode[0] #get the position of the node N
		#PositionsChecked.append((CurrentPosition, NodeMap[CurrentNode[0]]))
		if CurrentPosition == GoalPos:
			GoalNode = CurrentNode
			ClosedList[GoalNode[0]] = GoalNode
			break
		AvailableDirectionsFromMap = NodeMap[CurrentPosition]
		#add all available directions from that node onto the open list, when possible
		for Direction in AvailableDirectionsFromMap:
			NewPositionX, NewPositionY = CurrentPosition
			if Direction == North:
				NewPositionY += 1
			elif Direction == South:
				NewPositionY -= 1
			elif Direction == East:
				NewPositionX += 1
			elif Direction == West:
				NewPositionX -= 1
			
			NewPosition = (NewPositionX, NewPositionY)
			#checks so we don't add nodes we are already checking
			if NewPosition in ClosedList:
				#skipping nodes that are already in the closed list
				#so we don't check them again
				continue
			
			DistanceToGoal = Utility.DistanceTo(NewPosition, GoalPos)
			HeuristicDistance = (DistanceToGoal[0]**2) + (DistanceToGoal[1]**2)
			
			NewNode = (NewPosition, [CurrentNodeG + 1 + HeuristicDistance, CurrentNodeG+1, HeuristicDistance, CurrentPosition])
			
			#check if its already in the OpenList and optionally replace it
			FoundInOpenList = False
			BetterThanOpenList = False
			for Index in range(len(OpenList)):
				if OpenList[Index][0] == NewPosition:
					FoundInOpenList = True
					#check if move cost is lower
					if OpenList[Index][1][1] > NewNode[1][1]:
						OpenList.pop(Index)
						BetterThanOpenList = True
					break
						
			AddedToOpenList = False
			if FoundInOpenList and not BetterThanOpenList:
				continue	
			elif (FoundInOpenList and BetterThanOpenList) or not FoundInOpenList:
				for Index in range(len(OpenList)):
					if OpenList[Index][1][0] > NewNode[1][0]:
						OpenList.insert(Index, NewNode)
						AddedToOpenList = True
						break
			if not AddedToOpenList:
				OpenList.append(NewNode)
	
		ClosedList[CurrentNode[0]] = CurrentNode
		for Index in range(len(OpenList)):
			if OpenList[Index][0] == CurrentNode[0]:
				OpenList.pop(Index)
				break
		continue
	
	# reverse pathfind
	#if GoalNode == None:
		#quick_print("PATHFINDING FAILED")
		#return []
		
	CheckingPosition = GoalNode[0]
	MovesToMake = []
	while CheckingPosition != CurrentDronePosition:
		CheckingNode = ClosedList[CheckingPosition]
		ParentNode = ClosedList[CheckingNode[1][3]]
		
		MoveToMake = None
		#inverted thinking, which move do we have to make to get from parent to child
		if ParentNode[0][0] != CheckingPosition[0]:
			if ParentNode[0][0] > CheckingPosition[0]:
				MoveToMake = West
			else:
				MoveToMake = East
		else:
			if ParentNode[0][1] > CheckingPosition[1]:
				MoveToMake = South
			else:
				MoveToMake = North
				
		MovesToMake.insert(0, MoveToMake)
		CheckingPosition = ParentNode[0]
	
	return MovesToMake

def FollowPathAndUpdateMap(Path, ReturnWhenTreasureChange = False):
	UpdatedNodeMap = {}
	#checks also if the treasure location changes
	TreasureLocation = None
	if ReturnWhenTreasureChange:
		TreasureLocation = measure()
		if TreasureLocation == None:
			return UpdatedNodeMap
	
	UpdatedNodeMap = AddNode(UpdatedNodeMap)
	for Direction in Path:
		move(Direction)
		UpdatedNodeMap = AddNode(UpdatedNodeMap)
		#early cancel if our move would end in nothing
		if ReturnWhenTreasureChange:
			NewTreasureLocation = measure()
			if NewTreasureLocation != TreasureLocation:
				return UpdatedNodeMap
	
	return UpdatedNodeMap
	
	
#set_execution_speed(1)
#clear()
#StartMazeRun()
#StartMazeRun(4)
#AdvancedMoveTo.AdvancedMoveTo(get_world_size(), get_world_size(), True)