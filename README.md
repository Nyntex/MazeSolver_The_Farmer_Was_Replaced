# Maze Solver
This is my solution of a Maze Solver for the game "The Farmer Was Replaced()" (https://store.steampowered.com/app/2060160/The_Farmer_Was_Replaced/) where the user needs to automate a drone through code.
It utilizes all 32 available drones and 2.5 pathfinding algorithms to finish the exercise in ~5 minutes.

## What even is "The Farmer Was Replaced()"
If you are too lazy to read the steam page or watch its trailer, here is a quick rundown.
"The Farmer Was Replaced" is a factory game where you utilize a drone/s to gather resources using python code.
Different plants have different requirements and not all code is available from the start and must be unlocked, like for example operators.
One major feature of the game is the Tick. Almost all instructions cost Ticks in order to be fulfilled and from the start there are 400 ticks in every second. But every instruction may cost different amount of ticks so to optimize the code we must ensure to use as few ticks as possible.

Then there are leaderboards, challenges so to speak, where you must complete a goal in the shortest time possible, one of them is the Maze challenge for which this solver is made.

## Installation
Place the python scripts into AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced\Saves\{YOURSAVEGAMENAME}

## How does it work?
First of all the challenge. The challenge is to solve a maze 300 times where after each try the treasure moves to a new location and might remove a wall in the maze.
The first maze always spawns without any loops, this is an important detail as it allows us to use our first "pathfinding algorithm", the Wall-Hugging method.
We first have to map out the maze, this takes roughly one minute but ensures we move to all positions.
Now we have a map of all locations and with all available directions which we can use later. An important detail to mention here is the lack of objects. we only have access to basic types like int, float and bool and a small assortment of containers.

We create an array with the positions for 16 queens. Why specifically 16? because they fit nicely in a 4x4 grid and allows us to spawn enough searcher drones for any location. You could opt for a 5x5, but that doesn't leave much space for A* (later more on that) and the default Worker drones, but I will try to do that as well, see how it goes and update the code accordingly.
With the maze mapped out we start to spawn our "Queens". The queens will find a path to their position using A*. 
Now is a good point to mention how global variables, like our map, work. Drones do not share memory, so Drone A does not know what variables Drone B has and vice versa. So how do we share what we have? Now option 1 would be to just give it the information we have so that it can set it's own map, however, there is a better way. When a drone is summoned it snapshots all global variables from its parent, copying them for it's own use. So once a queen is spawned it gains a copy of the map it can use to find it's own path.

So, the queen finds a path using A*, that can take a while, because as stated before, each instruction cost ticks, that's just a gameplay mechanic, so depending on how far away the spot is it can take up to 30 seconds to find the path. Following the given path is very quick.

Now we stand before the problem, A* is slow when starting and Wall-Hug does not work with loops, so we need a third algorithm that "just works".
For that we use Trémaux's Algorithm, an algorithm that is able to, without knowledge of a maze, to traverse it an guarantee to reach its end, or in this case, the treasure. I added bias to be more likely to move into the direction of the treasure, but apart from that it works just the same.

The tactic is very simple, when the treasure is summoned to a new spot we spawn a Trémaux Worker Drone which starts running through the maze instantly. While that drone is running we try to find a direct path to the treasure using A* and only if the treasure hasn't changed it's location we spawn a Path Follow Worker Drone which traverses the maze very rapidly and probably reaches the goal faster than all the others.

<img width="810" height="666" alt="Record" src="https://github.com/user-attachments/assets/4337ef78-fc90-4f4e-b2ef-9305baa90411" />
