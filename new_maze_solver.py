from machine import Pin, PWM, time_pulse_us
import heapq
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

# Maze tracking
maze = {}  # Stores visited positions {(x, y): visit_count}
pos = [0, 0]  # Current (x, y) position
direction = "UP"  # UP, DOWN, LEFT, RIGHT

# Speed Control
def set_speed(speed=30000): 
    ENA.duty_u16(speed)
    ENB.duty_u16(speed)

# Movement functions
def backward():
    set_speed()
    IN1.high()
    IN2.low()
    IN3.high()
    IN4.low()

def forward():
    set_speed()
    # global direction
    IN1.low()
    IN2.high()
    IN3.low()
    IN4.high()
    utime.sleep(0.5)
    stop()
    
    if direction == "UP":
        pos[1] += 1
    elif direction == "DOWN":
        pos[1] -= 1
    elif direction == "LEFT":
        pos[0] -= 1
    elif direction == "RIGHT":
        pos[0] += 1

    maze[tuple(pos)] = maze.get(tuple(pos), 0) + 1  # Increase visit count

def turn_left():
    set_speed()
    global direction
    IN1.high()
    IN2.low()   # Left motor forward
    IN3.low()
    IN4.high()  # Right motor backward
    utime.sleep(1)
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
    IN2.high()  # Left motor backward
    IN3.high()
    IN4.low()   # Right motor forward
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

# Get distance from ultrasonic sensor
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
    return (time_passed * 0.0343) / 2  # Convert to cm

# Move servo
# def move_servo(angle):
#     duty = int((angle / 180 * 5000) + 2500)  # MG996R calibrated range
#     servo.duty_u16(duty)
#     utime.sleep(0.4)

front=4400
left = 7500
right=1200

# Move servo to specific angle (MG996R duty cycle)
def move_servo(angle):
    utime.sleep(0.5)  # Allow servo to move
    servo.duty_u16(angle)
    # duty = int(((angle / 180) * 2000) + 500)  # Adjusted for MG996R (500-2500us range)
    # servo.duty_u16(int(duty * 65.536))  # Convert to 16-bit range
    # servo.duty_u16(0)  # Stop sending signal
    
# Maze-solving algorithm
def solve_maze():
    move_servo(front)
    while True:
        dist_front = get_distance()
        print(f"Front: {dist_front} cm, Position: {tuple(pos)}")

        if dist_front > 15:
            forward()
        else:
            stop()
            utime.sleep(0.5)

            # Scan left and right
            move_servo(left)  # Look left
            dist_left = get_distance()
            utime.sleep(2)

            move_servo(right)  # Look right
            dist_right = get_distance()
            utime.sleep(2)

            move_servo(front)  # Reset
            utime.sleep(2)

            # Determine least visited direction
            left_pos = (pos[0] - 1, pos[1]) if direction == "UP" else \
                       (pos[0] + 1, pos[1]) if direction == "DOWN" else \
                       (pos[0], pos[1] - 1) if direction == "RIGHT" else \
                       (pos[0], pos[1] + 1)

            right_pos = (pos[0] + 1, pos[1]) if direction == "UP" else \
                        (pos[0] - 1, pos[1]) if direction == "DOWN" else \
                        (pos[0], pos[1] + 1) if direction == "RIGHT" else \
                        (pos[0], pos[1] - 1)

            left_visits = maze.get(left_pos, 0)
            right_visits = maze.get(right_pos, 0)

            if dist_left > 15 and left_visits < right_visits:
                turn_left()
            elif dist_right > 15:
                turn_right()
            else:
                print("Backtracking...")
                turn_left()
                turn_left()  # Reverse direction
                forward()
                
solve_maze()

# while True:
#     forward()
#     utime.sleep(1)
#     stop()
#     utime.sleep(1)
#     backward()
#     utime.sleep(1)
#     stop()
#     utime.sleep(1)
#     turn_right()
#     utime.sleep(1)
#     stop()
#     utime.sleep(1)
#     turn_left()
#     utime.sleep(1)
#     stop()
#     utime.sleep(1)
    # move_servo(front)
    # distance = get_distance()
    # print('Distance:', distance)
    # utime.sleep(1)
    # move_servo(1704)
    # distance = get_distance()
    # print('Distance:', distance)
    # utime.sleep(1)
    
    
# # Dijkstra's algorithm for maze solving
# def dijkstra_solve():
#     visited = set()  # Track visited positions
#     backtrack_stack = []  # Store previous moves for backtracking
#     pq = []  # Priority queue
#     position = (0, 0)  # (x, y) Grid-like representation of movement
#     heapq.heappush(pq, (0, position, 'START'))  # (cost, position, direction)

#     while pq:
#         cost, position, direction = heapq.heappop(pq)

#         if position in visited:
#             continue  # Skip already visited positions

#         visited.add(position)  # Mark position as visited

#         move_servo(90)  # Look forward
#         front_distance = get_distance()

#         move_servo(180)  # Look right
#         right_distance = get_distance()

#         move_servo(0)  # Look left
#         left_distance = get_distance()

#         available_moves = []

#         # Define new positions assuming a grid (updating x, y coordinates)
#         new_forward = (position[0], position[1] + 1)
#         new_right = (position[0] + 1, position[1])
#         new_left = (position[0] - 1, position[1])

#         # Add valid moves to priority queue
#         if front_distance > 15 and new_forward not in visited:
#             available_moves.append(('F', cost + 1, new_forward))
#         if right_distance > 15 and new_right not in visited:
#             available_moves.append(('R', cost + 2, new_right))
#         if left_distance > 15 and new_left not in visited:
#             available_moves.append(('L', cost + 2, new_left))

#         if available_moves:
#             available_moves.sort(key=lambda x: x[1])  
#             direction, _, new_position = available_moves[0]  
#             backtrack_stack.append(position)  # Save current position before moving
#         else:
#             # If stuck, backtrack
#             if backtrack_stack:
#                 position = backtrack_stack.pop()  
#                 backward()
#                 utime.sleep(0.5)
#                 continue  

#         # Move based on the selected direction
#         if direction == 'F':
#             forward()
#             position = new_forward
#         elif direction == 'R':
#             turn_right()
#             position = new_right
#         elif direction == 'L':
#             turn_left()
#             position = new_left

#         utime.sleep(0.5)

#         # Stop if the goal is reached (adjust stopping condition)
#         if cost > 20:  # Example condition
#             stop()
#             break

# # Run the maze solver
# dijkstra_solve()