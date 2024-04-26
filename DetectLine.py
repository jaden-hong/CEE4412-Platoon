import cv2
import numpy as np

def filter_color(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([70, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    return mask

def detect_lanes(mask):
    edges = cv2.Canny(mask, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=60, minLineLength=100, maxLineGap=150)
    return lines

def average_slope_intercept(lines, image):
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

    left_avg = np.mean(left_lines, axis=0) if left_lines else None
    right_avg = np.mean(right_lines, axis=0) if right_lines else None
    
    return left_avg, right_avg

def draw_lines(image, lines):
    line_image = np.zeros_like(image)
    left_avg, right_avg = average_slope_intercept(lines, image)
    y1 = image.shape[0]
    y2 = int(y1 * 0.6) 
    
    if left_avg is not None:
        left_x1 = int((y1 - left_avg[1]) / left_avg[0])
        left_x2 = int((y2 - left_avg[1]) / left_avg[0])
        cv2.line(line_image, (left_x1, y1), (left_x2, y2), (0, 255, 0), 10)
    
    if right_avg is not None:
        right_x1 = int((y1 - right_avg[1]) / right_avg[0])
        right_x2 = int((y2 - right_avg[1]) / right_avg[0])
        cv2.line(line_image, (right_x1, y1), (right_x2, y2), (0, 255, 0), 10)
    
    return line_image

def calculate_lane_center_offset(image, lines):
    left_avg, right_avg = average_slope_intercept(lines, image)
    if left_avg is not None and right_avg is not None:
        lane_center_x = (left_avg[0] + right_avg[0]) / 2
        image_center_x = image.shape[1] / 2
        offset = int(image_center_x - lane_center_x)
        return offset
    else:
        return None
    
def process_image(image):
    mask = filter_color(image)
    lines = detect_lanes(mask)
    lane_lines_image = draw_lines(image, lines)
    return lane_lines_image, lines

image = cv2.imread('image2.jpg')
processed_image, detected_lines = process_image(image)
lane_center_offset = calculate_lane_center_offset(image, detected_lines)
print(f'Lane Center Offset: {lane_center_offset}')
cv2.imshow('Original', image)
cv2.imshow('Processed', processed_image)
cv2.waitKey(0) 
cv2.destroyAllWindows()