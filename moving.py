# from machine import Pin, PWM
# import utime

# # Motor control pins (L298N)
# IN1 = Pin(0, Pin.OUT)
# IN2 = Pin(1, Pin.OUT)
# IN3 = Pin(2, Pin.OUT)
# IN4 = Pin(3, Pin.OUT)

# # ENA = PWM(Pin(14))
# # ENB = PWM(Pin(15))


# # def set_speed(speed1=35000, speed2=35000):
# #     ENA.duty_u16(speed1)
# #     ENB.duty_u16(speed2)

# def move_forward():
#     IN1.low()
#     IN2.high()
#     IN3.low()
#     IN4.high()

# def move_backward():
#     IN1.high()
#     IN2.low()
#     IN3.high()
#     IN4.low()

# def turn_left():
#     IN1.low()
#     IN2.high()
#     IN3.high()
#     IN4.low()

# def turn_right():
#     IN1.high()
#     IN2.low()
#     IN3.low()
#     IN4.high()

# def stop():
#     IN1.low()
#     IN2.low()
#     IN3.low()
#     IN4.low()

# def start():
#     # set_speed(35000, 35000)
#     move_forward()
#     utime.sleep(10)
#     stop()

# while True:
#     start()






from machine import Pin
import bluetooth
from ble_advertising import advertising_payload
from micropython import const
import struct
import time
from ubluetooth import BLE, UUID, FLAG_READ, FLAG_WRITE

# === Motor Control Pins ===
IN1 = Pin(0, Pin.OUT)
IN2 = Pin(1, Pin.OUT)
IN3 = Pin(2, Pin.OUT)
IN4 = Pin(3, Pin.OUT)

def move_forward():
    IN1.low(); IN2.high(); IN3.low(); IN4.high()

def move_backward():
    IN1.high(); IN2.low(); IN3.high(); IN4.low()

def turn_left():
    IN1.low(); IN2.high(); IN3.high(); IN4.low()

def turn_right():
    IN1.high(); IN2.low(); IN3.low(); IN4.high()

def stop():
    IN1.low(); IN2.low(); IN3.low(); IN4.low()

# === BLE Setup ===
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX   = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), FLAG_READ)
_UART_RX   = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), FLAG_WRITE)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX),)

ble = BLE()
ble.active(True)

def bt_irq(event, data):
    if event == 1:
        conn_handle, _, _ = data
        print("Device connected")
    elif event == 2:
        conn_handle, _, _ = data
        print("Device disconnected")
        start_advertising()
    elif event == 3:
        conn_handle, attr_handle = data
        command = ble.gatts_read(attr_handle).decode().strip().upper()
        print("Received:", command)
        if command == "F":
            move_forward()
        elif command == "B":
            move_backward()
        elif command == "L":
            turn_left()
        elif command == "R":
            turn_right()
        elif command == "S":
            stop()

def start_advertising():
    name = 'PicoCar'
    payload = advertising_payload(name=name, services=[_UART_UUID])
    ble.gap_advertise(100, adv_data=payload)
    print("Advertising as:", name)

# Register GATT server
services = ( _UART_SERVICE, )
((tx_handle, rx_handle), ) = ble.gatts_register_services(services)

ble.irq(bt_irq)
start_advertising()
