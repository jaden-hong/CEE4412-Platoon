import socket
import time
import threading
import queue

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput

'''
LeadModule is a class to communicate between lead to PC
and also between lead and follow. also includes all camera code

FollowModule is a class to communicate between follow to Lead Module
'''
class LeadModule:
    def __init__(self,laptop_hostname,connList,port=5000):
        ## socket for communicating with laptop
        self.laptop_hostname = laptop_hostname # host is the lead car 
        self.host = socket.gethostname()
        self.connList = connList #need to put in the ip addresses of: [laptop,lead1,fol1,fol2,..]
        self.conn_list = [None]
        self.port=port

        self.queue = queue.Queue()

        self.lead_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lead_socket.bind((self.host,self.port+1))

        #connList is list of all devices to be connected with details in order of:
        # [laptop.devicename,lead1.devicename,follow1.devicename,follow2.devicename,...]
        #leadList is list to be used to store sockets and their details:
        # [(socket.conn,socket.addr),...]

        

    def lead_fol_process(self,idx,connected = True,end = False):
        '''
        the process + protocols of lead car to follow car socket(s)
        idx is thread index
        movement = tuple of movement commands (pwm, led, buzzer)
        connect is whether or not its connected
        end is to break loop
        '''
        ## to initialize connection
        if connected==False: #only for the first lead car
            conn, addr = self.lead_socket.accept(1) #will accept 1 connection
            self.conn_list[idx] = (conn,addr)

        if end:
            self.lead_socket.close()

        #* regular processes *#
        # - needs to accept and send messages back and forth
        #get movement data

        movement = self.queue.get() #each thread will receive a movement string
        # movement = movement.decode('utf-8')

        self.conn_list[idx][0].send(movement)        


        data = self.connList[idx][0].recvall()
        if data: #message received: will be in format of tuple of the sensor data
            sensorData = str(data.decode('utf-8'))
            # self.queue.put()
            #* need to design the validation process
            #- if lead car pwm motor data does not match: need to do something LOL
            #if the ultrasonic data is 

    def fol_process(self,conn = True):
        '''
        the process + protocols of follow car to lead socket(s)
        '''
        if conn:
            pass

        pass
    
    def lead_laptop_process(self,idx=0,end=False,connected = True,szTuple = (1280,720),port=5000):
        '''
        the process + protocols of lead car to laptop socket(s)
        
        uses: https://github.com/raspberrypi/picamera2/blob/main/examples/capture_stream_udp.py
        '''
        
        if connected == False: #first time set up
            #setting up socket
            self.laptop_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.laptop_socket.bind((self.host,self.port))
            #connecting to laptop @ port
            self.laptop_socket.connect((self.laptop_host,port)) #default port 5000

            print("Successfully connected",self.host,"to laptop",self.laptop_host)

            #setting up streaming + camera
            picam2 = Picamera2()
            video_config = picam2.create_video_configuration({"size": szTuple})
            picam2.configure(video_config)
            encoder = H264Encoder(1000000)
            #sending stream data to laptop
            # self.laptop_sock.connect((self.laptop_hostname, 10001))
            stream = self.laptop_socket.makefile("wb")
            picam2.start_recording(encoder, FileOutput(stream))
        

        if end: #ending loop
            picam2.stop_recording()
            self.laptop_socket.close()
        
        #receiving data:
        data = self.connList[idx][0].recvall()
        if data: #message received: will be in format of tuple of the sensor data
            movement = str(data.decode('utf-8')) 
            for i in range(self.conn_list-2): #minus two accounting for laptop + lead
                self.queue.put(movement) #putting in queue so threads at idx 2+ can access, as each get removes from queue
            
            # movementData #will be tuple of pwm motors, led and buzzer    
            #need to take this data and pass to the main

    def connect(self):
        '''
        connects lead car to laptop
        connects lead car to followCars
        '''
        #creating socket for lead-pc connection
        self.threadList = []
        #creating sockets for each lead-follow connection
        
        totalConn = len(self.connList) #minus the lead and laptop
        for i in range(totalConn): #connect cars + laptop
            # follow_socket, follow_addr = self.lead_socket.accept()
            if i==0:
                connector = threading.Thread(target = self.lead_laptop_process, args = i)
            elif i>1:
                connector = threading.Thread(target = self.lead_fol_proccess, args=(i))
            self.threadList.append(connector)
            #* need to implement: 
            #connector.start()
            #connector.join() #to make sure each thread finishes before proces
        
        print("Successfully connected to",totalConn,"cars and laptop")


    def sendData(self,path,image,LMRdata,ultraData):
        '''
        for the lead car to send data

        https://stackoverflow.com/questions/42458475/sending-image-over-sockets-only-in-python-image-can-not-be-open
        '''
        image = path

        imageFile = open(image, 'rb') #rb - read binary
        bytes = imageFile.read()

        # if bytes[0] == b'\xff': return bytes[1:].decode('utf-16')

        size = len(bytes)
        # print(size)
        print("SIZE %s" % size)

        print("B4 sending")
        self.client_socket.sendall(("SIZE %s" % size).encode('utf-8')) #sending the size of the image
        print("Sent!")

        #received answer
        print("waiting for answer from server")
        answer  = self.client_socket.recv(4096).decode() #buffer size 4096
        
        print("answer = %s" % answer)
        # print(answer,answer=='GOT SIZE')
        if answer == 'GOT SIZE': #server received response
            print("sending image")
            self.client_socket.sendall(bytes)
            
            # answer = self.client_socket.recv(4096).decode()
            # print("answer = %s"%answer)

            if answer == "GOT IMAGE":
                self.client_socket.sendall("BYE".encode('utf-8'))
                print("Image send successful")

        pass
    def sendInstruction(self):
        '''
        for the lead car to send data to the following cars
        '''
        pass

    def receiveInstruction(self):
        '''
        for the following cars to receive instructions
        '''
        pass

    def run(self):
        # message = "Test"
        # for i in range(15):
        #     print(i,message)
        #     time.sleep(1)
        #     self.client_socket.send(message.encode())

        
        # self.client_socket.close()
        '''
        to start executing 
        '''
        

# class FollowModule(self)


if __name__ =='__main__':
    netmodule = LeadModule(host = "LAPTOP-2JG6DRO3")
    # netmodule.run()
    netmodule.sendImage('saved_frame.jpg')
    
