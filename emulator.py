import time
import os

class Emulator:
    def __init__(self, board, robot, driver, live_run=False):
        self.board = board
        self.driver = driver
        self.robot = robot
        self.live_run = live_run
    
    def run(self, live_run=False):
        if live_run == False:
            for step in range(1000):
                if self.board.is_goal(self.robot.curr_pos):
                    return "SUCCESS"
                prev = self.robot.curr_pos
                self.driver.step(self.robot, self.board)
                if self.robot.curr_pos != prev:
                    os.system("cls" if os.name == "nt" else "clear")
                    self.board.printBoard(self.robot)
                    time.sleep(0.1)
            return "FAILED (loop)"
        else:
            for _ in range(1000):
                if self.board.is_goal(self.robot.curr_pos):
                    return "SUCCESS"
                self.driver.step(self.robot, self.board)
            return "FAILED (loop)"


class Board:
    def __init__(self, grid, start, goal):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.size = len(grid) * len(grid[0]) if grid else 0

    def is_wall(self, pos):
        row, col = pos
        if row < 0 or row >= len(self.grid) or col < 0 or col >= len(self.grid[0]):
            return True
        return self.grid[row][col] == 1

    def is_goal(self, pos):
        return pos == self.goal

    def printBoard(self, robot):
        print("\n" + "-" * 30)
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                
                if (i, j) == robot.curr_pos:
                    print("*", end="")
                elif (i, j) == self.goal:
                    print("G", end="")
                elif cell == 1:
                    print("1", end="")
                else:
                    print(" ", end="")
            print()
        print("-" * 30)


class BoardLoader:
    @staticmethod
    def from_file(filename):
        grid = []
        start = None
        goal = None
        with open(filename, "r") as f:
            lines = f.readlines()
            lines = [line.rstrip("\n") for line in lines]
            maze_2d = [list(line) for line in lines]
            
            for i, row in enumerate(maze_2d):
                for j, char in enumerate(row):
                    if char == 'S':
                        start = (i, j)
                        maze_2d[i][j] = " "  
                    elif char == 'G':
                        goal = (i, j)
                        maze_2d[i][j] = " " 
                    elif char in ('|', '+', '-', '#'):
                        maze_2d[i][j] = 1
                    else:
                        maze_2d[i][j] = " "
        
        if start is None:
            raise ValueError(f"No start position 'S' found in {filename}")
        if goal is None:
            raise ValueError(f"No goal position 'G' found in {filename}")

        return Board(maze_2d, start, goal)


class RightHandDriver:
    def step(self, robot, board):
        if robot.can_move_right(board):
            robot.turn_right()
            robot.move_forward(board)
        elif robot.can_move_forward(board):
            robot.move_forward(board)
        else:
            robot.turn_left()
''' 
def FloodFillDriver:
    def step(ste)
'''

class LeftHandDriver:
    def step(self, robot, board):
        if robot.can_move_left(board):
            robot.turn_left()
            robot.move_forward(board)
        elif robot.can_move_forward(board):
            robot.move_forward(board)
        else:
            robot.turn_right()


class RandomDriver:
    import random
    
    def step(self, robot, board):
        
        possible_moves = []
        
        if robot.can_move_forward(board):
            possible_moves.append('forward')
        if robot.can_move_right(board):
            possible_moves.append('right')
        if robot.can_move_left(board):
            possible_moves.append('left')
        
        if not possible_moves:
            robot.turn_right()
            robot.turn_right() 
            return
        
        import random
        choice = random.choice(possible_moves)
        
        if choice == 'forward':
            robot.move_forward(board)
        elif choice == 'right':
            robot.turn_right()
            robot.move_forward(board)
        elif choice == 'left':
            robot.turn_left()
            robot.move_forward(board)

'''
class Robot:
    DIR = ["N", "E", "S", "W"]
    DELTA = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}

    def __init__(self, start_pos=(0,0), goal_pos=(1,1), board_size=[10,10]):
        self.curr_pos = start_pos
        self.goal_pos = goal_pos
        self.direction = "S"  
        self.is_found = False
        self.steps = 0
        self.board_size = board_size
        
        
        rows, cols = board_size
        self.roboard = [['*' for _ in range(cols)] for _ in range(rows)]
        
        start_row, start_col = start_pos
        self.roboard[start_row][start_col] = "X"
        
    def get_next_pos(self, board, direction): 
        dr, dc = self.DELTA[direction]
        row, col = self.curr_pos
        return (row+dr, col+dc)
    
    def find_path(self, board, direction): 
        for dir in self.DIR:
            dr, dc = self.DELTA[direction]
            row, col = self.curr_pos
            next_pos = [(dr+row), (dc+col)]
            next_row, next_col = next_pos
        
            if 0 <= next_row < len(self.roboard) and 0 <= next_col < len(self.roboard[0]):
                if self.roboard[next_row][next_col] == "*": 
    
    #This value will need to change in response to a real board.
    #This is where there will be an is_wall function that will
    #return a value and create the board   
                 
                    if board.is_wall(next_pos):
                        self.roboard[next_row][next_col] = 1
                    elif board.is_goal(next_pos):
                        self.roboard[next_row][next_col] = "G"
                    else:
                        self.roboard[next_row][next_col] = 0
            
    def printRoboard(self, roboard):
        self.roboard = roboard
        rows = len(roboard)
        col = len(rows)
        
        for i in range(rows):
            for c in range(col):
                print(self.roboard[i][c], end = "")
            print()
    
    def _get_next_pos(self, direction):
        dr, dc = self.DELTA[direction]
        row, col = self.curr_pos
        return (row + dr, col + dc)

    def can_move_right(self, board):
        right_idx = (self.DIR.index(self.direction) + 1) % 4
        right_dir = self.DIR[right_idx]
        next_pos = self._get_next_pos(right_dir)
        return not board.is_wall(next_pos)

    def can_move_left(self, board):
        left_idx = (self.DIR.index(self.direction) - 1) % 4
        left_dir = self.DIR[left_idx]
        next_pos = self._get_next_pos(left_dir)
        return not board.is_wall(next_pos)

    def can_move_forward(self, board):
        next_pos = self._get_next_pos(self.direction)
        return not board.is_wall(next_pos)

    def turn_right(self):
        idx = self.DIR.index(self.direction)
        self.direction = self.DIR[(idx + 1) % 4]

    def turn_left(self):
        idx = self.DIR.index(self.direction)
        self.direction = self.DIR[(idx - 1) % 4]

    def move_forward(self, board):
        next_pos = self._get_next_pos(self.direction)
        if not board.is_wall(next_pos):
            self.curr_pos = next_pos
            self.steps += 1
            return True
        return False
'''
class Result:
    def __init__(self, robot):
        self.robot = robot

    def statusReport(self):
        print(f"Final position: {self.robot.curr_pos}")
        print(f"Total steps: {self.robot.steps}")
        print(f"Final direction: {self.robot.direction}")


def run_simulation(board_file, driver_class, board_name, driver_name):
    print(f"\n--- {board_name} Board | {driver_name} ---")
    try:
        board = BoardLoader.from_file(board_file)
        robot = Robot(board.start, board.goal)
        driver = driver_class()
        emulator = Emulator(board, robot, driver)
        result = emulator.run()
        print(f"Result: {result}")
        result_obj = Result(robot)
        result_obj.statusReport()
        print()
    except FileNotFoundError:
        print(f"Error: Board file '{board_file}' not found!")
    except Exception as e:
        print(f"Error running simulation: {e}")


def main():
    board = BoardLoader.from_file("boards/file.txt")
    robot = Robot(board.start, board.goal)
    driver = RightHandDriver()
    emulator = Emulator(board, robot, driver)
    result = emulator.run()
    print(result)
    result_obj = Result(robot)
    result_obj.statusReport()


if __name__ == "__main__":
    main()