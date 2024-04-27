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
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.socket.connect((self.lead_hostname,self.port))
        print("succesfully connected to",self.lead_hostname,self.port)

        self.receiver = threading.Thread(target = self.receive)
        self.queue = queue.Queue()

    def receive(self):
        '''
        the receiving process for lead - follow pair
        '''
        movement = self.socket.recv(4096000)
        self.queue.put(movement)


    def run(self):
        print("Starting run loop")
        while True:
            self.receiver.start()
            self.receiver.join()
            print('getting from queue')
            movement = self.queue.get()
            print("movement:",movement)
            if changeMove: #if the follow car deviates from what instructions are given
                self.socket.send(currentMove) 
            else:
                sQueue.put(movement) #continue transmitting instructions

        pass



# Main program logic follows:
if __name__ == '__main__':
    print ('Program is starting ... ')
    lead_hostname = r"car1" #put the name of the lead car in here
    car = FollowCar(lead_hostname)
    try:
        car.run()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program  will be  executed.
        PWM.setMotorModel(0,0,0,0)
        ledbuzz(led,buzzer,'end')