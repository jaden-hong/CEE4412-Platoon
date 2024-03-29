import time
from Motor import *
import RPi.GPIO as GPIO
from servo import *
from PCA9685 import PCA9685
from Led import *
from Buzzer import *
led = Led()
buzzer = Buzzer()

#uses the git repository for base movement

class BaseCar:
    def __init__(self,MAX_DISTANCE = 300,TIME_OUT = 500):
        #ultrasonic portion
        GPIO.setwarnings(False)
        self.trigger_pin = 27
        self.echo_pin = 22
        self.MAX_DISTANCE = MAX_DISTANCE
        self.timeOut = self.MAX_DISTANCE * 60  # calculate timeout according to the maximum measuring distance
        # self.timeOut = TIME_OUT  # calculate timeout according to the maximum measuring distance
        
        GPIO.setmode(GPIO.BCM) # ultrasonic

        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)


        # setup for future functions
        self.PWM = Motor()
        self.LMR=0x00 #bite array for LMR data
        self.pwm_S = Servo()


        #line tracking portion of sensors
        self.IR01 = 14
        self.IR02 = 15
        self.IR03 = 23
        
        GPIO.setup(self.IR01,GPIO.IN)
        GPIO.setup(self.IR02,GPIO.IN)
        GPIO.setup(self.IR03,GPIO.IN)

    def pulseIn(self, pin, level, timeOut):  # obtain pulse time of a pin under timeOut
        t0 = time.time()
        while GPIO.input(pin) != level:
            if (time.time() - t0) > timeOut * 0.000001:
                return 0
        t0 = time.time()
        while GPIO.input(pin) == level:
            if (time.time() - t0) > timeOut * 0.000001:
                return 0
        pulseTime = (time.time() - t0) * 1000000
        return pulseTime

    def get_distance(self):  # get the measurement results of the ultrasonic module, with unit: cm
        distance_cm = [0, 0, 0, 0, 0]
        for i in range(5):
            GPIO.output(self.trigger_pin, GPIO.HIGH)  # make trigger_pin output 10us HIGH level
            time.sleep(0.00001)  # 10us
            GPIO.output(self.trigger_pin, GPIO.LOW)  # make trigger_pin output LOW level
            pingTime = self.pulseIn(self.echo_pin, GPIO.HIGH, self.timeOut)  # read plus time of echo_pin
            distance_cm[i] = pingTime * 340.0 / 2.0 / 10000.0  # calculate distance with sound speed 340m/s
        distance_cm = sorted(distance_cm)
        return int(distance_cm[2])

    def run(self):
        pass

    def calculateLMR(self):
        if GPIO.input(self.IR01)==True:
            self.LMR=(self.LMR | 4)
        if GPIO.input(self.IR02)==True:
            self.LMR=(self.LMR | 2)
        if GPIO.input(self.IR03)==True:
            self.LMR=(self.LMR | 1)

def ledbuzz(led,buzzer,action,buzz='none',carType='none'):
    #buzz = boolean
        if action== "drive":
            #runs when the car is going
            buzzer.run('0')
            led.ledIndex(0x08,0,255,0)      #green means go
            led.ledIndex(0x01,0,255,0)
            # print("DRIVING")

        elif action == "stop":
            #runs when the car must stop
            # buzzer.run('1')
            led.ledIndex(0x01,255,0,0)      #Red means stopped
            led.ledIndex(0x08,255,0,0)
            # print("OBJECT IN WAY / CAR STOPPED")
        elif action == "none":
            buzzer.run('0')
            led.ledIndex(0x08,0,0,0)
        elif action == "end":
            led.colorWipe(led.strip, Color(0,0,0))
            buzzer.run('0')

# def buzzerEnd(led,buzzer):
#     led.colorWipe(led.strip, Color(0,0,0))
#     buzzer.run('0')

'''
# def buzzerGo(led,buzzer):
#     #runs when the car is going
#     buzzer.run('0')
#     led.ledIndex(0x08,0,255,0)      #green means go
#     led.ledIndex(0x01,0,255,0)
#     # print("DRIVING")

# def buzzerStop(led,buzzer):
#     #runs when the car must stop
#     # buzzer.run('1')
#     led.ledIndex(0x01,255,0,0)      #Red means stopped
#     led.ledIndex(0x08,255,0,0)
#     # print("OBJECT IN WAY / CAR STOPPED")

# def buzzerAvoid(led,buzzer):
#     # buzzer.run('1')
#     led.ledIndex(0x01,255,255,0)      #Yellow avoiding
#     led.ledIndex(0x08,255,255,0)
#     # print("OBJECT IN WAY / AR STOPPED")

# def buzzerIntersection(led,buzzer):
#     # buzzer.run('1')
#     led.ledIndex(0x01,0,0,255)      #Blue forks
#     led.ledIndex(0x08,0,0,255)
#     # print("OBJECT IN WAY / CAR STOPPED")




# go=LaneDriveGROUP4()
# # Main program logic follows:
# if __name__ == '__main__':
#     print ('Program is starting ... ')
#     try:
#         go.run()
#     except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program  will be  executed.
#         PWM.setMotorModel(0,0,0,0)
#         buzzerEnd(led,buzzer)
'''