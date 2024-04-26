import socket
import time
import cv2
import numpy as np
import io

#import brains of da lead car

class Processing:
    '''
    Class to act as the "brains" of the lead car. This will be run
    on a laptop to use OPENCV to process information sent to it, then 
    send out the navigation directions back to the car. This is necessary
    due to the limited processing power of the Rpi
    '''
    def __init__(self,port = 5000, totalCars = 1):
        self.host = socket.gethostname()
        self.port = port

        print("Staring laptop host at",self.host,self.port)

        self.laptop_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create new socket
        self.laptop_socket.bind((self.host,self.port))

        print("Listening for lead car")
        self.laptop_socket.listen()
        self.conn, self.addr = self.laptop_socket.accept()
        print("Succesfully connected to lead car")
        self.video_decoder = cv2.VideoCapture()

    def process(self,data):
        '''
        function that takes in the sensor data: image, LMRdata, ultrasonicData
        '''
        # with image : process into vector representation + object detection
        # - if object detected too close (size of bounding box), stop vehicle until 
        #   object has passed
        # - objects will be pedestrians + stop signs
        

        # average out the points and determine the offset to left / right

        # adjust wheel rotation to center car back into lane

       
        # decisions = (wheelSpeed, ledStatus, buzzerStatus)
        #return decisions

        ## from data stream, assumes image is passed
        pass


    def communicate(self):
        '''
        parameters give movement data
        then communicate sends the data across to the lead car via socket 
        '''
        pass

    def run(self):
        '''
        main loop to receive image, process, and communicate
        '''

        #need to double check this encoding stuff
        print("Starting loop")
        while True:
            # Receive data
            print("Waiting for data:")
            data = self.conn.recv(4096000)  # Adjust buffer size as needed

            # Check if the data is empty, indicating the end of the stream
            if not data:
                print("No data detected")
                self.conn.close()
                break
            # Decode the data into a frame
            frame = self.video_decoder.decode(np.frombuffer(data, dtype=np.uint8))

            # Check if decoding was successful
            if frame is not None:
                # Convert the frame to RGB format
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                movement = self.process(rgb_frame)
                self.communicate(movement)


                # Process the frame as needed
                # For example, you can display it
                cv2.imshow('Frame', rgb_frame)


    def run2(self):
        while True:
            # Receive data
            print('recving data')
            data = self.conn.recv(4096000000)  # Adjust buffer size as needed

            # Check if the data is empty, indicating the end of the stream
            if not data:
                print("No data detected")
                self.conn.close()
                break
            
            print("interpreting data")
            # print(data)
            # Create a bytes IO object to read the data as a stream
            stream = io.BytesIO(data)
            # print(stream)
            # Decode the data into a frame
            print(stream.read())
            frame = cv2.imdecode(np.frombuffer(stream.read(), dtype=np.uint8), cv2.IMREAD_COLOR)
            print(frame)

            # Check if decoding was successful
            if frame is not None:
                print("Frame alive!")
                # Convert the frame to RGB format
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Process the frame as needed
                movement = self.process(rgb_frame)
                self.communicate(movement)

                # Display the frame
                cv2.imshow('Frame', rgb_frame)
                print("displayed image")

                # Check for key press to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        # Close any OpenCV windows when the loop exits
        cv2.destroyAllWindows()


if __name__ == "__main__":

    laptopName = socket.gethostname()
    print("Laptop name:",laptopName,"Put it into leadCar.py")
    proc = Processing()
    proc.run2()