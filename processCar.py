from BaseCar import *
#from Network import *
from Communication import *
from Network import NetworkModule
from picamera2 import Picamera2

## imports for image processing
import numpy as np
import pandas as pd
import cv2

import time 


class ProcessCar(BaseCar):
    def __init__(self,host, port = 5000,):
        super(ProcessCar,self,).__init__()
        self.network = NetworkModule(host,port)

    def LMRdecision(self,sf):
        '''
        function to take in the 
        
        '''
        print("")
        print("Driving, The lmr is:",self.LMR)

        # LMR 1,2,3,4,5,6,7
        # 2 will never occur

        if self.LMR==0:
            #if lmr = 0, all sensors detect low 
            PWM.setMotorModel(int(sf*700),int(sf*700),int(sf*700),int(sf*700))
            # print('forwards')
            # moving forwards 
        elif self.LMR==4: #detect Left
            #slight turn to the RIGHT
            PWM.setMotorModel(int(sf*2500),int(sf*2500),int(sf*-1500),int(sf*-1500))
            time.sleep(sleep)
            
        elif self.LMR==6: #detect Left + Middle
            #turn to RIGHT
            PWM.setMotorModel(int(sf*4000),int(sf*4000),int(sf*-2500),int(sf*-2500))
            time.sleep(sleep)

        elif self.LMR==1: #detect Right
            #slight turn to LEFT
            PWM.setMotorModel(int(sf*-1500),int(sf*-1500),int(sf*2500),int(sf*2500))
            time.sleep(sleep)

        elif self.LMR==3: #detect Right + Middle
            #turn LEFT
            PWM.setMotorModel(int(sf*-2500),int(sf*-2500),int(sf*4000),int(sf*4000))
            time.sleep(sleep)

        elif self.LMR==7 or self.LMR == 5:
            #all sensors are detected: fork detected #or fork detected
            print("Intersection detected!")

            ledbuzz(led,buzzer)
            PWM.setMotorModel(0,0,0,0)
            time.sleep(1.0)
            self.intersectionProcedure()
        

    def run(self):
        #set initial states
        self.pwm_S.setServoPwm('0',90) #starts looking straight first 
        threshold = 15 #set to distance to emergency stop
        sf = 0.95 #the speed factor
        sleep = 0.3
        counter = 0
        wait = 30
        # flag = False
        while True:

            ##get sensor information:
            frontDistance = self.get_distance()
            picam2 = Picamera2()
            startTime=time.time()
            picam2.start_and_capture_file("image.jpg")

            self.getVector()

            self.calculateLMR()
            # LMRdata = self.LMR

            # ## send data to host laptop:
            # # self.communications.send(image,LMRdata = self.LMR,ultraData = frontDistance)
            # self.network.sendData(image,LMRdata=self.LMR,ultraData=frontDistance)


            # ## receive message from host laptop
            # #
            # self.network.receiveInstruction()

            # ## send message to following cars
            # self.network.sendInstruction()

            ## run cars 

            counter+=1
            if counter%wait==0:
                print("NEXT ITERATION")
                print("Front distance",frontDistance)
            # self.calculateLMR()
            
            

            #whenever the car is able to go and drive
            if frontDistance>threshold: #for emergency braking
                ledbuzz(led,buzzer,"drive")
                
                # based off decision tuple, update parameters of car:
                #
                #self.PWM.setMotorModel()
                #ledbuzz(led,buzzer,status)

                self.PWM.setMotorModel(1000,1000,1000,1000)

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

    # def getVector():
        

car = ProcessCar()
# Main program logic follows:
if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        car.run()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program  will be  executed.
        PWM.setMotorModel(0,0,0,0)
        ledbuzz(led,buzzer,'end')