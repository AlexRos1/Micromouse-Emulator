import time

# Minimal priority queue (replaces heapq, which is absent in CircuitPython)

def _pq_push(pq, item):
    pq.append(item)

def _pq_pop(pq):
    min_idx = 0
    for i in range(1, len(pq)):
        if pq[i][0] < pq[min_idx][0]:
            min_idx = i
    item = pq[min_idx]
    pq[min_idx] = pq[-1]
    pq.pop()
    return item

SIZE  = 12
START = (1, 1)
GOAL  = (5, 6)

MAZE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

DIR   = ["N", "E", "S", "W"]
DELTA = {
    "N": (-1,  0),
    "E": ( 0,  1),
    "S": ( 1,  0),
    "W": ( 0, -1),
}

START_DIR = "S"               # robot starts facing South
STEP_TIME = 0.7               # seconds per forward move (physical estimate)
TURN_TIME = 1.4               # seconds per 90-degree turn (physical estimate)

def print_board(path=None):
    path_set = set(path) if path else set()
    print()
    for r in range(SIZE):
        row_str = ""
        for c in range(SIZE):
            if (r, c) == START:
                row_str += "S "
            elif (r, c) == GOAL:
                row_str += "G "
            elif (r, c) in path_set:
                row_str += ". "
            elif MAZE[r][c] == 1:
                row_str += "# "
            else:
                row_str += "  "
        print(row_str)
    print()

def _turns_needed(from_dir, to_dir):
    """Minimum 90-degree turns to rotate from *from_dir* to *to_dir*."""
    ci = DIR.index(from_dir)
    ni = DIR.index(to_dir)
    return min((ni - ci) % 4, (ci - ni) % 4)

def heuristic(pos, goal):
    """Admissible time heuristic -- every remaining cell costs at least STEP_TIME."""
    return (abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])) * STEP_TIME

def astar():
    """A* over (row, col, facing) states so turn cost is part of the search."""
    start_state = (START[0], START[1], START_DIR)
    frontier = []
    _pq_push(frontier, (0, start_state))

    came_from   = {start_state: None}
    cost_so_far = {start_state: 0}

    while frontier:
        _, current = _pq_pop(frontier)

        r, c, facing = current

        if (r, c) == GOAL:
            path = []
            while current is not None:
                path.append((current[0], current[1]))
                current = came_from[current]
            path.reverse()
            return path

        for d, (dr, dc) in DELTA.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE and MAZE[nr][nc] != 1:
                turns     = _turns_needed(facing, d)
                move_cost = turns * TURN_TIME + STEP_TIME
                new_cost  = cost_so_far[current] + move_cost
                next_state = (nr, nc, d)
                if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                    cost_so_far[next_state] = new_cost
                    priority = new_cost + heuristic((nr, nc), GOAL)
                    _pq_push(frontier, (priority, next_state))
                    came_from[next_state] = current

    return None

def solve(commands, robot):
    actions = {
        "F": robot.move_forward,
        "R": robot.turn_right,
        "L": robot.turn_left,
    }
    for cmd in commands:
        actions[cmd]()

def path_to_commands(path):
    if not path:
        return ""

    commands  = []
    direction = "S"   # robot starts facing South

    for i in range(len(path) - 1):
        dr = path[i + 1][0] - path[i][0]
        dc = path[i + 1][1] - path[i][1]

        needed = next(d for d, delta in DELTA.items() if delta == (dr, dc))

        while direction != needed:
            ci = DIR.index(direction)
            ni = DIR.index(needed)
            if (ni - ci) % 4 <= (ci - ni) % 4:
                commands.append("R")
                direction = DIR[(ci + 1) % 4]
            else:
                commands.append("L")
                direction = DIR[(ci - 1) % 4]

        commands.append("F")

    return "".join(commands)

# Main

print("=" * 42)
print("  MICROMOUSE TIME-BASED A* STRESS TEST")
print("  Pre-mapped maze -- no movement")
print("=" * 42)

print("\nMaze layout:")
print_board()

t0   = time.monotonic()
path = astar()
t1   = time.monotonic()

elapsed_ms = (t1 - t0) * 1000

if path is None:
    print("ERROR: No path found from", START, "to", GOAL)
else:
    commands  = path_to_commands(path)
    num_steps = commands.count("F")
    num_turns = commands.count("R") + commands.count("L")
    est_time  = num_steps * STEP_TIME + num_turns * TURN_TIME

    print("Time-optimal path:")
    print_board(path)

    #print("Path cells   :", path)
    print("Commands     :", commands)
    print(f"Cells visited: {len(path)}")
    print(f"Steps  (F)   : {num_steps}")
    print(f"Turns  (R/L) : {num_turns}")
    print(f"A* compute   : {elapsed_ms:.3f} ms")

    print("=" * 42)
    print("  ESTIMATED PHYSICAL RUN TIME")
    print("=" * 42)
    print(f"  Forward moves : {num_steps:>3}  x {STEP_TIME}s = {num_steps * STEP_TIME:>6.2f}s")
    print(f"  Turns         : {num_turns:>3}  x {TURN_TIME}s = {num_turns * TURN_TIME:>6.2f}s")
    print(f"  {'─' * 36}")
    print(f"  Total         :              {est_time:>6.2f}s")
    print("=" * 42)

