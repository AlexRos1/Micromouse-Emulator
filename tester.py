from emulator import Emulator, BoardLoader, Result
import time
import heapq


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(roboard, start, goal):
    rows = len(roboard)
    cols = len(roboard[0])

    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            return list(reversed(path))

        r, c = current
        for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if roboard[nr][nc] != 1 and roboard[nr][nc] != '*':
                    new_cost = cost_so_far[current] + 1
                    if (nr, nc) not in cost_so_far or new_cost < cost_so_far[(nr, nc)]:
                        cost_so_far[(nr, nc)] = new_cost
                        priority = new_cost + heuristic((nr, nc), goal)
                        heapq.heappush(frontier, (priority, (nr, nc)))
                        came_from[(nr, nc)] = current

    return None


class Robot:
    DIR = ["N", "E", "S", "W"]
    DELTA = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}

    def __init__(self, start_pos=(0, 0), goal_pos=(1, 1), board_size=(10, 10)):
        self.curr_pos = start_pos
        self.start_pos = start_pos
        self.goal_pos = goal_pos
        self.direction = "N"
        self.steps = 0
        self.is_found = False
        self.visited = {start_pos}
        self.command_string = ""
        self.command_index = 0

        rows, cols = board_size
        self.roboard = [['*' for _ in range(cols)] for _ in range(rows)]
        self.roboard[start_pos[0]][start_pos[1]] = "X"

    def find_path(self, board, direction):
        for direction in self.DIR:
            dr, dc = self.DELTA[direction]
            r, c = self.curr_pos
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(self.roboard) and 0 <= nc < len(self.roboard[0]):
                if self.roboard[nr][nc] == "*":
                    if board.is_wall((nr, nc)):
                        self.roboard[nr][nc] = 1
                    elif board.is_goal((nr, nc)):
                        self.roboard[nr][nc] = "G"
                    else:
                        self.roboard[nr][nc] = 0

    def pick_nearest_unvisited(self):
        best_path = None
        best_len = float("inf")

        for r in range(len(self.roboard)):
            for c in range(len(self.roboard[0])):
                if (r, c) not in self.visited and self.roboard[r][c] not in (1, '*'):
                    path = astar(self.roboard, self.curr_pos, (r, c))
                    if path and len(path) < best_len:
                        best_path = path
                        best_len = len(path)

        return best_path

    def path_to_commands(self, path):
        commands = []
        direction = self.direction

        for i in range(len(path) - 1):
            dr = path[i + 1][0] - path[i][0]
            dc = path[i + 1][1] - path[i][1]

            for d, delta in self.DELTA.items():
                if delta == (dr, dc):
                    needed = d
                    break

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

    def fill_path(self, board):
        while True:
            self.find_path(board, self.DIR)
            path = self.pick_nearest_unvisited()
            if path is None:
                break

            for pos in path[1:]:
                self.roboard[self.curr_pos[0]][self.curr_pos[1]] = 0
                self.curr_pos = pos
                self.visited.add(pos)
                self.steps += 1

                if self.roboard[pos[0]][pos[1]] == "G":
                    self.is_found = True
                else:
                    self.roboard[pos[0]][pos[1]] = "X"

                self.find_path(board, self.DIR)

        self.roboard[self.curr_pos[0]][self.curr_pos[1]] = 0

        if self.is_found:
            optimal = astar(self.roboard, self.start_pos, self.goal_pos)
            if optimal:
                return self.path_to_commands(optimal)

        return ""

    def _get_next_pos(self, direction):
        dr, dc = self.DELTA[direction]
        r, c = self.curr_pos
        return r + dr, c + dc

    def can_move_right(self, board):
        right_idx = (self.DIR.index(self.direction) + 1) % 4
        return not board.is_wall(self._get_next_pos(self.DIR[right_idx]))

    def can_move_left(self, board):
        left_idx = (self.DIR.index(self.direction) - 1) % 4
        return not board.is_wall(self._get_next_pos(self.DIR[left_idx]))

    def can_move_forward(self, board):
        return not board.is_wall(self._get_next_pos(self.direction))

    def turn_right(self):
        i = self.DIR.index(self.direction)
        self.direction = self.DIR[(i + 1) % 4]

    def turn_left(self):
        i = self.DIR.index(self.direction)
        self.direction = self.DIR[(i - 1) % 4]

    def move_forward(self, board):
        next_pos = self._get_next_pos(self.direction)
        if not board.is_wall(next_pos):
            self.curr_pos = next_pos
            self.steps += 1

    def string_to_movement(self, board):
        if not self.command_string:
            self.command_string = self.fill_path(board)
            self.command_index = 0

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


class AStarDriver:
    def step(self, robot, board):
        robot.string_to_movement(board)


def main():
    board = BoardLoader.from_file("boards/file.txt")
    rows = len(board.grid)
    cols = len(board.grid[0])
    robot = Robot(board.start, board.goal, (rows, cols))
    driver = AStarDriver()
    emulator = Emulator(board, robot, driver)
    result = emulator.run()
    print(result)
    Result(robot).statusReport()


if __name__ == "__main__":
    main()
