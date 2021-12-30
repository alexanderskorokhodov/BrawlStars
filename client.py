import socket
from commands import *  # commands

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (socket.gethostbyname(socket.gethostname()), 10000)
print('Подключено к {} порт {}'.format(*server_address))
sock.connect(server_address)
login = input('Enter login:')
while len(login) > 12 or len(login) == 0:
    print('Length of login must be between 1 and 12')
    login = input('Enter login:')
password = input('Enter password:')
while len(password) > 12 or len(password) == 0:
    print('Length of password must be between 1 and 12')
    password = input('Enter password:')
sock.sendall((CMD_TRY_TO_ACCESS + login + Delimiter + password).encode())
print(sock.recv(max(len(CMD_RIGHT_PASSWORD), len(CMD_WRONG_PASSWORD))).decode())