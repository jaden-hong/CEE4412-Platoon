from BaseCar import *
from Network import LeadModule
from sharedQueue import sQueue #squeue used to access instructions
import queue
import threading
from AutoDriveDraft import * #capture, region_selection_road, process_image_and_get_offset
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
        self.syncList = [None] #when all platoon cars are under same command

        self.lead_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lead_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lead_socket.bind((self.hostname,self.port))
        self.lead_socket.listen(fol_cars)
        self.threadDelay = 0.25
        

    def exit(self):
        '''
        incase of crash: to handle gracefully!
        '''
        self.lead_socket.close() #closing main socket
        for c in self.conn_list:
            c[0].close() #closing each lead-fol connection


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
            self.initConnect(i)
            comms = threading.Thread(target = self.communicate, args=(i,))
            self.threadList.append(comms)
            print("added to threadlist")
            #* need to implement: 
            # connector.start()
            # connector.join() #to make sure each thread finishes before proces
        
    def communicate(self,i): #will be run in thread
        #need to place all functions that wait on response from follow cars
        socket_lock = threading.Lock()
        counter = 0
        with socket_lock: #to make sure only one socket accesses at a time
            while(True): #thread will keep running 
                print("---THREAD---: looping",counter)
                counter+=1
                # print('___________________B4 movement______________')
                movement = self.queue.get()

                str_movement = tuple(str(num) for num in movement)
                # converting to integer

                # print('___________________B4 data______________')
                data = ';'.join(str_movement).encode()

                # print(self.conn_list[i],[0],self.conn_list[i][0])
                self.conn_list[i][0].send(data)


                # for conn in self.conn_list:
                # print("receiving fol car #",i,", sync status")
                # print('___________________B4 recv______________')
                data = self.conn_list[i][0].recv(4096000).decode() # will receive the movement commands
                
                # if self.in_sync == True: #none are out
                print("data:",data)
                # print("data[0:4]",data[0:4])
                if data[0:4] == "stop": #
                    print("follow car stopped!")
                    self.syncList[i] = False
                else: #data would be "sync"
                    self.syncList[i] = True
                # time.sleep(self.threadDelay)
                # else:



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
    
    def makeDecision(self,threshold=15): #oldMovement
        '''
        calculates and makes decision tuple
        (wheel1,2,3,4)
        threshold in cm, how far away to stop car
        '''
        frontDistance = self.get_distance()
        self.calculateLMR
        frame = capture()

        
        #sending to lane track
        offset = process_image_and_get_offset(frame)
        

        if offset is None:
            offset=0

        print("Offset:", offset,"Distance:",frontDistance,"q-size:",self.queue.qsize())
        if frontDistance>threshold:
            if offset>350:
                movement = (2000, 2000, -1000, -1000)

            elif offset<-350:
                movement = (-1000, -1000, 2000, 2000)
            else:
                movement = (750, 750, 750, 750)
        else:
            movement = (0,0,0,0) #car stopped
        
        # if oldMovement!=movement:
        #     #change! must delay all the follow cars so they keep running 
        #     self.change = True
        # else:
        #     self.change = False

        

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
        
        #put result in queue for the # of fol cars + delay
        # for i in range(self.fol_cars):
        # self.queue.put(movement)


        return movement

    def run(self):
        #set initial states
        self.pwm_S.setServoPwm('0',90) #starts looking straight first 
        threshold = 30 #set to distance to emergency stop
        sf = 0.95 #the speed factor
        sleep = 0.3
        counter = 0
        # wait = 30
        sync = True
        movement = (0,0,0,0) #default state
        oldMovement = movement
        for thread in self.threadList:
            thread.start()

        while True:
            # for thread in self.threadList:
            #     thread.start()
            # for thread in self.threadList:
            #     thread.join()


            #using khens function to get offset

            # print("getting movement")
            
            movement = self.makeDecision(threshold=threshold)#,oldMovement = oldMovement)
            # oldMovement = movement
            # print("movement:",movement)

            for s in self.syncList: #making sure all cars are in sync
                if s==False:
                    sync = False
                    break
                else:
                    sync = True
            
            if sync:
                PWM.setMotorModel(*movement) #unpacking into args
            else:
                PWM.setMotorModel(0,0,0,0) #case where car should stop since out of sync
            print("C:",counter,"sync:",sync,"movement:",movement)
            counter+=1

            #putting into queue 
            # if self.change and oldMovement == (0,0,0,0):
            #     print("SLEEPING_--------------------------------------------------")
            #     time.sleep(1.25)
            self.queue.put(movement)

            # movement = sQueue.get()

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
        print("\Interrupted!")

    except Exception as e:
        print("Error:",e)

    finally:
        PWM.setMotorModel(0,0,0,0)
        ledbuzz(led,buzzer,'end')
        car.exit()
        picam2.close()
        

        
