import SunflowerFarm
import Companion

def PlantAndHarvest(Entity, GroundNeeded, MinWaterLevel = 0.1, UseFertilizer = False):
	if get_ground_type() != GroundNeeded:
		till()
	if not can_harvest() and get_entity_type() == Entities.Pumpkin:
		plant(Entity)
		return
	if can_harvest():
		harvest()
	plant(Entity)
	if get_water() <= MinWaterLevel and MinWaterLevel >= 0:
		use_item(Items.Water)
	if UseFertilizer:
		use_item(Items.Fertilizer)
		PlantAndHarvest(Entity, GroundNeeded, MinWaterLevel, False)

def GetGroundTypeForEntity(Entity):
	SoilTypes = {
	Entities.Pumpkin:Grounds.Soil, 
	Entities.Carrot:Grounds.Soil, 
	Entities.Sunflower:Grounds.Soil, 
	Entities.Cactus:Grounds.Soil,
	Entities.Bush:Grounds.Grassland, 
	Entities.Tree:Grounds.Grassland, 
	Entities.Grass:Grounds.Grassland, 
	}
	
	return SoilTypes[Entity]
	

def GetAvailableDirections():
	AvailableDirections = []
	if can_move(North):
		AvailableDirections.append(North)
	if can_move(East):
		AvailableDirections.append(East)
	if can_move(West):
		AvailableDirections.append(West)
	if can_move(South):
		AvailableDirections.append(South)
	
	return AvailableDirections


def SwapGroundType(GroundType):
	if get_ground_type() != GroundType:
		till()
	return

def DoNothing():
	return

def GetCurrentPosPair():
	return (get_pos_x(), get_pos_y())

#Using off screen movement
def SimpleMoveToLocation(PosX,PosY):
	WorldSize = get_world_size()
	CurrentPosX = get_pos_x()
	CurrentPosY = get_pos_y()
	MovesRight = ((WorldSize + PosX) - CurrentPosX) % WorldSize
	MovesUp = ((WorldSize + PosY)  - CurrentPosY) % WorldSize
	MovesLeft = ((WorldSize + CurrentPosX) - PosX) % WorldSize
	MovesDown = ((WorldSize + CurrentPosY) - PosY) % WorldSize
	
	if MovesRight > 0 and MovesRight < MovesLeft:
		for i in range(MovesRight):
			move(East)
	elif MovesLeft > 0:
		for i in range(MovesLeft):
			move(West)
	
	if MovesUp > 0 and MovesUp < MovesDown:
		for i in range(MovesUp):
			move(North)
	elif MovesDown > 0:
		for i in range(MovesDown):
			move(South)
	
	
# in looped farms we always start at the bottom left and start with i = 0,
# i in this case means the amount of north movements we used
def LoopedFarmWalkLeftOrRight(CurrentY):
	if CurrentY % 2 == 0:
		move(East)
	else:
		move(West)

# clears the field, ensures the ground is correct and plants
def EnsurePlantConditions(PlantType, MinWaterLevel = 0.5, IgnoreHarvestable = True):
	WaterLevel = get_water()
	if WaterLevel <= MinWaterLevel and num_items(Items.Water) > 0:
		use_item(Items.Water)
		
	CurrentPlantType = get_entity_type()
	if CurrentPlantType == PlantType:
		return
	while not can_harvest() and not IgnoreHarvestable and CurrentPlantType != None:
		continue
	harvest() #clear current field
	if PlantType != None:
		SwapGroundType(GetGroundTypeForEntity(PlantType))
		plant(PlantType)
	
		
def FieldLoop(StartPosX, StartPosY, EndPosX, EndPosY, FunctionToRun):
	for i in range(EndPosY - StartPosY + 1):
		for j in range(EndPosX - StartPosX):
			FunctionToRun(i,j)

			
#like clear(), but harvesting everything instead of just resetting	
def AllDroneFieldClear():
	SimpleMoveToLocation(0,0)
	LastActiveHandle = None
	for i in range(get_world_size()):
		NewHandle = None
		while NewHandle == None:
			NewHandle = spawn_drone(ClearColumn)
		LastActiveHandle = NewHandle
		move(East)
	if not has_finished(LastActiveHandle):
		wait_for(LastActiveHandle)
	clear()
	
def ClearColumn():
	for i in range(get_world_size()):
		HarvestCurrentPosition(Entities.Grass)
		if get_ground_type() == Grounds.Soil:
			till()
		move(North)
	return	
	
def EnsureEnergyIsHigh(AmountToKeep = 20000):
	while num_items(Items.Power) < AmountToKeep:
		SunflowerFarm.RunSunflowerFarm(0,0,get_world_size(), get_world_size())

#Planting
def AllDroneFullPlant(Entity, StartPosX = 0, StartPosY = 0, EndPosX = get_world_size(), EndPosY = get_world_size(), WaitAtEnd = True):
	SimpleMoveToLocation(StartPosX, StartPosY)
	LastActiveHandle = None
	for i in range(EndPosX - StartPosX):
		NewHandle = None
		while NewHandle == None:
			NewHandle = spawn_drone(PlantColumn, Entity, EndPosY - StartPosY)
		LastActiveHandle = NewHandle
		move(East)
	if LastActiveHandle and WaitAtEnd:
		wait_for(LastActiveHandle)


def PlantColumn(Entity, MaxMoves = get_world_size()):
	for i in range(MaxMoves):
		EnsurePlantConditions(Entity)
		move(North)

def PlantCompanionColumn(MaxMoves = get_world_size()):
	for i in range(MaxMoves):
		PosX, PosY = GetCurrentPosPair()
		Companion.PlantCompanion(PosX, PosY)
		move(North)
			

#Harvesting
def AllDroneFullHarvest(Entity, StartPosX = 0, StartPosY = 0, EndPosX = get_world_size(), EndPosY = get_world_size(), WaitAtEnd = True, WaitForHarvestable = True):
	SimpleMoveToLocation(StartPosX, StartPosY)
	LastActiveHandle = None
	for i in range(EndPosX - StartPosX):
		NewHandle = None
		while NewHandle == None:
			NewHandle = spawn_drone(HarvestColumn, Entity, WaitForHarvestable, EndPosY - StartPosY)
		LastActiveHandle = NewHandle
		move(East)
	if LastActiveHandle and WaitAtEnd:
		wait_for(LastActiveHandle)


def HarvestCurrentPosition(Entity, WaitForHarvestable = True):
	EnsurePlantConditions(Entity)
	while not can_harvest() and WaitForHarvestable and get_entity_type() != Entities.Dead_Pumpkin and get_entity_type() != None:
		continue
	harvest()


def HarvestColumn(Entity, WaitForHarvestable = True, MaxMoves = get_world_size()):
	for i in range(MaxMoves):
		HarvestCurrentPosition(Entity, WaitForHarvestable)
		move(North)

def DistanceTo(PosFrom, PosTo):
	DistanceX = 0
	DistanceY = 0
	
	if PosFrom[0] > PosTo[0]:
		DistanceX = PosFrom[0] - PosTo[0]
	else:
		DistanceX = PosTo[0] - PosFrom[0]
		
	if PosFrom[1] > PosTo[1]:
		DistanceY = PosFrom[1] - PosTo[1]
	else:
		DistanceY = PosTo[1] - PosFrom[1]
	
	return (DistanceX, DistanceY)

def Sleep(TimeToSleep):
	Time = get_time()
	while get_time() - Time < TimeToSleep:
		continue

def ChooseBestDirection(Directions, GoalPositionX, GoalPositionY, UseWrapAround = False):
	if UseWrapAround:
		WorldSize = get_world_size()
		CurrentPosX = get_pos_x()
		CurrentPosY = get_pos_y()
		MovesRight = ((WorldSize + GoalPositionX) - CurrentPosX) % WorldSize
		MovesUp = ((WorldSize + GoalPositionY)  - CurrentPosY) % WorldSize
		MovesLeft = ((WorldSize + CurrentPosX) - GoalPositionX) % WorldSize
		MovesDown = ((WorldSize + CurrentPosY) - GoalPositionY) % WorldSize
		
		BestMoves = 320000
		BestDirection = Directions[0]
		for Direction in Directions:
			if Direction == North and MovesUp < BestMoves and MovesUp != 0:
				BestMoves = MovesUp
				BestDirection = North
			elif Direction == South and MovesDown < BestMoves and MovesDown != 0:
				BestMoves = MovesDown
				BestDirection = South
			elif Direction == East and MovesRight < BestMoves and MovesRight != 0:
				BestMoves = MovesRight
				BestDirection = East
			elif Direction == West and MovesLeft < BestMoves and MovesLeft != 0:
				BestMoves = MovesLeft
				BestDirection = West
	else:
		CurrentPosX = get_pos_x()
		CurrentPosY = get_pos_y()
		Infinite = -1
	
		FarthestDistance = Infinite
		BestDirection = Directions[0]
	
		for Direction in Directions:
			ThisDistance = -1
			if Direction == North:
				if GoalPositionY - CurrentPosY <= 0:
					ThisDistance = Infinite
				else: 
					ThisDistance = GoalPositionY - CurrentPosY
			elif Direction == South:
				if CurrentPosY - GoalPositionY <= 0:
					ThisDistance = Infinite
				else: 
					ThisDistance = CurrentPosY - GoalPositionY
			elif Direction == East:
				if GoalPositionX - CurrentPosX <= 0:
					ThisDistance = Infinite
				else: 
					ThisDistance = GoalPositionX - CurrentPosX
			elif Direction == West:
				if CurrentPosX - GoalPositionX <= 0:
					ThisDistance = Infinite
				else: 
					ThisDistance = CurrentPosX - GoalPositionX
		
			if ThisDistance > FarthestDistance:
				FarthestDistance = ThisDistance
				BestDirection = Direction
		
	return BestDirection
