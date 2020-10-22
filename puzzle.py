import collections
import numpy as np
import copy
import warnings
import math
import heapq
import time

#check if a string can be cast to an int
def string_is_int(s):
    try:
        s=int(s)
    except ValueError:
        print("Error in file")
        return None
    return int(s)

def flatten(nested_list):
    if isinstance(nested_list, collections.Iterable):
        return [j for i in nested_list for j in flatten(i)]
    else:
        return [nested_list]

def LoadFromFile(file_path):
    file1 = open(file_path, 'r')
    tiles = []
    N = file1.readline()
    N = string_is_int(N)
    while True:
        line = file1.readline()
        if not line:
            break
        line = line.replace("*", "0")
        line = line.split("\t")
        line = list(map(string_is_int, line))
        if None in line:
            return None
        tiles.append(line)
    f_tiles=flatten(tiles)
    if len(tiles) == N and len(tiles[0]) == N and sorted(f_tiles) == list(range(N**2)):
        return f_tiles
    else:
        print("Error in file")
        return None

#Takes in a game state (stored as an array) and prints it. 0 not converted to *
def DebugPrint(state):
    N=round(math.sqrt(len(state)))
    for i in range(N):
        print(*state[i*N:i*N+N], sep="\t")

#Takes in a game state (as array) and finds positions reachable from 1 move.
def ComputeNeighbors(state):
    N=round(math.sqrt(len(state)))
    zero_loc = state.index(0)

    #can the gap move left?
    left = not zero_loc % N == 0
    #can gap move right?
    right = not zero_loc % N == N-1
    #can gap move up?
    up = not (0 <= zero_loc and zero_loc < N)
    #can gap move down?
    down = not (N**2-N <= zero_loc and zero_loc < N**2)

    to_return=[]
    copy_l=copy.copy(state)
    copy_r=copy.copy(state)
    copy_u=copy.copy(state)
    copy_d=copy.copy(state)
    if left:
        copy_l[zero_loc], copy_l[zero_loc-1] = copy_l[zero_loc-1], copy_l[zero_loc]
        to_return.append((copy_l[zero_loc], copy_l))
    if right:
        copy_r[zero_loc], copy_r[zero_loc+1] = copy_r[zero_loc+1], copy_r[zero_loc]
        to_return.append((copy_r[zero_loc], copy_r))
    if up:
        copy_u[zero_loc], copy_u[zero_loc-N] = copy_u[zero_loc-N], copy_u[zero_loc]
        to_return.append((copy_u[zero_loc], copy_u))
    if down:
        copy_d[zero_loc], copy_d[zero_loc+N] = copy_d[zero_loc+N], copy_d[zero_loc]
        to_return.append((copy_d[zero_loc], copy_d))
    return to_return

def IsGoal(state):
    N=round(math.sqrt(len(state)))
    goal = list(range(1,N**2))
    goal.append(0)
    return state == goal


#Checks if config is actually solvable. Generally this method is more efficient
#than BFS or DFS. Add the Manhattan distance of the empty square to bottom right
#corner to the parity of the permutation (when empty square is represented by
#N^2)

def solvable(state):
    N=round(math.sqrt(len(state)))
    zero_loc=state.index(0)
    row=zero_loc // N
    col=zero_loc%N
    manhattan=N-1-row + N-1-col

    state[zero_loc]=N**2
    inversion_ctr=0
    for i in range(N**2):
        for j in range(i+1,N**2):
            inversion_ctr += int(state[i] > state[j])
    invariant=(inversion_ctr + manhattan) % 2
    state[zero_loc]=0
    return invariant % 2 == 0

#Takes a state path (a list of game state tuples) and converts to a sequence of
#tiles to move as strings.
def TileSwap(state_path):
    tiles_to_move=[]
    for i in range(0, len(state_path)-1):
        zero_loc=state_path[i].index(0)
        swapped_with=state_path[i+1][zero_loc]
        tiles_to_move.append(str(swapped_with))
    return tiles_to_move


def BFS(state):
    if not solvable(state):
        print("No path exists")
        return None
    state=tuple(state)
    frontier = [state]
    discovered = set() #former frontier elements
    parents = {state: None}
    while len(frontier) > 0:
        current_state = frontier.pop(0)
        discovered.add(current_state)
        if IsGoal(list(current_state)):
            path=[current_state]
            par=parents[current_state]
            while par != None:
                path.append(par)
                par=parents[par]
            return TileSwap(path[::-1])
        for value_state_tuple in ComputeNeighbors(list(current_state)):
            neighbor=tuple(value_state_tuple[1])
            if neighbor not in discovered and neighbor not in frontier:
                frontier.append(neighbor)
                parents[neighbor] = current_state
    print("Not solvable")
    return None

def DFS(state):
    if not solvable(state):
        print("No path exists")
        return None
    state=tuple(state)
    frontier = [state]
    discovered = set() #former frontier elements
    parents = {state: None}
    while len(frontier) > 0:
        current_state = frontier.pop(0)
        discovered.add(current_state)
        if IsGoal(list(current_state)):
            path=[current_state]
            par=parents[current_state]
            while par != None:
                path.append(par)
                par=parents[par]
            return TileSwap(path[::-1])
        for value_state_tuple in ComputeNeighbors(list(current_state)):
            neighbor=tuple(value_state_tuple[1])
            if neighbor not in discovered and neighbor not in frontier:
                frontier.insert(0,neighbor)
                parents[neighbor] = current_state
    print("Not solvable")
    return None

def BidirectionalSearch(state):
    if not solvable(state):
        print("No path exists")
        return None
    N=round(math.sqrt(len(state)))
    state=tuple(state)
    frontier=[state]
    discovered=set()
    parents={state: None}

    goal=list(range(1,N**2))
    goal.append(0)
    goal=tuple(goal)

    if state == goal:
        return [state]

    frontier_rev=[goal]
    discovered_rev=set()
    parents_rev={goal: None}

    join_point=tuple()

    forward_search=True
    time_to_exit=False

    while True:
        if forward_search:
            current_state=frontier.pop(0)
            discovered.add(current_state)
            for value_state_tuple in ComputeNeighbors(list(current_state)):
                neighbor=tuple(value_state_tuple[1])
                if neighbor not in discovered and neighbor not in frontier:
                    frontier.append(neighbor)
                    parents[neighbor]=current_state
                    if neighbor in frontier_rev:
                        join_point = neighbor
                        time_to_exit=True
        else:
            current_state_rev=frontier_rev.pop(0)
            discovered_rev.add(current_state_rev)
            for value_state_tuple_rev in ComputeNeighbors(list(current_state_rev)):
                neighbor_rev=tuple(value_state_tuple_rev[1])
                if (neighbor_rev not in discovered_rev) and (neighbor_rev not in frontier_rev):
                    frontier_rev.append(neighbor_rev)
                    parents_rev[neighbor_rev]=current_state_rev
                    if neighbor_rev in frontier:
                        join_point = neighbor_rev
                        time_to_exit=True
        if time_to_exit:
            break
        forward_search= not forward_search
    front=[join_point]
    par=parents[join_point]
    while par != None:
        front.append(par)
        par=parents[par]
    front=front[::-1]
    par_rev=parents_rev[join_point]
    while par_rev != None:
        front.append(par_rev)
        par_rev=parents_rev[par_rev]
    return TileSwap(front)

#for each tile, compute manhattan distance from tile position to target position
#add up manhattan distances. heuristic for A*
def manhattan(state):
    #Goes by ordering of numbers in state, not necessarily in order 1, 2, ..., n^2
    N=round(math.sqrt(len(state)))
    total=0
    for i in range(N**2):
        curr_row= i // N
        curr_col=i%N
        if state[i] == 0:
            target_row=N-1
            target_col=N-1
        else:
            target_row=(state[i]-1) // N
            target_col=(state[i]-1) %N
        cell_manhattan=abs(curr_row-target_row) + abs(curr_col-target_col)
        total+=cell_manhattan
    return total

def AStar(state):
    if not solvable(state):
        print("No path exists")
        return None
    state=tuple(state)
    frontier = [(manhattan(state), state)]
    heapq.heapify(frontier)
    discovered = set() #former frontier elements
    parents = {state: None}
    while True:
        priority, current_state = heapq.heappop(frontier)
        discovered.add(current_state)
        if IsGoal(list(current_state)):
            path=[current_state]
            par=parents[current_state]
            while par != None:
                path.append(par)
                par=parents[par]
            return TileSwap(path[::-1])
        for value_state_tuple in ComputeNeighbors(list(current_state)):
            neighbor=tuple(value_state_tuple[1])
            if neighbor not in discovered and neighbor not in frontier:
                heapq.heappush(frontier,(manhattan(neighbor),neighbor))
                parents[neighbor] = current_state
    print("Not solvable")
    return None

# Called from command line like "word_games.py scrabble.txt"
if __name__ == '__main__':
  warnings.filterwarnings("ignore")
  file_path = "/Users/katherinetung/npuzzle/example.txt"

  input = LoadFromFile(file_path)

  if input==None:
      exit()

  print(AStar(input))
