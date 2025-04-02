# from machine import Pin, time_pulse_us
# import utime

# trig = Pin(14, Pin.OUT)
# echo = Pin(15, Pin.IN)

# def get_distance():
#     trig.low()
#     utime.sleep_us(2)
#     trig.high()
#     utime.sleep_us(10)
#     trig.low()
    
#     duration = time_pulse_us(echo, 1)
#     distance = (duration * 0.0343) / 2  # Convert to cm
#     return distance

# from machine import Pin, PWM

# # Motor Pins
# IN1 = Pin(16, Pin.OUT)
# IN2 = Pin(17, Pin.OUT)
# IN3 = Pin(18, Pin.OUT)
# IN4 = Pin(19, Pin.OUT)
# ENA = PWM(Pin(20))
# ENB = PWM(Pin(21))

# # Set PWM frequency
# ENA.freq(1000)
# ENB.freq(1000)

# def forward(speed=65000):
#     ENA.duty_u16(speed)
#     ENB.duty_u16(speed)
#     IN1.high()
#     IN2.low()
#     IN3.high()
#     IN4.low()

# def backward(speed=65000):
#     ENA.duty_u16(speed)
#     ENB.duty_u16(speed)
#     IN1.low()
#     IN2.high()
#     IN3.low()
#     IN4.high()
    
# def left(speed=65000):
#     ENA.duty_u16(speed)
#     ENB.duty_u16(speed)
#     IN1.high()
#     IN2.low()
#     IN3.low()
#     IN4.high()
    
# def right(speed=65000):
#     ENA.duty_u16(speed)
#     ENB.duty_u16(speed)
#     IN1.low()
#     IN2.high()
#     IN3.high()
#     IN4.low()

# def stop():
#     IN1.low()
#     IN2.low()
#     IN3.low()
#     IN4.low()

# def solve_maze():
#     while True:
#         distance = get_distance()
#         if distance > 15:
#             forward()
#         else:
#             stop()
#             utime.sleep(0.5)  # Pause
            
#             # Try turning right
#             right()
#             utime.sleep(0.5)  # Small turn
            
#             # Check distance again
#             if get_distance() < 15:
#                 # If still blocked, turn left instead
#                 left()
#                 utime.sleep(1)
                
  
                
# solve_maze()


# from machine import Pin, PWM, time_pulse_us
# import utime

# # Motor control pins
# IN1 = Pin(16, Pin.OUT)
# IN2 = Pin(17, Pin.OUT)
# IN3 = Pin(18, Pin.OUT)
# IN4 = Pin(19, Pin.OUT)
# ENA = PWM(Pin(20))  # PWM for speed control
# ENB = PWM(Pin(21))

# ENA.freq(1000)
# ENB.freq(1000)

# # Ultrasonic sensor pins
# trig = Pin(14, Pin.OUT)
# echo = Pin(15, Pin.IN)

# # Movement functions
# def forward(speed=65000):
#     ENA.duty_u16(speed)
#     ENB.duty_u16(speed)
#     IN1.high()
#     IN2.low()
#     IN3.high()
#     IN4.low()

# def backward(speed=65000):
#     ENA.duty_u16(speed)
#     ENB.duty_u16(speed)
#     IN1.low()
#     IN2.high()
#     IN3.low()
#     IN4.high()

# def turn_right():
#     IN1.high()
#     IN2.low()
#     IN3.low()
#     IN4.high()
#     utime.sleep(0.5)  # Adjust based on your setup

# def turn_left():
#     IN1.low()
#     IN2.high()
#     IN3.high()
#     IN4.low()
#     utime.sleep(0.5)  # Adjust based on your setup

# def stop():
#     IN1.low()
#     IN2.low()
#     IN3.low()
#     IN4.low()

# # Get distance from ultrasonic sensor
# def get_distance():
#     trig.low()
#     utime.sleep_us(2)
#     trig.high()
#     utime.sleep_us(10)
#     trig.low()
    
#     duration = time_pulse_us(echo, 1)
#     distance = (duration * 0.0343) / 2  # Convert to cm
#     return distance

# # DFS Algorithm
# def depth_first_search():
#     visited = set()  # Store visited points
#     stack = []  # Stack for DFS
    
#     while True:
#         distance = get_distance()
        
#         if distance > 15:
#             forward()
#             utime.sleep(0.5)  # Move forward slightly
#             stop()
            
#             # Mark as visited
#             stack.append('F')  # Move forward
#             visited.add(tuple(stack))  # Save path
            
#         else:
#             stop()
#             utime.sleep(0.5)
            
#             # Try turning right first
#             turn_right()
#             utime.sleep(0.5)
#             if get_distance() > 15:
#                 stack.append('R')  # Mark right turn
#                 continue  # Move forward
            
#             # If right is blocked, turn left
#             turn_left()
#             utime.sleep(1)  # Extra turn to align
#             if get_distance() > 15:
#                 stack.append('L')  # Mark left turn
#                 continue  # Move forward
            
#             # If both directions blocked, backtrack
#             if stack:
#                 last_move = stack.pop()
#                 if last_move == 'F':
#                     backward()
#                     utime.sleep(0.5)
#                 elif last_move == 'R':
#                     turn_left()  # Reverse right turn
#                 elif last_move == 'L':
#                     turn_right()  # Reverse left turn

# # Run the DFS algorithm
# depth_first_search()


# SERVO MOUNTED ULTRASONIC SENSOR MAZE SOLVER

from machine import Pin, PWM, time_pulse_us
import utime

# Motor control pins (L293D)
IN1 = Pin(14, Pin.OUT)  # Motor A
IN2 = Pin(15, Pin.OUT)
IN3 = Pin(12, Pin.OUT)  # Motor B
IN4 = Pin(13, Pin.OUT)

ENA = PWM(Pin(16))  # PWM for speed control
ENB = PWM(Pin(17))


# Servo for ultrasonic sensor
servo = PWM(Pin(22))
servo.freq(50)  # 50Hz for servo

# Ultrasonic sensor pins
trig = Pin(3, Pin.OUT)
echo = Pin(4, Pin.IN)

# Movement functions
def forward():
    IN1.high()
    IN2.low()
    IN3.high()
    IN4.low()

def backward():
    IN1.low()
    IN2.high()
    IN3.low()
    IN4.high()

def turn_right():
    IN1.high()
    IN2.low()
    IN3.low()
    IN4.high()
    utime.sleep(0.5)

def turn_left():
    IN1.low()
    IN2.high()
    IN3.high()
    IN4.low()
    utime.sleep(0.5)

def stop():
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
    
    duration = time_pulse_us(echo, 1)
    distance = (duration * 0.0343) / 2  # Convert to cm
    return distance

# Move servo to specific angle
def move_servo(angle):
    duty = int((angle / 180 * 5000) + 2500)  # Convert angle to duty cycle
    servo.duty_u16(duty)
    utime.sleep(0.5)  # Allow servo to move

# DFS Algorithm for Maze Solving
def depth_first_search():
    visited = set()  # Store visited points
    stack = []  # Stack for DFS
    
    while True:
        move_servo(90)  # Look straight
        front_distance = get_distance()
        
        if front_distance > 15:
            forward()
            utime.sleep(0.5)
            stop()
            stack.append('F')  # Mark forward move
            visited.add(tuple(stack))
            
        else:
            stop()
            utime.sleep(0.5)
            
            move_servo(180)  # Look right
            right_distance = get_distance()
            utime.sleep(0.5)

            move_servo(0)  # Look left
            left_distance = get_distance()
            utime.sleep(0.5)

            if right_distance > 15:
                turn_right()
                stack.append('R')
            elif left_distance > 15:
                turn_left()
                stack.append('L')
            else:
                if stack:
                    last_move = stack.pop()
                    if last_move == 'F':
                        backward()
                        utime.sleep(0.5)
                    elif last_move == 'R':
                        turn_left()
                    elif last_move == 'L':
                        turn_right()

# Run DFS Algorithm
# depth_first_search()


# from machine import Pin, PWM
# from time import sleep

# pwmPIN=16
# cwPin=14 
# acwPin=15

# def motorMove(speed,direction,speedGP,cwGP,acwGP):
#     if speed > 100: speed=100
#     if speed < 0: speed=0
#     Speed = PWM(Pin(speedGP))
#     Speed.freq(50)
#     cw = Pin(cwGP, Pin.OUT)
#     acw = Pin(acwGP, Pin.OUT)
#     Speed.duty_u16(int(speed/100*65536))
    
#     if direction < 0:
#       cw.value(0)
#       acw.value(1)
#     if direction == 0:
#       cw.value(0)
#       acw.value(0)
#     if direction > 0:
#       cw.value(1)
#       acw.value(0)
      
# motorMove(100,-1,pwmPIN,cwPin,acwPin)
# sleep(5)
# motorMove(100,0,pwmPIN,cwPin,acwPin)