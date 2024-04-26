import cv2
import numpy as np
import math
import time
from PCA9685 import PCA9685
from ADC import *
from picamera2 import Picamera2

class Motor:
    def __init__(self):
        self.pwm = PCA9685(0x40, debug=True)
        self.pwm.setPWMFreq(50)
        self.time_proportion = 2.5 
        self.adc = Adc()

    @staticmethod
    def duty_range(duty1, duty2, duty3, duty4):
        if duty1 > 4095:
            duty1 = 4095
        elif duty1 < -4095:
            duty1 = -4095

        if duty2 > 4095:
            duty2 = 4095
        elif duty2 < -4095:
            duty2 = -4095

        if duty3 > 4095:
            duty3 = 4095
        elif duty3 < -4095:
            duty3 = -4095

        if duty4 > 4095:
            duty4 = 4095
        elif duty4 < -4095:
            duty4 = -4095
        return duty1, duty2, duty3, duty4

    def left_Upper_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(0, 0)
            self.pwm.setMotorPwm(1, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(1, 0)
            self.pwm.setMotorPwm(0, abs(duty))
        else:
            self.pwm.setMotorPwm(0, 4095)
            self.pwm.setMotorPwm(1, 4095)

    def left_Lower_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(3, 0)
            self.pwm.setMotorPwm(2, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(2, 0)
            self.pwm.setMotorPwm(3, abs(duty))
        else:
            self.pwm.setMotorPwm(2, 4095)
            self.pwm.setMotorPwm(3, 4095)

    def right_Upper_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(6, 0)
            self.pwm.setMotorPwm(7, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(7, 0)
            self.pwm.setMotorPwm(6, abs(duty))
        else:
            self.pwm.setMotorPwm(6, 4095)
            self.pwm.setMotorPwm(7, 4095)

    def right_Lower_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(4, 0)
            self.pwm.setMotorPwm(5, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(5, 0)
            self.pwm.setMotorPwm(4, abs(duty))
        else:
            self.pwm.setMotorPwm(4, 4095)
            self.pwm.setMotorPwm(5, 4095)

    def setMotorModel(self, duty1, duty2, duty3, duty4):
        duty1, duty2, duty3, duty4 = self.duty_range(duty1, duty2, duty3, duty4)
        self.left_Upper_Wheel(duty1)
        self.left_Lower_Wheel(duty2)
        self.right_Upper_Wheel(duty3)
        self.right_Lower_Wheel(duty4)

    def Rotate(self, n):
        angle = n
        bat_compensate = 7.5 / (self.adc.recvADC(2) * 3)
        while True:
            W = 2000

            VY = int(2000 * math.cos(math.radians(angle)))
            VX = -int(2000 * math.sin(math.radians(angle)))

            FR = VY - VX + W
            FL = VY + VX - W
            BL = VY - VX - W
            BR = VY + VX + W

            PWM.setMotorModel(FL, BL, FR, BR)
            print("rotating")
            time.sleep(5 * self.time_proportion * bat_compensate / 1000)
            angle -= 5

PWM = Motor()
picam2 = Picamera2()

def capture():
    picam2.start_preview()
    time.sleep(2)

    config = picam2.create_still_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    buffer = picam2.capture_array("main") 
    picam2.stop()

    image = cv2.cvtColor(buffer, cv2.COLOR_RGB2BGR)

    return image

def setMotorModel(self, duty1, duty2, duty3, duty4):
        duty1, duty2, duty3, duty4 = self.duty_range(duty1, duty2, duty3, duty4)
        self.PWM.left_Upper_Wheel(-duty1)
        self.PWM.left_Lower_Wheel(-duty2)
        self.PWM.right_Upper_Wheel(-duty3)
        self.PWM.right_Lower_Wheel(-duty4)

def forward():
    PWM.setMotorModel(1000,1000,1000,1000)

def left():
    PWM.setMotorModel(-1500, -1500, 2000, 2000)

def right():
    PWM.setMotorModel(2000, 2000, -1500, -1500)

def process_image_and_get_offset(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([70, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    edges = cv2.Canny(mask, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=150)
    if lines is None:
        return None 

    left_lines = []
    right_lines = []
    middle_x = image.shape[1] / 2
    for line in lines:
        for x1, y1, x2, y2 in line:
            parameters = np.polyfit((x1, x2), (y1, y2), 1)
            slope = parameters[0]
            intercept = parameters[1]
            if slope < 0 and x1 < middle_x and x2 < middle_x:
                left_lines.append((slope, intercept))
            elif slope > 0 and x1 > middle_x and x2 > middle_x:
                right_lines.append((slope, intercept))
    
    if not left_lines or not right_lines:
        return None 

    left_avg = np.mean(left_lines, axis=0)
    right_avg = np.mean(right_lines, axis=0)

    y1 = image.shape[0]
    left_x1 = int((y1 - left_avg[1]) / left_avg[0])
    right_x1 = int((y1 - right_avg[1]) / right_avg[0])
    lane_center_x = (left_x1 + right_x1) / 2

    image_center_x = middle_x
    offset = int(lane_center_x - image_center_x)

    return offset if left_lines and right_lines else None

def main_loop():
    try:
        while True:
            # take image
            image = capture()

            # process image for offset
            offset = process_image_and_get_offset(image)
            print(offset)
            
            # turn right/left depending on offset
            if offset is not None:
                if offset > 50:
                    right()
                elif offset < -50:
                    left()
                else:
                    forward()
            else:
                forward() 

            time.sleep(1)

    except KeyboardInterrupt:
        setMotorModel(0, 0, 0, 0)
        print('stop')

if __name__ == "__main__":
    main_loop()