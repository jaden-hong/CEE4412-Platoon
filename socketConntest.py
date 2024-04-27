import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((r"car1",5000))

print("succes!")