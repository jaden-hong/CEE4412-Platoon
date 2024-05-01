from BaseCar import *
import threading
import queue
# from Network import FollowModule
# from sharedQueue import sQueue

class FollowCar(BaseCar):
    def __init__(self,lead_hostname, port = 5000,):
        super(FollowCar,self).__init__()
        self.lead_hostname = lead_hostname
        self.host = socket.gethostname()
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create new socket
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.socket.connect((self.lead_hostname,self.port))
        print("succesfully connected to",self.lead_hostname,self.port)

        self.receiver = threading.Thread(target = self.receive)
        self.sender = threading.Thread(target = self.sendLead)
        self.queue = queue.Queue()
        self.messageQueue = queue.Queue()

    def exit(self):
        '''
        incase of crash: to handle gracefully!
        '''
        self.socket.close() #closing main socket

    def receive(self):
        '''
        the receiving process for lead - follow pair
        '''
        movement = self.socket.recv(4096000).decode()
        #converting back to integer
        int_movement = tuple(int(num) for num in movement.split(';'))

        self.queue.put(movement)
    
    def sendLead(self):
        '''
        sending message to lead car ( whenever fol car has to stop)
        '''
        
        message = self.messageQueue.get()
        print('sending message ',message,'to lead car!')
        self.socket.send(message.encode())

    def run(self):
        print("Starting run loop")
        threshold = 15
        # changeMove = False
        movement = (0,0,0,0)
        counter = 0
        frontDistance = self.get_distance()
        self.receiver.start()
        self.sender.start()
        # self.receiver.join()

        while True:
            print("counter:",counter)
            counter+=1
            if frontDistance>threshold:

                print('getting from queue')
                movement = self.queue.get()
                print("queue movement:",movement)
                print('putting into message queue, "sync"')
                self.messageQueue.put("sync")
            else: #something wrong on follow car side
                movement = (0,0,0,0)
                #two cases: 1 is ultrasonic sensor, 2 is pwm sensor, for now we only care for case 1
                self.messageQueue.put("stop")

            print(movement)
            print(*movement)
            PWM.setMotorModel(*movement)
            #checking if collision / etc.
            
            # oldMovement = movement
            # if oldMovement!=movement: #if the follow car deviates from what instructions are given
            #     self.socket.send(movement) 
            # else:
            #     # sQueue.put(movement) #continue transmitting instructions
            #     print("change movemnet")


# Main program logic follows:
if __name__ == '__main__':
    print ('Program is starting ... ')
    lead_hostname = r"car1" #put the name of the lead car in here
    car = FollowCar(lead_hostname)
    try:
        car.run()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program  will be  executed.
        print("\Interrupted!")

    except Exception as e:
        print("Error:",e)

    finally:
        PWM.setMotorModel(0,0,0,0)
        ledbuzz(led,buzzer,'end')
        car.exit()