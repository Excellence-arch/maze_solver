from machine import Pin, PWM
import utime

# Motor control pins (L298N)
IN1 = Pin(0, Pin.OUT)
IN2 = Pin(1, Pin.OUT)
IN3 = Pin(2, Pin.OUT)
IN4 = Pin(3, Pin.OUT)

# ENA = PWM(Pin(14))
# ENB = PWM(Pin(15))


# def set_speed(speed1=35000, speed2=35000):
#     ENA.duty_u16(speed1)
#     ENB.duty_u16(speed2)

def move_forward():
    IN1.low()
    IN2.high()
    IN3.low()
    IN4.high()

def move_backward():
    IN1.high()
    IN2.low()
    IN3.high()
    IN4.low()

def turn_left():
    IN1.low()
    IN2.high()
    IN3.high()
    IN4.low()

def turn_right():
    IN1.high()
    IN2.low()
    IN3.low()
    IN4.high()

def stop():
    IN1.low()
    IN2.low()
    IN3.low()
    IN4.low()

def start():
    # set_speed(35000, 35000)
    move_forward()
    utime.sleep(10)
    stop()

while True:
    start()