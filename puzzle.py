import collections
import numpy as np
import copy
import warnings
import math

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
    copy_l=copy.deepcopy(state)
    copy_r=copy.deepcopy(state)
    copy_u=copy.deepcopy(state)
    copy_d=copy.deepcopy(state)
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

"""
#Converts a list of lists into a tuple of tuples.
def nested_tuple(nested_list):
    outer_tuple=[]
    for i in nested_list:
        i=tuple(i)
        outer_tuple.append(i)
    return tuple(outer_tuple)

#Converts a tuple of tuples into a list of lists.
def nested_list(nested_tuple):
    outer_list=[]
    for i in nested_tuple:
        i=list(i)
        outer_list.append(i)
    return outer_list"""

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
    """print("Inversion counter")
    print(inversion_ctr)
    print("Manhattan")
    print(manhattan)"""
    invariant=(inversion_ctr + manhattan) % 2
    state[zero_loc]=0
    """print("Invariant")
    print(invariant)"""
    return invariant % 2 == 0



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
            return path[::-1]
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
            return path[::-1]
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
            """print("frontier")
            print(frontier)"""
            current_state=frontier.pop(0)
            """print('current state')
            print(current_state)"""
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
            """print("frontier reverse")
            print(frontier_rev)"""
            current_state_rev=frontier_rev.pop(0)
            """print("current state rev")
            print(current_state_rev)"""
            discovered_rev.add(current_state_rev)
            """print("neighbors")
            print(ComputeNeighbors(list(current_state_rev)))"""
            for value_state_tuple_rev in ComputeNeighbors(list(current_state_rev)):
                neighbor_rev=tuple(value_state_tuple_rev[1])
                """print("considered neighbor")
                print(neighbor_rev)
                print("discovered")
                print(discovered_rev)
                print("frontier rev")
                print(frontier_rev)
                print((neighbor_rev not in discovered_rev))
                print((neighbor_rev not in frontier_rev))"""
                if (neighbor_rev not in discovered_rev) and (neighbor_rev not in frontier_rev):
                    frontier_rev.append(neighbor_rev)
                    parents_rev[neighbor_rev]=current_state_rev
                    if neighbor_rev in frontier:
                        join_point = neighbor_rev
                        time_to_exit=True
        if time_to_exit:
            break
        forward_search= not forward_search
    #print(join_point)
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
    return front

# Called from command line like "word_games.py scrabble.txt"
if __name__ == '__main__':
  warnings.filterwarnings("ignore")
  file_path = "/Users/katherinetung/npuzzle/example.txt"

  input = LoadFromFile(file_path)

  #print(input)
  #DebugPrint(input)
  #print(ComputeNeighbors(input))
  #print(solvable(input))
  #print(BFS(input))
  print(BidirectionalSearch(input))
  #print(solvable(input))
  #print(input)
  #print(IsGoal(input))
  #print(DFS(input))
  #print(ComputeNeighbors(input))
