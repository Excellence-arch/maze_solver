from machine import Pin, PWM
import utime

# Motor control pins (L298N)
IN1 = Pin(14, Pin.OUT)  # Motor A
IN2 = Pin(15, Pin.OUT)
IN3 = Pin(12, Pin.OUT)  # Motor B
IN4 = Pin(13, Pin.OUT)

ENA = PWM(Pin(16))  # PWM for speed control
ENB = PWM(Pin(17))

# Servo for ultrasonic sensor (MG996R)
servo = PWM(Pin(0))  
servo.freq(50)

# Ultrasonic sensor pins
trig = Pin(3, Pin.OUT)
echo = Pin(4, Pin.IN)

# Servo positions (duty cycle values)
FRONT = 4400
LEFT = 7500
RIGHT = 1200

# Maze tracking
maze = {}  # Stores visited positions and directions tried
pos = (0, 0)  # Current (x, y) position
direction = "UP"  # UP, DOWN, LEFT, RIGHT
path_history = []  # Tracks the path taken for backtracking

# Speed Control
def set_speed(speed=15000):
    ENA.duty_u16(speed)
    ENB.duty_u16(speed)

# Movement functions
def backward():
    set_speed()
    IN1.high()
    IN2.low()
    IN3.high()
    IN4.low()
    utime.sleep(0.5)
    stop()

def forward():
    global pos, path_history
    set_speed()
    IN1.low()
    IN2.high()
    IN3.low()
    IN4.high()
    utime.sleep(0.5)  # Move forward a fixed distance
    stop()
    
    # Update position
    x, y = pos
    if direction == "UP":
        pos = (x, y + 1)
    elif direction == "DOWN":
        pos = (x, y - 1)
    elif direction == "LEFT":
        pos = (x - 1, y)
    elif direction == "RIGHT":
        pos = (x + 1, y)
    
    # Update maze tracking
    if pos not in maze:
        maze[pos] = {'visits': 1, 'directions': [direction]}
    else:
        maze[pos]['visits'] += 1
        if direction not in maze[pos]['directions']:
            maze[pos]['directions'].append(direction)
    
    path_history.append((pos, direction))

def turn_left():
    global direction
    set_speed()
    IN1.high()
    IN2.low()
    IN3.low()
    IN4.high()
    utime.sleep(0.5)
    stop()
    # Update direction
    if direction == "UP":
        direction = "LEFT"
    elif direction == "LEFT":
        direction = "DOWN"
    elif direction == "DOWN":
        direction = "RIGHT"
    elif direction == "RIGHT":
        direction = "UP"

def turn_right():
    global direction
    set_speed()
    IN1.low()
    IN2.high()
    IN3.high()
    IN4.low()
    utime.sleep(0.5)
    stop()
    # Update direction
    if direction == "UP":
        direction = "RIGHT"
    elif direction == "RIGHT":
        direction = "DOWN"
    elif direction == "DOWN":
        direction = "LEFT"
    elif direction == "LEFT":
        direction = "UP"

def stop():
    ENA.duty_u16(0)
    ENB.duty_u16(0)
    IN1.low()
    IN2.low()
    IN3.low()
    IN4.low()

def get_distance():
    trig.low()
    utime.sleep_us(2)
    trig.high()
    utime.sleep_us(10)
    trig.low()
    
    while echo.value() == 0:
        signal_off = utime.ticks_us()
    while echo.value() == 1:
        signal_on = utime.ticks_us()
    
    time_passed = signal_on - signal_off
    return (time_passed * 0.0343) / 2

def move_servo(angle):
    servo.duty_u16(angle)
    utime.sleep(0.3)  # Reduced stabilization time

def scan(direction_angle):
    stop()  # Stop motors before scanning
    move_servo(direction_angle)
    distance = get_distance()
    move_servo(FRONT)
    return distance

def get_available_moves():
    moves = {}
    # Always check front first
    move_servo(FRONT)
    front_dist = get_distance()
    moves['front'] = front_dist
    
    # Only check sides if front is blocked
    if front_dist < 15:
        moves['left'] = scan(LEFT)
        moves['right'] = scan(RIGHT)
    
    return moves

def choose_direction(moves):
    # If front is clear and not over-visited
    if moves['front'] > 15:
        if pos not in maze or direction not in maze[pos]['directions']:
            return 'front'
        elif maze[pos]['visits'] < 2:
            return 'front'
    
    # Evaluate alternatives
    possible = [d for d, dist in moves.items() if dist > 15]
    if not possible:
        return None
    
    # Prefer untried directions
    current = maze.get(pos, {'directions': []})
    untried = [d for d in possible if direction_from_move(d) not in current['directions']]
    if untried:
        return untried[0]
    
    # Otherwise choose least visited
    visit_counts = {}
    for d in possible:
        new_dir = direction_from_move(d)
        new_pos = get_new_position(pos, new_dir)
        visit_counts[d] = maze.get(new_pos, {'visits': 0})['visits']
    return min(possible, key=lambda x: visit_counts[x])

def direction_from_move(move):
    if move == 'front':
        return direction
    dir_map = {
        'UP': {'left': 'LEFT', 'right': 'RIGHT'},
        'LEFT': {'left': 'DOWN', 'right': 'UP'},
        'DOWN': {'left': 'RIGHT', 'right': 'LEFT'},
        'RIGHT': {'left': 'UP', 'right': 'DOWN'}
    }
    return dir_map[direction][move]

def get_new_position(current_pos, dir):
    x, y = current_pos
    if dir == "UP":
        return (x, y + 1)
    elif dir == "DOWN":
        return (x, y - 1)
    elif dir == "LEFT":
        return (x - 1, y)
    elif dir == "RIGHT":
        return (x + 1, y)

def backtrack():
    global pos, direction, path_history
    if not path_history:
        return False
    
    prev_pos, prev_dir = path_history.pop()
    while direction != prev_dir:
        turn_left()
    turn_left()
    turn_left()
    forward()
    pos = prev_pos
    return True

def solve_maze():
    move_servo(FRONT)
    
    while True:
        moves = get_available_moves()
        print(f"Position: {pos}, Direction: {direction}")
        print(f"Available moves: {moves}")
        
        best_move = choose_direction(moves)
        if best_move is None:
            print("Backtracking...")
            if not backtrack():
                print("Maze unsolvable")
                break
            continue
        
        if best_move == 'left':
            turn_left()
        elif best_move == 'right':
            turn_right()
        
        forward()
        
        if maze[pos]['visits'] > 3:
            print("Loop detected")
            break

solve_maze()