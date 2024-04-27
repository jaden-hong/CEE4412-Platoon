from BaseCar import *
from Network import LeadModule
from sharedQueue import sQueue #squeue used to access instructions
import queue
import threading
from AutoDriveDraft import capture, region_selection_road, process_image_and_get_offset
from openCV_live import *

class LeadCar2(BaseCar):
    def __init__(self,fol_cars, port = 5000):
        super(LeadCar2,self).__init__()
        self.hostname = socket.gethostname() # host is the lead car 
        self.hostname = ""
        print("lead car host name:",self.hostname)
        self.fol_cars = fol_cars
        self.conn_list = [None]
        self.port=port
        
        self.queue = queue.Queue()

        self.lead_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.lead_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lead_socket.bind((self.hostname,self.port))
        self.lead_socket.listen(fol_cars)

    def connect(self):
        '''
        connects lead car to followCars
        '''
        #creating socket for lead-pc connection
        self.threadList = []
        #creating sockets for each lead-follow connection
        
         #number of follow cars
        for i in range(self.fol_cars): #connect cars
            print("car",i)
            connector = threading.Thread(target = self.initConnect, args=(i,))
            self.threadList.append(connector)
            print("added to threadlist")
            #* need to implement: 
            # connector.start()
            # connector.join() #to make sure each thread finishes before proces
        
        

    def initConnect(self,idx):
        '''
        the initial connection process for lead - follow pair
        '''
        print("starting to listen for follow cars! at idx:",idx)
        # self.lead_socket.listen(1)
        print("listening for idx",idx)
        conn, addr = self.lead_socket.accept()
        print("accepted!")
        self.conn_list[idx] = (conn,addr)
        print("Successfully connected to",self.fol_cars,"follow-cars")
    
    def makeDecision(self):
        '''
        calculates and makes decision tuple
        ([wheel1,2,3,4],led,buzzer)
        '''
        frontDistance = self.get_distance()
        self.calculateLMR


        frame = capture()
        
        #sending to lane track
        offset = process_image_and_get_offset(frame)
        print("Offset:", offset)

        #sending to stop / face detection
        # processed_frame = frame_processor(frame)
    
        # # Apply region selection for objects
        # mask1 = region_selection_object(processed_frame)
        
        # # Detect faces
        # face_detected_frame = detect_faces(mask1)
        
        # # Detect stop signs
        # processed_frame = detect_stop_signs(face_detected_frame)

        # # Display the resulting frame
        # cv2.imshow('Frame', processed_frame)
        


        result = ()
        #put result in queue for the # of fol cars + delay
        self.queue.put(result)



        pass
    
    def run(self):
        #set initial states
        self.pwm_S.setServoPwm('0',90) #starts looking straight first 
        threshold = 15 #set to distance to emergency stop
        sf = 0.95 #the speed factor
        sleep = 0.3
        counter = 0
        wait = 30

        while True:
            
            for thread in self.threadList:
                thread.start()
                thread.join()
            print("counter",counter)

            #using khens function to get offset

            self.makeDecision()

            print("getting movement")
            movement = sQueue.get()

            ## send message to following cars
            # self.network.sendInstruction()

            ## run cars
    
# Main program logic follows:
if __name__ == '__main__':
    print ('Program is starting ... ')

    #connList is a list of all the hostnames of 
    connList = []

    car = LeadCar2(1)
    try:
        car.connect()
        car.run()
        
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program  will be  executed.
        PWM.setMotorModel(0,0,0,0)
        ledbuzz(led,buzzer,'end')
        print("issue! stopping")