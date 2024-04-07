import socket

class ImageProcess:
    def __init__(self,port = 5000,totalCars=1):
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
        


    def run(self):
        imagePath = 'saved_frame1.jpg'
        while True:
            # now listening 
            print("waiting for message from client")
            emptyData = 0
            for car in self.carList:
                # print(data)
                data = car[0].recv(40960000)#.decode('utf-8') #limit of 1024 bytes
                # text = str(data)
                # print(data,text)
                # text = str(data)
                # print(data)

                # if not data: #printing any data that is sent
                #     emptyData+=1
                #     pass
                # else:
                #     print("from car:",car[1][0],"at port",car[1][1]," Data:",data)
                # else:
                if data:
                    # print(str(data.decode('utf-8')))
                    print(len(data))
                    
                    try:
                        text = str(data.decode('utf-8'))
                        if text.startswith('SIZE'):
                            tmp = str(data.decode('utf-8')).split()
                            size = int(tmp[1])

                            #bruh why do we even need this
                            print('GOT SIZE')

                            car[0].send(("GOT SIZE").encode('utf-8'))

                        elif text.startswith('BYE'):
                            print("GOT BYE")
                            emptyData+=1
                            # car[0].shutdown(socket.SHUT_RDWR)
                    except:
                        print("no other option, recv. an image then")
                        myfile = open(imagePath, 'wb')

                        # data = car[0].recv(409600000)#.decode('utf-8', 'ignore')
                        if not data:
                            print("NO DATA")
                            myfile.close()
                            break
                        myfile.write(data)
                        myfile.close()
                        print("SENDING : GOT IMAGE")
                        car[0].send(("GOT IMAGE").encode())
                        emptyData+=1
                    # if str(data.decode('utf-8')).startswith('SIZE'):
                    #     tmp = str(data.decode('utf-8')).split()
                    #     size = int(tmp[1])

                    #     print('GOT SIZE')

                    #     car[0].send(("GOT SIZE").encode('utf-8'))

                    # elif str(data.decode('utf-8')).startswith('BYE'):
                    #     print("GOT BYE")
                    #     emptyData+=1
                    #     # car[0].shutdown(socket.SHUT_RDWR)

                    # else:
                    #     print("no other option, recv. an image then")
                    #     myfile = open(imagePath, 'wb')

                    #     data = car[0].recv(409600000)#.decode('utf-8', 'ignore')
                    #     if not data:
                    #         myfile.close()
                    #         break
                    #     myfile.write(data)
                    #     myfile.close()

                    #     car[0].send(("GOT IMAGE").encode())
                    #     # self.server_socket.shutdown()

            if emptyData == len(self.carList):
                break # no data is received
        
        print("Finished!")
        for car in self.carList:
            car[0].close() #closing connection 
            # car[0].shutdown(socket.SHUT_RDWR)


    # def sendMsg(self,message):
        
if __name__=="__main__":
    ImageProcess().run()