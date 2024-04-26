import socket


def client_program():
    # host = socket.gethostname()  # as both code is running on same pc

    # clientHost = socket.gethostname()
    # clientPort = 5001

    serverPort = 5000  # socket server port number
    serverHost = r"ASUS-ROG-Strix-G15" #name of the server host (from print(socket.gethostname()))
    
    # client_socket = socket.socket((clientHost,clientPort))  # instantiate
    client_socket = socket.socket()
    client_socket.connect((serverHost, serverPort))  # connect to the server

    message = input(" -> ")  # take input

    while message.lower().strip() != 'bye':
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(5000).decode()  # receive response

        print('Received from server: ' + data)  # show in terminal

        message = input(" -> ")  # again take input

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()