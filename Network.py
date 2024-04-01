import socket
import time

class NetworkModule:
    def __init__(self,host,port = 5000):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #connecting to host @ port
        self.client_socket.connect((host,port))
        self.car_name = socket.gethostname()
        print("Successfully connected to host")

    def sendImage(self,path):
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
        self.client_socket.sendall(("SIZE %s" % size).encode()) #sending the size of the image
        print("Sent!")

        #received answer
        print("waiting for answer from server")
        answer  = self.client_socket.recv(4096).decode() #buffer size 4096
        
        print("answer = %s" % answer)
        
        if answer == 'GOT SIZE': #server received response
            self.client_socket.sendall(bytes)
            
            answer = self.client_socket.recv(4096).decode()
            print("answer = %s"%answer)

            if answer == "GOT IMAGE":
                self.client_socket.sendall("BYE".encode())
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
        message = "Test"
        for i in range(15):
            print(i,message)
            time.sleep(1)
            self.client_socket.send(message.encode())

        
        self.client_socket.close()

if __name__ =='__main__':
    netmodule = NetworkModule(host = "LAPTOP-2JG6DRO3")
    # netmodule.run()
    netmodule.sendImage('saved_frame.jpg')
    
