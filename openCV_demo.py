import numpy as np
import cv2 as cv

# Load the cascade
face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    
    # Convert frame to grayscale for face detection
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Draw rectangles around the faces
    for (x, y, w, h) in faces:
        cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Display the resulting frame
    cv.imshow('frame', frame)
    
    key = cv.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('c'):  # Press 'c' to save the frame
        cv.imwrite('saved_frame.jpg', frame)
        print("Frame saved as saved_frame.jpg")

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
