from BaseCar import *
from Network import LeadModule
from sharedQueue import sQueue #squeue used to access instructions
import queue
import threading

#edit laptop_hostname to be name of host laptop (leadLaptop.py

class LeadCar(BaseCar):
    def __init__(self,connList, port = 5000):
        super(LeadCar,self,).__init__()
        self.hostname = socket.gethostname() # host is the lead car 
        self.connList = connList #need to put in the ip addresses of: [laptop,lead1,fol1,fol2,..]
        self.conn_list = [None]
        self.port=port
        
        self.queue = queue.Queue()

        self.lead_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lead_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        '''
        connects lead car to followCars
        '''
        #creating socket for lead-pc connection
        self.threadList = []
        #creating sockets for each lead-follow connection
        
        totalConn = len(self.connList) #number of follow cars
        for i in range(totalConn): #connect cars
            connector = threading.Thread(target = self.initConnect, args=(i))
            self.threadList.append(connector)
            #* need to implement: 
            #connector.start()
            #connector.join() #to make sure each thread finishes before proces
        
        print("Successfully connected to",totalConn,"cars and laptop")

    def initConnect(self,idx):
        '''
        the initial connection process for lead - follow pair
        '''
        self.lead_socket.listen(1)
        conn, addr = self.lead_socket.accept(1) #will accept 1 connection
        self.conn_list[idx] = (conn,addr)
    
    def LMRdecision(self,sf):
        '''
        calculates the LMR and provides a decision
        '''
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
            print("counter",counter)

            ##get sensor information:
            frontDistance = self.get_distance()
            self.calculateLMR()
            #using khens function to get offset


            LMRdata = self.LMR


            



            # self.network.receiveInstruction()
            print("getting movement")
            movement = sQueue.get()

            ## send message to following cars
            # self.network.sendInstruction()

            ## run cars 

            counter+=1
            if counter%wait==0:
                print("NEXT ITERATION")
                print("Front distance",frontDistance)
            # self.calculateLMR()
            
            
            print('car decision making')
            #whenever the car is able to go and drive
            if frontDistance>threshold: #for emergency braking
                ledbuzz(led,buzzer,"drive")
                
                # based off decision tuple, update parameters of car:
                #
                #self.PWM.setMotorModel()
                #ledbuzz(led,buzzer,status)
                print(movement)
                self.PWM.setMotorModel(1000,1000,1000,1000)

                # self.PWM.
                if counter%wait==0:
                    print("Car moving forwards")

            #when car should stop
            if frontDistance<=threshold:
                # if flag==False:
                self.PWM.setMotorModel(0,0,0,0)
                ledbuzz(led,buzzer,"stop")
                if counter%wait==0:
                    print("Car stopped")
                    
                #calls the avoiding when vehicle is detected
                # flag = self.avoidProcedure()
                

            #feedback for current state

    
# Main program logic follows:
if __name__ == '__main__':
    print ('Program is starting ... ')
    # laptop_hostname = r"LAPTOP-2JG6DRO3"
    laptop_hostname = r"JADENPC_2024"
    car = LeadCar(laptop_hostname)
    try:
        car.run()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program  will be  executed.
        PWM.setMotorModel(0,0,0,0)
        ledbuzz(led,buzzer,'end')
        print("issue! stopping")