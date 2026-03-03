import time

# ---------------------------------------------------------------------------
# Minimal priority queue (replaces heapq, which is absent in CircuitPython)
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Pre-mapped 10 x 10 maze
#   1 = wall   0 = open cell
#   Start (S): (1, 1)   Goal (G): (8, 8)
#   All border cells are walls, matching the physical maze boundary.
# ---------------------------------------------------------------------------

SIZE  = 10
START = (1, 1)
GOAL  = (8, 8)

MAZE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

DIR   = ["N", "E", "S", "W"]
DELTA = {
    "N": (-1,  0),
    "E": ( 0,  1),
    "S": ( 1,  0),
    "W": ( 0, -1),
}

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# A* pathfinding
# ---------------------------------------------------------------------------

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar():
    frontier = []
    _pq_push(frontier, (0, START))

    came_from   = {START: None}
    cost_so_far = {START: 0}

    while frontier:
        _, current = _pq_pop(frontier)

        if current == GOAL:
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        r, c = current
        for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE and MAZE[nr][nc] != 1:
                new_cost = cost_so_far[current] + 1
                if (nr, nc) not in cost_so_far or new_cost < cost_so_far[(nr, nc)]:
                    cost_so_far[(nr, nc)] = new_cost
                    priority = new_cost + heuristic((nr, nc), GOAL)
                    _pq_push(frontier, (priority, (nr, nc)))
                    came_from[(nr, nc)] = current

    return None

# ---------------------------------------------------------------------------
# Execute a pre-built command string on a robot object
# ---------------------------------------------------------------------------

def solve(commands, robot):
    actions = {
        "F": robot.move_forward,
        "R": robot.turn_right,
        "L": robot.turn_left,
    }
    for cmd in commands:
        actions[cmd]()

# ---------------------------------------------------------------------------
# Path -> robot command string  (F = forward, L = turn left, R = turn right)
# Inspired by Robot.py generate_path()
# ---------------------------------------------------------------------------

def path_to_commands(path):
    if not path:
        return ""

    commands  = []
    direction = "N"   # robot starts facing North

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

# ---------------------------------------------------------------------------
# Main - stress test: compute A* on the pre-mapped maze without moving
# ---------------------------------------------------------------------------

STEP_TIME = 0.7   # seconds per forward move (physical estimate)
TURN_TIME = 1.4   # seconds per 90-degree turn (physical estimate)

print("=" * 42)
print("  MICROMOUSE A* STRESS TEST")
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

    print("Optimal path:")
    print_board(path)

    print("Path cells   :", path)
    print("Commands     :", commands)
    print(f"Cells visited: {len(path)}")
    print(f"Steps  (F)   : {num_steps}")
    print(f"Turns  (R/L) : {num_turns}")
    print(f"A* compute   : {elapsed_ms:.3f} ms")

    print()
    print("=" * 42)
    print("  ESTIMATED PHYSICAL RUN TIME")
    print("=" * 42)
    print(f"  Forward moves : {num_steps:>3}  x {STEP_TIME}s = {num_steps * STEP_TIME:>6.2f}s")
    print(f"  Turns         : {num_turns:>3}  x {TURN_TIME}s = {num_turns * TURN_TIME:>6.2f}s")
    print(f"  {'─' * 36}")
    print(f"  Total         :              {est_time:>6.2f}s")
    print("=" * 42)
