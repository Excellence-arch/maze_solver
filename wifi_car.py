import network
import socket
from machine import Pin, PWM
import time
import secrets  # this should contain your SSID and PASSWORD

# === Motor Pins ===
IN1 = Pin(0, Pin.OUT)
IN2 = Pin(1, Pin.OUT)
IN3 = Pin(2, Pin.OUT)
IN4 = Pin(3, Pin.OUT)

TRIG = Pin(5, Pin.OUT)
ECHO = Pin(6, Pin.IN)

servo = PWM(Pin(7))
servo.freq(50)

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



def set_servo_angle(angle):
    duty = int(1638 + (angle / 180) * (8192 - 1638))
    servo.duty_u16(duty)

def get_distance():
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()

    while ECHO.value() == 0:
        pass
    start = time.ticks_us()

    while ECHO.value() == 1:
        pass
    end = time.ticks_us()

    duration = time.ticks_diff(end, start)
    distance = duration / 58
    return distance



wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)

print("Connecting to Wi-Fi...")
while not wlan.isconnected():
    time.sleep(1)

ip = wlan.ifconfig()[0]
print(f"Connected, IP: {ip}")



html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Pico Car Control</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
      color: white;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
    }

    h2 {
      margin-bottom: 30px;
      font-size: 2rem;
      color: #00ffcc;
      text-shadow: 1px 1px 3px #000;
    }

    .button-container {
      display: grid;
      grid-template-columns: repeat(3, 100px);
      grid-gap: 15px;
      align-items: center;
      justify-items: center;
    }

    .button-container a {
      text-decoration: none;
    }

    button {
      width: 100px;
      height: 50px;
      background-color: #00bcd4;
      border: none;
      border-radius: 10px;
      color: white;
      font-size: 1rem;
      font-weight: bold;
      cursor: pointer;
      box-shadow: 0 4px 6px rgba(0,0,0,0.2);
      transition: transform 0.2s, background-color 0.3s;
    }

    button:hover {
      background-color: #0097a7;
      transform: scale(1.1);
    }

    /* Arrange buttons to form a directional pad layout */
    .forward { grid-column: 2; }
    .left { grid-column: 1; }
    .stop { grid-column: 2; }
    .right { grid-column: 3; }
    .backward { grid-column: 2; }
  </style>
</head>
<body>

  <h2>Pico Car Control</h2>
  <div class="button-container">
    <a href="/forward" class="forward"><button>▲</button></a>
    <a href="/left" class="left"><button>◀</button></a>
    <a href="/stop" class="stop"><button>■</button></a>
    <a href="/right" class="right"><button>▶</button></a>
    <a href="/backward" class="backward"><button>▼</button></a>
  </div>

  <h3 style="margin-top: 30px;">Sensor Direction</h3>
<div class="button-container">
  <a href="/sensor/left"><button>↖ Left</button></a>
  <a href="/sensor/center"><button>⬆ Center</button></a>
  <a href="/sensor/right"><button>↗ Right</button></a>
</div>

<h3 style="margin-top: 30px;">Obstacle Status: <span id="obstacle">Loading...</span></h3>


<script>
  async function checkObstacle() {
    try {
      const res = await fetch('/obstacle');
      const status = await res.text();
      document.getElementById('obstacle').textContent = status;
    } catch (e) {
      document.getElementById('obstacle').textContent = 'Error';
    }
  }

  setInterval(checkObstacle, 1000); // check every 1 sec
  checkObstacle(); // check immediately on load
</script>
</body>
</html>

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
        elif 'GET /sensor/left' in request:
            set_servo_angle(150)
        elif 'GET /sensor/center' in request:
            set_servo_angle(90)
        elif 'GET /sensor/right' in request:
            set_servo_angle(30)
        elif 'GET /obstacle' in request:
            distance = get_distance()
            status = "Obstacle Detected!" if distance < 10 else "Clear"
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
            cl.send(status)
            cl.close()
            continue

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(html)
        cl.close()

    except Exception as e:
        print("Error:", e)
