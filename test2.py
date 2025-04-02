from machine import Pin, PWM
import time

# Motor control pins
motor1A = Pin(17, Pin.OUT)
motor1B = Pin(18, Pin.OUT)
motor2A = Pin(19, Pin.OUT)
motor2B = Pin(20, Pin.OUT)
pwm1 = PWM(Pin(21))
pwm2 = PWM(Pin(22))
pwm1.freq(1000)
pwm2.freq(1000)

# Servo and Ultrasonic Sensor
servo = PWM(Pin(16))
servo.freq(50)
trig = Pin(14, Pin.OUT)
echo = Pin(15, Pin.IN)

# Maze tracking
maze = {}  # Stores visited positions {(x, y): visit_count}
pos = [0, 0]  # Current (x, y) position
direction = "UP"  # UP, DOWN, LEFT, RIGHT

# Movement functions
def move_forward():
    global pos, direction
    motor1A.high()
    motor1B.low()
    motor2A.high()
    motor2B.low()
    pwm1.duty_u16(30000)
    pwm2.duty_u16(30000)
    time.sleep(1)  # Move one grid step
    stop()

    # Update position in the grid
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
    global direction
    motor1A.low()
    motor1B.high()
    motor2A.high()
    motor2B.low()
    pwm1.duty_u16(20000)
    pwm2.duty_u16(20000)
    time.sleep(0.5)
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
    motor1A.high()
    motor1B.low()
    motor2A.low()
    motor2B.high()
    pwm1.duty_u16(20000)
    pwm2.duty_u16(20000)
    time.sleep(0.5)
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
    motor1A.low()
    motor1B.low()
    motor2A.low()
    motor2B.low()

# Distance measurement
def get_distance():
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)
    trig.low()

    while echo.value() == 0:
        start_time = time.ticks_us()
    while echo.value() == 1:
        end_time = time.ticks_us()

    duration = end_time - start_time
    distance = (duration * 0.0343) / 2  # cm
    return distance

# Servo control
def set_servo(angle):
    duty = int(5000 + (angle / 180) * 5000)
    servo.duty_u16(duty)
    time.sleep(0.3)

# Maze-solving algorithm
def solve_maze():
    while True:
        dist_front = get_distance()
        print(f"Front: {dist_front} cm, Position: {tuple(pos)}")

        if dist_front > 15:
            move_forward()
        else:
            stop()
            time.sleep(0.5)

            # Scan left and right
            set_servo(0)  # Look left
            dist_left = get_distance()
            time.sleep(0.5)

            set_servo(180)  # Look right
            dist_right = get_distance()
            time.sleep(0.5)

            set_servo(90)  # Reset

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
                turn_right()
                turn_right()  # Reverse direction
                move_forward()

solve_maze()
