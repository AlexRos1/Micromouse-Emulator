from Emulator import *
import heapq


# ---------------------------------------------------------------------------
# A* helpers  (time-based: turns cost TURN_TIME, forward costs STEP_TIME)
# ---------------------------------------------------------------------------

STEP_TIME = 0.7   # seconds per forward move
TURN_TIME = 1.4   # seconds per 90-degree turn

_DIR   = ["N", "E", "S", "W"]
_DELTA = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}


def _turns_needed(from_dir, to_dir):
    """Minimum 90-degree turns to rotate from *from_dir* to *to_dir*."""
    ci = _DIR.index(from_dir)
    ni = _DIR.index(to_dir)
    return min((ni - ci) % 4, (ci - ni) % 4)


def heuristic(pos, goal):
    """Admissible time heuristic -- every remaining cell costs at least STEP_TIME."""
    return (abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])) * STEP_TIME


def astar(grid, start, goal, start_dir="N"):
    """A* over (row, col, facing) states so turn cost is part of the search."""
    rows = len(grid)
    cols = len(grid[0])

    start_state = (start[0], start[1], start_dir)
    frontier = []
    heapq.heappush(frontier, (0, start_state))

    came_from   = {start_state: None}
    cost_so_far = {start_state: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        r, c, facing = current

        if (r, c) == goal:
            path = []
            while current is not None:
                path.append((current[0], current[1]))
                current = came_from[current]
            return list(reversed(path))

        for d, (dr, dc) in _DELTA.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 1:
                turns     = _turns_needed(facing, d)
                move_cost = turns * TURN_TIME + STEP_TIME
                new_cost  = cost_so_far[current] + move_cost
                next_state = (nr, nc, d)
                if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                    cost_so_far[next_state] = new_cost
                    priority = new_cost + heuristic((nr, nc), goal)
                    heapq.heappush(frontier, (priority, next_state))
                    came_from[next_state] = current

    return None


# ---------------------------------------------------------------------------
# Robot
# ---------------------------------------------------------------------------

class Robot:
    DIR   = ["N", "E", "S", "W"]
    DELTA = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}

    def __init__(self, start_pos, goal_pos, board_size):
        self.curr_pos  = start_pos
        self.start_pos = start_pos
        self.goal_pos  = goal_pos
        self.direction = "N"

        # movement counters used by Result.timeReport()
        self.steps = 0   # forward moves
        self.turns = 0   # 90-degree turns (logged by reactive drivers)

        # A* pre-computed command string
        self.command_string = ""
        self.command_index  = 0
        self.board_size     = board_size

    # ------------------------------------------------------------------
    # A* path generation
    # ------------------------------------------------------------------

    def generate_path(self, board):
        path = astar(board.grid, self.start_pos, self.goal_pos, self.direction)
        if not path:
            return ""

        commands  = []
        direction = self.direction

        for i in range(len(path) - 1):
            dr = path[i + 1][0] - path[i][0]
            dc = path[i + 1][1] - path[i][1]

            needed = next(d for d, delta in self.DELTA.items() if delta == (dr, dc))

            while direction != needed:
                ci = self.DIR.index(direction)
                ni = self.DIR.index(needed)
                if (ni - ci) % 4 <= (ci - ni) % 4:
                    commands.append("R")
                    direction = self.DIR[(ci + 1) % 4]
                else:
                    commands.append("L")
                    direction = self.DIR[(ci - 1) % 4]

            commands.append("F")

        return "".join(commands)

    def execute_next(self, board):
        if not self.command_string:
            self.command_string = self.generate_path(board)
            self.command_index  = 0

        if self.command_index >= len(self.command_string):
            return

        cmd = self.command_string[self.command_index]
        self.command_index += 1

        if cmd == "F":
            self.move_forward(board)
        elif cmd == "R":
            self.turn_right()
        elif cmd == "L":
            self.turn_left()

    # ------------------------------------------------------------------
    # Primitive actions
    # ------------------------------------------------------------------

    def _get_next_pos(self, direction):
        dr, dc = self.DELTA[direction]
        r, c   = self.curr_pos
        return r + dr, c + dc

    def move_forward(self, board):
        next_pos = self._get_next_pos(self.direction)
        if not board.is_wall(next_pos):
            self.curr_pos = next_pos
            self.steps   += 1

    def turn_right(self):
        i              = self.DIR.index(self.direction)
        self.direction = self.DIR[(i + 1) % 4]
        self.turns    += 1          # log every 90-degree turn

    def turn_left(self):
        i              = self.DIR.index(self.direction)
        self.direction = self.DIR[(i - 1) % 4]
        self.turns    += 1          # log every 90-degree turn

    # ------------------------------------------------------------------
    # Sensing helpers
    # ------------------------------------------------------------------

    def can_move_forward(self, board):
        return not board.is_wall(self._get_next_pos(self.direction))

    def can_move_right(self, board):
        i = (self.DIR.index(self.direction) + 1) % 4
        return not board.is_wall(self._get_next_pos(self.DIR[i]))

    def can_move_left(self, board):
        i = (self.DIR.index(self.direction) - 1) % 4
        return not board.is_wall(self._get_next_pos(self.DIR[i]))


# ---------------------------------------------------------------------------
# A* driver
# ---------------------------------------------------------------------------

class AStarDriver:
    def step(self, robot, board):
        robot.execute_next(board)