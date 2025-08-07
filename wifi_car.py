import network
import socket
from machine import Pin
import time
import secrets  # this should contain your SSID and PASSWORD

# === Motor Pins ===
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

# === Connect to WiFi ===
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)

print("Connecting to Wi-Fi...")
while not wlan.isconnected():
    time.sleep(1)

ip = wlan.ifconfig()[0]
print(f"Connected, IP: {ip}")

# === Web Server ===
html = """<!DOCTYPE html>
<html>
<head><title>Pico Car</title></head>
<body>
<h2>Pico Car Control</h2>
<a href="/forward"><button>Forward</button></a>
<a href="/backward"><button>Backward</button></a>
<a href="/left"><button>Left</button></a>
<a href="/right"><button>Right</button></a>
<a href="/stop"><button>Stop</button></a>
</body></html>
"""

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print("Listening on", addr)

while True:
    try:
        cl, addr = s.accept()
        print("Client connected from", addr)
        request = cl.recv(1024)
        request = request.decode('utf-8')
        print("Request:", request)

        if 'GET /forward' in request:
            move_forward()
        elif 'GET /backward' in request:
            move_backward()
        elif 'GET /left' in request:
            turn_left()
        elif 'GET /right' in request:
            turn_right()
        elif 'GET /stop' in request:
            stop()

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(html)
        cl.close()

    except Exception as e:
        print("Error:", e)
