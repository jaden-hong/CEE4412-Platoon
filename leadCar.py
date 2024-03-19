from BaseCar import *

class LeadCar(BaseCar):
    def __init__(self):
        super(LeadCar,self).__init__()

    def LMRdecision(self,sf):
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

            ledBuzz(led,buzzer)
            PWM.setMotorModel(0,0,0,0)
            time.sleep(1.0)
            self.intersectionProcedure()
        

    def run(self):
        #set initial states
        self.pwm_S.setServoPwm('0',90) #starts looking straight first 
        threshold = 15 #set to distance the how early to start lane procedure
        sf = 0.95 #the speed factor
        sleep = 0.3

        # flag = False
        while True:
            print("NEXT ITERATION")
            # self.calculateLMR()
            
            frontDistance = self.get_distance()
            print("Front distance",frontDistance)

            #whenever the car is able to go and drive
            if frontDistance>threshold:
                ledbuzz(led,buzzer,"drive")
                # self.LMRdecision(sf)
                self.PWM.setMotorModel(1000,1000,1000,1000)
                print("Car moving forwards")
            #when car should stop
            if frontDistance<=threshold:
                # if flag==False:
                self.PWM.setMotorModel(0,0,0,0)
                ledbuzz(led,buzzer,"stop")
                print("Car stopped")
                    
                #calls the avoiding when vehicle is detected
                # flag = self.avoidProcedure()
                

            #feedback for current state

    '''
    drive ->
    if there is no object infront
        continue along path 


        if fork in road ( the LMR = 7):
            turn right or left according to logic



        
    if object infront:
        assume object dimensions are n x n:
        turn car right, move n cm
        turn car left move n cm
        turn car left move n cm
        turn car right, continue as usual
    
    

    
    # def turnInPlace(self,dir):
    #     print('TURNING IN PLACE')
    #     # dir = 1 #direction factor
    #     # if direction == "L":
    #     #     dir = -1
        
    #     PWM.setMotorModel(dir * 1500, dir * 1500, dir * -1500, dir * -1500)
    #     time.sleep(3.0)

    def intersectionProcedure(self):
        #scanning to check and make sure there are no objects
        threshold = 30
        stop = True
        while stop:
            #assuming that intersection is clear each loop
            objectDetect = False
            for i in range(0,180,20):
                self.pwm_S.setServoPwm('0',i)
                time.sleep(0.2)
                dist = self.get_distance()
                print(dist)
                if dist < threshold:
                    objectDetect = True
            # print("object detected: ",objectDetect)
            if objectDetect:
                stop = True
            else:
                stop = False

        #now the intersection is clear !
        #assuming that car is perfectly aligned:
        
        PWM.setMotorModel(1000,1000,1000,1000)
        time.sleep(0.3)
        while True:
            self.LMR=0x00
            if GPIO.input(self.IR01)==True:
                self.LMR=(self.LMR | 4)
            if GPIO.input(self.IR02)==True:
                self.LMR=(self.LMR | 2)
            if GPIO.input(self.IR03)==True:
                self.LMR=(self.LMR | 1)

            print('driving thru Intersection',self.LMR)
            self.pwm_S.setServoPwm('0',90)
            
            
            #assuming that car is perfectly aligned:
            PWM.setMotorModel(1000,1000,1000,1000)
            
            if self.LMR == 7:
                break

        
    
    def avoidProcedure(self):
        print('avoid PROCEDURE')
        buzzerAvoid(led,buzzer)
        #need to callibrate
        manueverTime = 0.75
        forwardTime1 = 0.5
        forwardTime2 = 0.25
        sf = 1.2

        # iter 2. 
        # will assume line is straight through the obstacle

        #car turns right
        # PWM.setMotorModel( 0, 4000, 4000, 0)
        PWM.setMotorModel(int(sf*-1500),int(sf*-1500),int(sf*2500),int(sf*2500))
        print('car diagonally left')
        time.sleep(manueverTime)
    
        #car turns left
        PWM.setMotorModel(int(sf*2500),int(sf*2500),int(sf*-1500),int(sf*-1500))
        print('car diagonally rightfr')
        time.sleep(manueverTime)

        PWM.setMotorModel(700,700,700,700)
        time.sleep(forwardTime1)

        #car turns left
        PWM.setMotorModel(int(sf*2500),int(sf*2500),int(sf*-1500),int(sf*-1500))
        print('car diagonally right')
        time.sleep(manueverTime)

        PWM.setMotorModel(700,700,700,700)
        time.sleep(forwardTime2)

        PWM.setMotorModel(int(sf*-1500),int(sf*-1500),int(sf*2500),int(sf*2500))
        print('car diagonally left')
        time.sleep(manueverTime)
        return True
'''
car = LeadCar()
# Main program logic follows:
if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        car.run()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program  will be  executed.
        PWM.setMotorModel(0,0,0,0)
        ledBuzz(led,buzzer,'end')