import RPi.GPIO as GPIO
import time
import threading
import enum as ENUM
import pigpio

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
BUTTONPIN = 26
GPIO.setup(BUTTONPIN, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #Button
LEDPIN = 16
GPIO.setup(16, GPIO.OUT) #StatusLED
ECHOPIN = 21
GPIO.setup(ECHOPIN, GPIO.IN) #Ultrasonic Sensor ECHOPIN
TRIGPIN = 20
GPIO.setup(TRIGPIN, GPIO.OUT) #" " TRIGPIN
SERVOPIN = 24
#global variables
signal = 0

#local variables
toggled = 0 #ServoMove
distance = 0 #SensorDetect
count = 0 #SensorDetect

BP_STATES = ["BP_SMStart","BP_WaitPress","BP_Pressed"]
BP_STATE = BP_STATES[0]

def TickFct_ButtonPress(BP_STATE):
    global signal
    #mealy
    if BP_STATE == BP_STATES[0]:
        signal = 0 #Set servo signal low
        BP_STATE = BP_STATES[1]
    elif BP_STATE == BP_STATES[1]:
        if GPIO.input(BUTTONPIN) == GPIO.HIGH:
            signal = 1 #Set servo signal high
            BP_STATE = BP_STATES[2]
        elif GPIO.input(BUTTONPIN) == GPIO.LOW:
            BP_STATE = BP_STATES[1]
        else:
            BP_STATE = BP_STATES[1]
    elif BP_STATE == BP_STATES[2]:
        if GPIO.input(BUTTONPIN) == GPIO.LOW:
            BP_STATE = BP_STATES[1]
        elif GPIO.input(BUTTONPIN) == GPIO.HIGH:
            BP_STATE = BP_STATES[2]
        else:
            BP_STATE = BP_STATES[2]
    else:
        BP_STATE = BP_STATES[0]
    return BP_STATE

def getDist():
    GPIO.output(TRIGPIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIGPIN, GPIO.LOW)
    start = time.time()
    stop = time.time()
    
    while GPIO.input(ECHOPIN) == 0:
        start = time.time()
    while GPIO.input(ECHOPIN) == 1:
        stop = time.time()
        
    return ((stop - start) * 34300 / 2)

US_STATES = ["US_SMStart", "US_WaitClose", "US_Close"]
US_STATE = US_STATES[0]

def TickFct_USSensorDetect(US_STATE):
    global signal
    global distance
    global count
    #mealy
    if US_STATE == US_STATES[0]:
        distance = 0
        US_STATE = US_STATES[1]
    elif US_STATE == US_STATES[1]:
        if distance <= 10:
            count = 0
            US_STATE = US_STATES[2]
        elif distance > 10:
            US_STATE = US_STATES[1]
        else:
            US_STATE = US_STATES[1]
    elif US_STATE == US_STATES[2]:
        if distance <= 10 and count <= 3:
            US_STATE = US_STATES[2]
        elif distance > 10 or count > 3:
            if count > 3:
                signal = 1
            US_STATE = US_STATES[1]
        else:
            US_STATE = US_STATES[2]
    else:
        US_STATE = US_STATES[0]

    #moore
    if US_STATE == US_STATES[1]:
        distance =  getDist()
    elif US_STATE == US_STATES[2]:
        distance = getDist()
        count += 1
    return US_STATE


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
            servo.set_servo_pulsewidth(SERVOPIN,1850)
            time.sleep(0.5)
            toggled = 0
            signal = 0
            SM_STATE = SM_STATES[2]
        elif signal == 1 and toggled == 0: 
            #print("OFF")
            #print("SERVO OFF")
            servo.set_servo_pulsewidth(SERVOPIN,1250)
            time.sleep(0.5)
            toggled = 1
            signal = 0
            SM_STATE = SM_STATES[3]
        elif signal == 0:
            #print("SERVO NEUTRAL")
            servo.set_servo_pulsewidth(SERVOPIN,1550)
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


#initialize servo
servo = pigpio.pi()
servo.set_servo_pulsewidth(SERVOPIN, 1850)
time.sleep(1)
servo.set_servo_pulsewidth(SERVOPIN, 1550)
time.sleep(1)
servo.set_servo_pulsewidth(SERVOPIN, 1250)
time.sleep(1)

GPIO.output(16, GPIO.HIGH)
print("RUNNING")
try:
    while True:
        BP_STATE = TickFct_ButtonPress(BP_STATE)
        US_STATE = TickFct_USSensorDetect(US_STATE)
        SM_STATE = TickFct_ServoMove(SM_STATE)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
