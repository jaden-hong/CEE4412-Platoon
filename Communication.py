import socket
import time

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
        print("Staring host at",self.host)
        self.port = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create new socket
        self.server_socket.bind((self.host,self.port))
    
        numCars = 0
        self.carList = []
        self.server_socket.listen(totalCars)
        while numCars < totalCars: #until all cars are connected
            
            conn, addr = self.server_socket.accept()
            self.carList.append([conn,addr])
            numCars+=1
        # print(self.carList)
        #connecting to the cars

    def process(self):
        self

    def communicate(self):
        '''
        Acts as the lead car.
        '''

        #can set a speed to update the car
        maxDataLength = 100000
        while True:
            for car in self.carList:                
                # accept incoming data from each lead car
                data = car[0].recv(maxDataLength) 
                #
                #data will be in either byte (for image) or string form
                if data:
                    try:
                        # where more complex handshaking and security would take place
                        text = str(data.decode('utf-8'))
                        # data is in strings

                        if text.startswith('SENSOR DATA READY'):
                            car[0].send(("SEND SENSOR DATA").encode('utf-8'))

                        elif text.startswith('BYE'): #
                            # car needs to stop (case when car leaves bounds or smth like that)
                            pass

                    except:
                        # data is in bytes
                        LMRdata = car[0].recv(4096) #other sensor data will be significantly less
                        ultraData = car[0].recv(4096)

                        # decision should be tuple representing the PWM motor params, LEDS and buzzer
                        decision = self.process(data,LMRdata,ultraData)

                        #send processed data 
                        car[0].send(decision)
            #next iteration:

                # send data back to each lead car

if __name__ == "__main__":
    Processing()