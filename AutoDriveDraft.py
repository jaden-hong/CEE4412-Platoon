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

    def duty_range(self, duty1, duty2, duty3, duty4):
        duties = [duty1, duty2, duty3, duty4]
        return [max(min(d, 4095), -4095) for d in duties]

    def set_motor_model(self, duty1, duty2, duty3, duty4):
        duties = self.duty_range(duty1, duty2, duty3, duty4)
        self.left_upper_wheel(duties[0])
        self.left_lower_wheel(duties[1])
        self.right_upper_wheel(duties[2])
        self.right_lower_wheel(duties[3])

    def left_upper_wheel(self, duty):
        self.pwm.setMotorPwm(1, max(0, duty))
        self.pwm.setMotorPwm(0, max(0, -duty))

    def left_lower_wheel(self, duty):
        self.pwm.setMotorPwm(2, max(0, duty))
        self.pwm.setMotorPwm(3, max(0, -duty))

    def right_upper_wheel(self, duty):
        self.pwm.setMotorPwm(7, max(0, duty))
        self.pwm.setMotorPwm(6, max(0, -duty))

    def right_lower_wheel(self, duty):
        self.pwm.setMotorPwm(5, max(0, duty))
        self.pwm.setMotorPwm(4, max(0, -duty))

picam2 = Picamera2()  # Create a single camera instance outside the function
config = picam2.create_still_configuration(main={"size": (640, 480)})
picam2.configure(config)

def capture():
    try:
        picam2.start()
        # Give the camera a warm-up time
        time.sleep(0.25)
        buffer = picam2.capture_array("main")
        return cv2.cvtColor(buffer, cv2.COLOR_RGB2BGR)
    finally:
        picam2.stop()

def region_selection_road(image):
	"""
	Determine and cut the region of interest in the input image.
	Parameters:
		image: we pass here the output from canny where we have 
		identified edges in the frame
	"""
	# create an array of the same size as of the input image 
	mask = np.zeros_like(image) 
	# if you pass an image with more then one channel
	if len(image.shape) > 2:
		channel_count = image.shape[2]
		ignore_mask_color = (255,) * channel_count
	# our image only has one channel so it will go under "else"
	else:
		# color of the mask polygon (white)
		ignore_mask_color = 255
	# creating a polygon to focus only on the road in the picture
	# we have created this polygon in accordance to how the camera was placed
 
	rows, cols = image.shape[:2]
	bottom_left = [cols * 0.02, rows * 0.95]
	top_left	 = [cols * 0.3, rows * 0.55]
	bottom_right = [cols * 0.98, rows * 0.95]
	top_right = [cols * 0.7, rows * 0.55]
 
 
	vertices = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
	# filling the polygon with white color and generating the final mask
	cv2.fillPoly(mask, vertices, ignore_mask_color)
	# performing Bitwise AND on the input image and mask to get only the edges on the road
	masked_image = cv2.bitwise_and(image, mask)
	return masked_image

def process_image_and_get_offset(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([70, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask = region_selection_road(mask)
    edges = cv2.Canny(mask, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=150)
    if lines is None:
        return None 

    left_lines, right_lines = [], []
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
    return int(lane_center_x - image_center_x)

def main_loop():
    motor = Motor()
    try:
        while True:
            image = capture()
            offset = process_image_and_get_offset(image)
            print("Offset:", offset)

            if offset is not None:
                if offset > 350:
                    print('Turning right')
                    while offset > 350:
                        motor.set_motor_model(2000, 2000, -1500, -1500)  # Turn right
                        image = capture()
                        offset = process_image_and_get_offset(image)
                        print("Offset:", offset)
                        time.sleep(0.25)

                elif offset < -350:
                    print('Turning left')
                    while offset < -350:
                        motor.set_motor_model(-1500, -1500, 2000, 2000)  # Turn left
                        image = capture()
                        offset = process_image_and_get_offset(image)
                        print("Offset:", offset)
                        time.sleep(0.25)
                else:
                    print('Moving forward')
                    motor.set_motor_model(500, 500, 500, 500)
            else:
                print('No lane detected, stopping')
                motor.set_motor_model(0, 0, 0, 0)

            time.sleep(0.5)  # You may adjust this delay as needed

    except KeyboardInterrupt:
        motor.set_motor_model(0, 0, 0, 0)
        print('Stopped by User')

if __name__ == "__main__":
    main_loop()