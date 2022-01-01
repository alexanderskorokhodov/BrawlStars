import socket
from commands import *  # commands
from json import loads


def get_player_info(sock):
    message = sock.recv(len(CMD_PLAYER_INFO_IN_MENU)).decode()
    if message == CMD_PLAYER_INFO_IN_MENU:
        data = sock.recv(32).decode()
        while data[-1] != Delimiter:
            data += sock.recv(32).decode()
        info = loads(data[:-1])
        return info


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (socket.gethostbyname(socket.gethostname()), 10000)
print('Подключено к {} порт {}'.format(*server_address))
sock.connect(server_address)
do = input("Log in or Registration?('log'/'reg')")
if do == 'log':
    login = input('Enter login:')
    while len(login) > 12 or len(login) == 0:
        print('Length of login must be between 1 and 12')
        login = input('Enter login:')
    password = input('Enter password:')
    while len(password) > 12 or len(password) == 0:
        print('Length of password must be between 1 and 12')
        password = input('Enter password:')
    sock.sendall((CMD_TO_LOG_IN + login + Delimiter + password).encode())
    print(sock.recv(max(len(CMD_RIGHT_PASSWORD), len(CMD_WRONG_PASSWORD))).decode())
    print(get_player_info(sock))
elif do == 'reg':
    login = input('Enter login:')
    while len(login) > 12 or len(login) == 0:
        print('Length of login must be between 1 and 12')
        login = input('Enter login:')
    password = input('Enter password:')
    while len(password) > 12 or len(password) == 0:
        print('Length of password must be between 1 and 12')
        password = input('Enter password:')
    nickname = input('Enter nickname:')
    while len(nickname) > 12 or len(nickname) == 0:
        print('Length of nickname must be between 1 and 12')
        nickname = input('Enter nickname:')
    sock.sendall((CMD_TO_REGISTRATION + login + Delimiter + password + Delimiter + nickname).encode())
    print(sock.recv(max(len(CMD_SUCCESSFUL_REGISTRATION), len(CMD_FAIL_REGISTRATION))).decode())
    print(get_player_info(sock))