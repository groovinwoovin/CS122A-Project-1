import RPi.GPIO as GPIO
import time
import threading
import enum as ENUM
import pigpio

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(20, GPIO.OUT)

servo = pigpio.pi()

servo.set_servo_pulsewidth(24, 1000)
time.sleep(1)
servo.set_servo_pulsewidth(24, 1500)
time.sleep(1)
servo.set_servo_pulsewidth(24,2000)
time.sleep(1)

#global variables
signal = 0
toggled = 0

BP_STATES = ["BP_SMStart","BP_WaitPress","BP_Pressed"]
BP_STATE = BP_STATES[0]

def TickFct_ButtonPress(BP_STATE):
    global signal
    #mealy
    if BP_STATE == BP_STATES[0]:
        signal = 0 #Set servo signal low
        BP_STATE = BP_STATES[1]
    elif BP_STATE == BP_STATES[1]:
        if GPIO.input(26) == GPIO.HIGH:
            signal = 1 #Set servo signal high
            BP_STATE = BP_STATES[2]
        elif GPIO.input(26) == GPIO.LOW:
            BP_STATE = BP_STATES[1]
        else:
            BP_STATE = BP_STATES[1]
    elif BP_STATE == BP_STATES[2]:
        if GPIO.input(26) == GPIO.LOW:
            BP_STATE = BP_STATES[1]
        elif GPIO.input(26) == GPIO.HIGH:
            BP_STATE = BP_STATES[2]
        else:
            BP_STATE = BP_STATES[2]
    else:
        BP_STATE = BP_STATES[0]
    return BP_STATE

SM_STATES = ["SM_SMStart", "SM_Neutral", "SM_Up", "SM_Down"]
SM_STATE = SM_STATES[0]

def TickFct_ServoMove(tempState):
    SM_STATE = tempState
    global signal
    global toggled
    #print(signal, toggled)
    #mealy
    if SM_STATE == SM_STATES[0]:
        #print("SMSTART")
        toggled = 1
        SM_STATE = SM_STATES[1]
    elif SM_STATE == SM_STATES[1]:
        if signal == 1 and toggled == 1:
            #print("ON")
            #print("SERVO ON")
            servo.set_servo_pulsewidth(24,2000)
            time.sleep(0.5)
            toggled = 0
            signal = 0
            SM_STATE = SM_STATES[2]
        elif signal == 1 and toggled == 0: 
            #print("OFF")
            #print("SERVO OFF")
            servo.set_servo_pulsewidth(24,1000)
            time.sleep(0.5)
            toggled = 1
            signal = 0
            SM_STATE = SM_STATES[3]
        elif signal == 0:
            #print("SERVO NEUTRAL")
            servo.set_servo_pulsewidth(24,1500)
            SM_STATE = SM_STATES[1]
            #print("NEUTRAL")
        else:
            #print("RESET")
            SM_STATE = SM_STATES[1]
    elif SM_STATE == SM_STATES[2]:
        #print("BACK TO NEUTRAL")
        SM_STATE = SM_STATES[1]
    elif SM_STATE == SM_STATES[3]:
        #print("BACK TO NEUTRAL")
        SM_STATE = SM_STATES[1]
    else:
        SM_STATE = SM_STATES[0]
    
    return SM_STATE

print("RUNNING")

while True:
    BP_STATE = TickFct_ButtonPress(BP_STATE)
    SM_STATE = TickFct_ServoMove(SM_STATE)
    time.sleep(0.1)
