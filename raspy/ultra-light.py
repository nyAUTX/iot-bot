import RPi.GPIO as GPIO
import time
from picamera2 import Picamera2
from datetime import datetime

# ------------------ GPIO SETUP ------------------
GPIO.setmode(GPIO.BCM)

# Ultrasonic pins
TRIG = 23
ECHO = 24

# RGB LED pins
RED = 17
GREEN = 27
BLUE = 22

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)

GPIO.output(TRIG, False)

# ------------------ CAMERA SETUP ------------------
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()

# ------------------ FUNCTIONS ------------------
def set_color(r, g, b):
    GPIO.output(RED, r)
    GPIO.output(GREEN, g)
    GPIO.output(BLUE, b)

def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

def warning_sequence():
    # ~5 seconds total
    for _ in range(5):
        set_color(0, 1, 0)   # Green
        time.sleep(0.3)
        set_color(1, 1, 0)   # Yellow
        time.sleep(0.3)
        set_color(1, 0, 0)   # Red
        time.sleep(0.3)
        set_color(0, 0, 0)
        time.sleep(0.1)

def take_photo():
    filename = f"/home/andreas/photos/photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    camera.capture_file(filename)
    print(f"Photo saved: {filename}")

# ------------------ MAIN LOOP ------------------
try:
    print("System armed...")
    while True:
        dist = measure_distance()
        print(f"Distance: {dist} cm")

        # Covered sensor (adjust if needed)
        if dist < 5:
            print("Sensor covered!")
            warning_sequence()
            take_photo()
            time.sleep(3)  # prevent multiple triggers

        time.sleep(0.2)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    set_color(0, 0, 0)
    GPIO.cleanup()

