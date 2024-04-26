import numpy as np 
import pandas as pd 
import cv2 
import time

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
	bottom_left = [cols * 0.02, rows * 0.65]
	top_left	 = [cols * 0.02, rows * 0.95]
	bottom_right = [cols * 0.99, rows * 0.65]
	top_right = [cols * 0.99, rows * 0.95]
 
 
	vertices = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
	# filling the polygon with white color and generating the final mask
	cv2.fillPoly(mask, vertices, ignore_mask_color)
	# performing Bitwise AND on the input image and mask to get only the edges on the road
	masked_image = cv2.bitwise_and(image, mask)
	return masked_image

# def hough_transform(image):
# 	"""
# 	Determine and cut the region of interest in the input image.
# 	Parameter:
# 		image: grayscale image which should be an output from the edge detector
# 	"""
# 	# Distance resolution of the accumulator in pixels.
# 	rho = 1			
 
# 	# Angle resolution of the accumulator in radians.
# 	theta = np.pi/360
 
# 	# Only lines that are greater than threshold will be returned.
# 	threshold = 180
 
# 	# Line segments shorter than that are rejected.
# 	minLineLength = 5
 
# 	# Maximum allowed gap between points on the same line to link them
# 	maxLineGap = 10
 	
# 	# function returns an array containing dimensions of straight lines 
# 	# appearing in the input image
# 	return cv2.HoughLinesP(image, rho = rho, theta = theta, threshold = threshold,
# 						minLineLength = minLineLength, maxLineGap = maxLineGap)
 
def average_slope_intercept(lines):
    """
    Find the slope and intercept of the left and right lanes of each image.
    Parameters:
        lines: output from Hough Transform
    """
    left_lines = [] #(slope, intercept)
    left_weights = [] #(length,)
    right_lines = [] #(slope, intercept)
    right_weights = [] #(length,)

    try:
        for line in lines:
            for x1, y1, x2, y2 in line:
                if x1 == x2:
                    continue
                # calculating slope of a line
                slope = (y2 - y1) / (x2 - x1)
                # calculating intercept of a line
                intercept = y1 - (slope * x1)
                # calculating length of a line
                length = np.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2))
                # slope of left lane is negative and for right lane slope is positive
                if slope < 0:
                    left_lines.append((slope, intercept))
                    left_weights.append((length))
                else:
                    right_lines.append((slope, intercept))
                    right_weights.append((length))
        # 
        left_lane = np.dot(left_weights, left_lines) / np.sum(left_weights) if len(left_weights) > 0 else None
        right_lane = np.dot(right_weights, right_lines) / np.sum(right_weights) if len(right_weights) > 0 else None
        return left_lane, right_lane
    except Exception as e:
        print("No road detected")
        return None, None

def pixel_points(y1, y2, line):
    """
    Converts the slope and intercept of each line into pixel points.
        Parameters:
            y1: y-value of the line's starting point.
            y2: y-value of the line's end point.
            line: The slope and intercept of the line.
    """
    if line is None:
        return None
    slope, intercept = line
    
    # Check if the slope is zero (vertical line)
    if slope == 0:
        # Assign default x-coordinates (same as intercept)
        x1 = int(intercept)
        x2 = int(intercept)
    else:
        # Calculate x-coordinates using the slope and intercept
        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)
    
    y1 = int(y1)
    y2 = int(y2)
    
    return ((x1, y1), (x2, y2))

def lane_lines(image, lines):
	"""
	Create full lenght lines from pixel points.
		Parameters:
			image: The input test image.
			lines: The output lines from Hough Transform.
	"""
	left_lane, right_lane = average_slope_intercept(lines)
	y1 = image.shape[0]
	y2 = y1 * 0.6
	left_line = pixel_points(y1, y2, left_lane)
	right_line = pixel_points(y1, y2, right_lane)
	return left_line, right_line

	
def draw_lane_lines(image, lines, color=[255, 0, 0], thickness=12):
	"""
	Draw lines onto the input image.
		Parameters:
			image: The input test image (video frame in our case).
			lines: The output lines from Hough Transform.
			color (Default = red): Line color.
			thickness (Default = 12): Line thickness. 
	"""
	line_image = np.zeros_like(image)
	for line in lines:
		if line is not None:
			cv2.line(line_image, *line, color, thickness)
	return cv2.addWeighted(image, 1.0, line_image, 1.0, 0.0)

def frame_processor(image):
    """
    Process the input frame to detect lane lines.
    Parameters:
        image: image of a road where one wants to detect lane lines
        (we will be passing frames of video to this function)
    """
    # Convert the RGB image to grayscale
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to remove noise from the frames
    blur = cv2.GaussianBlur(grayscale, (5, 5), 0)
    
    # Thresholding to ignore dark colors
    _, thresholded = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)

    # Canny edge detection
    edges = cv2.Canny(thresholded, 100, 200) 
    
    # Region selection mask
    mask = np.zeros_like(edges)
    ignore_mask_color = 255
    imshape = image.shape
    vertices = np.array([[(0, imshape[0]), (imshape[1] / 2, imshape[0] / 2), (imshape[1], imshape[0])]], dtype=np.int32)
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    masked_edges = cv2.bitwise_and(edges, mask)
    
    # Hough transform to detect lines
    lines = cv2.HoughLinesP(masked_edges, 2, np.pi/180, 15, np.array([]), minLineLength=5, maxLineGap=20)
    
    # Draw the detected lines on the original image
    result = draw_lane_lines(image, lane_lines(image, lines))
    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    
    return result_rgb



def region_selection_object(image):
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
	top_left	 = [cols * 0.02, rows * 0.3]
	bottom_right = [cols * 0.98, rows * 0.95]
	top_right = [cols * 0.98, rows * 0.3]
 
 
	vertices = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
	# filling the polygon with white color and generating the final mask
	cv2.fillPoly(mask, vertices, ignore_mask_color)
	# performing Bitwise AND on the input image and mask to get only the edges on the road
	masked_image = cv2.bitwise_and(image, mask)
	return masked_image


def detect_faces(image):
    """
    Detect faces in the input image and draw rectangles around them.
    
    Parameters:
        image: Input image in BGR format.
        
    Returns:
        image_with_faces: Image with rectangles drawn around detected faces.
    """
    # Load the cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Convert the image to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Draw rectangles around the faces
    image_with_faces = image.copy()  # Make a copy to not modify the original image
    for (x, y, w, h) in faces:
        cv2.rectangle(image_with_faces, (x, y), (x+w, y+h), (255, 0, 0), 2)

    result_rgb = cv2.cvtColor(image_with_faces, cv2.COLOR_BGR2RGB)
    return result_rgb

def detect_stop_signs(img):
    """
    Detects stop signs in the input image and draws rectangles around them.
    
    Parameters:
        img: Input image in BGR format.
        
    Returns:
        img_rgb: Image with rectangles drawn around detected stop signs in RGB format.
    """
    # Convert image to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Convert image to RGB format
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Load stop sign classifier
    stop_data = cv2.CascadeClassifier('stop_data.xml')

    # Detect stop signs
    found = stop_data.detectMultiScale(img_gray, minSize=(20, 20))

    try:
        # Draw rectangles around detected stop signs
        for (x, y, width, height) in found:
            cv2.rectangle(img_rgb, (x, y), (x + height, y + width), (0, 255, 0), 5)
    except OverflowError as e:
        print("OverflowError:", e)
        # Return the original image without drawing rectangles
        
        
        return img_rgb

    result_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)

    return result_rgb



# Initialize video capture from webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Loop to continuously read frames from the webcam
while True:
    # Capture frame-by-frame
    start_time = time.time()
    
    ret, frame = cap.read()
    
    # Process the frame to detect lane lines
    processed_frame = frame_processor(frame)
    
    # Apply region selection for objects
    mask1 = region_selection_object(processed_frame)
    
    # Detect faces
    face_detected_frame = detect_faces(mask1)
    
    # Detect stop signs
    processed_frame = detect_stop_signs(face_detected_frame)

    # Display the resulting frame
    cv2.imshow('Frame', processed_frame)
    
    # Calculate the time taken to process the frame
    time_taken = time.time() - start_time
    
    # Calculate the delay required to achieve the desired frame rate
    delay = max(1.0 / 4 - time_taken, 0)
    
    # Wait for the calculated delay
    time.sleep(delay)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    if cv2.waitKey(1) & 0xFF == ord('c'):
        cv2.imwrite('saved_frame.jpg', processed_frame)
        print("Frame saved as saved_frame.jpg")

# Release the capture
cap.release()
cv2.destroyAllWindows()
