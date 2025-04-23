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
maze = {}
pos = (0, 0)
direction = "UP"  # UP, DOWN, LEFT, RIGHT
path_history = []
last_scan_time = utime.ticks_ms()

# Reduced speed (original was 30000)
def set_speed(speed=15000):  # Reduced speed by 50%
    ENA.duty_u16(speed)
    ENB.duty_u16(speed)

# Movement functions
def move_forward():
    global pos, path_history
    IN1.low()
    IN2.high()
    IN3.low()
    IN4.high()
    
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
    IN1.high()
    IN2.low()
    IN3.low()
    IN4.high()
    utime.sleep(0.8)  # Increased turn time for reduced speed
    stop()
    
    # Update direction
    dir_map = {"UP": "LEFT", "LEFT": "DOWN", "DOWN": "RIGHT", "RIGHT": "UP"}
    direction = dir_map[direction]

def turn_right():
    global direction
    IN1.low()
    IN2.high()
    IN3.high()
    IN4.low()
    utime.sleep(0.8)  # Increased turn time for reduced speed
    stop()
    
    # Update direction
    dir_map = {"UP": "RIGHT", "RIGHT": "DOWN", "DOWN": "LEFT", "LEFT": "UP"}
    direction = dir_map[direction]

def stop():
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
    
    timeout = 25000  # microseconds (25ms)
    start = utime.ticks_us()
    
    # Wait for echo to go high
    while echo.value() == 0 and utime.ticks_diff(utime.ticks_us(), start) < timeout:
        pass
    
    if echo.value() == 0:
        return -1  # Timeout
    
    echo_start = utime.ticks_us()
    
    # Wait for echo to go low
    while echo.value() == 1 and utime.ticks_diff(utime.ticks_us(), start) < timeout:
        pass
    
    if echo.value() == 1:
        return -1  # Timeout
    
    echo_end = utime.ticks_us()
    
    duration = echo_end - echo_start
    distance = (duration * 0.0343) / 2  # cm
    return distance if distance > 0 else -1

def move_servo(angle):
    servo.duty_u16(angle)
    utime.sleep(0.5)  # Increased stabilization time for more accurate readings

def scan_surroundings():
    global last_scan_time
    current_time = utime.ticks_ms()
    
    # Only scan every 1000ms to allow proper servo movement and distance measurement
    if utime.ticks_diff(current_time, last_scan_time) < 1000:
        return None
    
    last_scan_time = current_time
    surroundings = {}
    
    # Front check with extra measurement time
    move_servo(FRONT)
    utime.sleep(0.8)  # Additional stabilization
    surroundings['front'] = get_distance()
    
    # Always scan sides (regardless of front distance) but with proper timing
    move_servo(LEFT)
    utime.sleep(0.8)  # Additional stabilization
    surroundings['left'] = get_distance()
    
    move_servo(RIGHT)
    utime.sleep(0.8)  # Additional stabilization
    surroundings['right'] = get_distance()
    
    move_servo(FRONT)  # Return to front
    utime.sleep(0.8)  # Additional stabilization
    
    return surroundings

def choose_direction(surroundings):
    if not surroundings:
        return 'forward'
    
    # Threshold distance (in cm)
    threshold = 20
    
    # Always prefer forward if clear
    if surroundings.get('front', 0) > threshold or surroundings.get('front', -1) == -1:
        return 'forward'
    
    # Then check sides
    options = []
    if surroundings.get('left', 0) > threshold:
        options.append(('left', maze.get(get_new_position(pos, direction_from_move('left')), {'visits': 0})))
    if surroundings.get('right', 0) > threshold:
        options.append(('right', maze.get(get_new_position(pos, direction_from_move('right')), {'visits': 0})))
    
    if not options:
        return None  # No options
    
    # Choose least visited option
    options.sort(key=lambda x: x[1]['visits'])
    return options[0][0]

def direction_from_move(move):
    dir_map = {
        'UP': {'left': 'LEFT', 'right': 'RIGHT', 'forward': 'UP'},
        'LEFT': {'left': 'DOWN', 'right': 'UP', 'forward': 'LEFT'},
        'DOWN': {'left': 'RIGHT', 'right': 'LEFT', 'forward': 'DOWN'},
        'RIGHT': {'left': 'UP', 'right': 'DOWN', 'forward': 'RIGHT'}
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

def solve_maze():
    set_speed()  # Using the reduced speed
    move_servo(FRONT)
    
    while True:
        # Continue moving forward while scanning
        move_forward()
        
        # Get surroundings with proper timing
        surroundings = scan_surroundings()
        
        if surroundings:
            print(f"Position: {pos}, Direction: {direction}")
            print(f"Surroundings: Front: {surroundings['front']}cm, Left: {surroundings['left']}cm, Right: {surroundings['right']}cm")
            
            decision = choose_direction(surroundings)
            
            if decision == 'left':
                print("Turning left")
                turn_left()
            elif decision == 'right':
                print("Turning right")
                turn_right()
            elif decision is None:  # Dead end
                print("Backtracking...")
                turn_left()
                turn_left()  # 180 degree turn
                
        utime.sleep(0.2)  # Increased delay to reduce MCU load

# Start solving
solve_maze()