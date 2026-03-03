from romi import Romi
import time
import board
import digitalio
from adafruit_debouncer import Debouncer

pin = digitalio.DigitalInOut(board.IO14)
pin.direction = digitalio.Direction.INPUT
pin.pull = digitalio.Pull.UP
switch = Debouncer(pin)

robot = Romi()
# robot._getStatus()  

# AVAILABLE FUNCTIONS
# moveSquare() - moves 10 inches
# turnRight() - turns 90 degrees
# turnLeft() - turns -90 degrees
# frontWall() - returns 1 if the the front sensor detects a wall in the occupied square

DIR = ["N", "E", "S", "W"]
STACK = []

DELTA = {
    "N": (-1, 0),
    "E": (0, 1),
    "S": (1, 0),
    "W": (0, -1)
}

SIZE = 10
visited = [[False for _ in range(SIZE)] for _ in range(SIZE)]

def create_board():
    b = [["*" for _ in range(10)] for _ in range(10)]
    for i in range(10):
        b[i][9] = "1"
        b[9][i] = "1"
        b[i][0] = "1"
        b[0][i] = "1"
    return b

def print_board(b):
    print()
    for r in b:
        print(" ".join(r))
    print()

maze = create_board()

start_r = 1
start_c = 1
row = start_r
col = start_c

direction = 0  # 0 is starting N, 1 is E...

#Temporary Solution
def is_left():
    print("Turning Left")
    robot.turnLeft()
    result = robot.frontWall() == 1   
    if result:
        print("I see a wall")
    print("Return Straight")
    robot.turnRight()
    time.sleep(2)
    return result
    
  #Temporary Solution  
def is_right():
    print("Turning Right")
    robot.turnRight()
    result = robot.frontWall() == 1   
    if result:
        print("I see a wall")
    print("Return Straight")
    robot.turnLeft()
    time.sleep(2)
    return result
    
#Temporary Solution
def detect_walls():
    global row, col, direction

    print(f"[detect_walls] At ({row}, {col}), facing {DIR[direction]}")
    front = robot.frontWall()
    left = is_left()
    right = is_right()
    print(f"[detect_walls] Results - front: {bool(front)}, left: {bool(left)}, right: {bool(right)}")

	#When we add sensors, delete function

    # FRONT
    if front:
        dr, dc = DELTA[DIR[direction]]
        nr = row + dr
        nc = col + dc
        if 0 <= nr < SIZE and 0 <= nc < SIZE:
            print(f"[detect_walls] Wall detected FRONT at ({nr}, {nc})")
            maze[nr][nc] = "1"

    # LEFT
    left_dir = (direction - 1) % 4
    if left:
        dr, dc = DELTA[DIR[left_dir]]
        nr = row + dr
        nc = col + dc
        if 0 <= nr < SIZE and 0 <= nc < SIZE:
            print(f"[detect_walls] Wall detected LEFT at ({nr}, {nc})")
            maze[nr][nc] = "1"

    # RIGHT
    right_dir = (direction + 1) % 4
    if right:
        dr, dc = DELTA[DIR[right_dir]]
        nr = row + dr
        nc = col + dc
        if 0 <= nr < SIZE and 0 <= nc < SIZE:
            print(f"[detect_walls] Wall detected RIGHT at ({nr}, {nc})")
            maze[nr][nc] = "1"
            
def turn_to(new_dir):
    global direction
    print(f"[turn_to] Turning from {DIR[direction]} to {DIR[new_dir]}")
    # Turn right until facing new_dir
    while direction != new_dir:
        robot.turnRight()  # only allowed turn function
        direction = (direction + 1) % 4
        print(f"[turn_to] Now facing {DIR[direction]}")
        time.sleep(0.1)
    print(f"[turn_to] Reached target direction {DIR[direction]}")

def move_forward():
    global row, col
    print(f"[move_forward] Moving from ({row}, {col}) facing {DIR[direction]}")
    robot.moveSquare()
    dr, dc = DELTA[DIR[direction]]
    row += dr
    col += dc
    print(f"[move_forward] Arrived at ({row}, {col})")
    time.sleep(0.5)
    
def explore():
    global row, col

    print(f"[explore] Visiting ({row}, {col}), stack depth: {len(STACK)}")
    visited[row][col] = True
    maze[row][col] = "V"
    print_board(maze)

    detect_walls()

    for new_dir in range(4):

        dr, dc = DELTA[new_dir]
        new_r = row + dr
        new_c = col + dc

        if maze[new_r][new_c] == "1":
            print(f"[explore] Skipping direction {DIR[new_dir]}: wall at ({new_r}, {new_c})")
            continue

        if visited[new_r][new_c]:
            print(f"[explore] Skipping direction {DIR[new_dir]}: already visited ({new_r}, {new_c})")
            continue

        print(f"[explore] Going {DIR[new_dir]} to ({new_r}, {new_c})")
        stack.append((row, col))

        turn_to(new_dir)
        move_forward()

        explore()

        prev_r, prev_c = stack.pop()
        print(f"[explore] Backtracking to ({prev_r}, {prev_c})")

        for d in range(4):
            if row + DELTA[d][0] == prev_r and col + DELTA[d][1] == prev_c:
                turn_to(d)
                break

        move_forward()
    print(f"[explore] Done exploring from ({row}, {col})")
    
while True:
    switch.update()
    if switch.fell:
        print("Beginning Exploration")
        maze[row][col] = "X"
        print_board(maze)
        explore()
        print("Exploration Complete")
        print_board(maze)
    time.sleep(0.01)

