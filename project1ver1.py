import RPi.GPIO as GPIO
import time
import threading
import enum as ENUM

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.OUT)

LB_STATES = ["LB_SMStart", "LB_WaitPress", "LB_Pressed"]
LB_STATE = LB_STATES[0]

def TickFct_LedBlink(LB_STATE):
    if LB_STATE == LB_STATES[0]:
        GPIO.output(16, GPIO.LOW)
        LB_STATE = LB_STATES[1]
    elif LB_STATE == LB_STATES[1]:
        if GPIO.input(26) == GPIO.HIGH:
            GPIO.output(16, GPIO.HIGH if GPIO.input(16) == GPIO.LOW else GPIO.LOW)
            LB_STATE = LB_STATES[2]
        elif GPIO.input(26) == GPIO.LOW:
            LB_STATE = LB_STATES[1]
        else:
            LB_STATE = LB_STATES[1]
    elif LB_STATE == LB_STATES[2]:
        if GPIO.input(26) == GPIO.LOW:
            LB_STATE = LB_STATES[1]
        elif GPIO.input == GPIO.HIGH:
            LB_STATE = LB_STATES[2]
        else:
            LB_STATE = LB_STATES[2]
    else:
        LB_STATE = LB_STATES[0]
    return LB_STATE
print("RUNNING")

while True:
    LB_STATE = TickFct_LedBlink(LB_STATE)
