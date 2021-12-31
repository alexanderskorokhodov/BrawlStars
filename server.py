import socket
from commands import *  # commands
from threading import Thread
import sqlite3


def log_in(sock, id):

    def check_password(login, password):
        con = sqlite3.connect("BrawlStars.db")
        cur = con.cursor()
        result = cur.execute(f"""SELECT password FROM passwords WHERE login = '{login}'""").fetchone()
        con.close()
        print(result)
        if result is None:
            return False
        elif result[0] == password:
            return True
        else:
            return False

    def registration(login, password, nickname):
        con = sqlite3.connect("BrawlStars.db")
        cur = con.cursor()
        result = cur.execute(f"""SELECT login FROM passwords WHERE login = '{login}'""").fetchall()
        if result:
            con.close()
            return False
        else:
            cur.execute(
                f"""INSERT INTO passwords(login, password) VALUES('{login}', '{password}')""")
            cur.execute(f"""INSERT INTO players(login, nickname) VALUES('{login}', '{nickname}')""")
            con.commit()
            con.close()
            return True

    try:
        print('connected with ' + str(id))
        successful_authorization = False
        while not successful_authorization:
            mes = sock.recv(4).decode()
            # log command
            if mes == CMD_TO_LOG_IN:
                data = sock.recv(25).decode()
                try:
                    login, password = data.split(Delimiter)
                    print(login, password)
                    if check_password(login, password):
                        sock.sendall(CMD_RIGHT_PASSWORD.encode())
                        successful_authorization = True
                        break
                    else:
                        sock.sendall(CMD_WRONG_PASSWORD.encode())
                except ValueError:
                    sock.close()
                    break
            # registration command
            elif mes == CMD_TO_REGISTRATION:
                data = sock.recv(38).decode()
                try:
                    login, password, nickname = data.split(Delimiter)
                    print(login, password, nickname)
                    if registration(login, password, nickname):
                        sock.sendall(CMD_SUCCESSFUL_REGISTRATION.encode())
                        successful_authorization = True
                        break
                    else:
                        sock.sendall(CMD_FAIL_REGISTRATION.encode())
                except ValueError:
                    sock.close()
                    break
            else:
                sock.close()
                break

        if successful_authorization:
            pass
            # next game logic
    except ConnectionError:
        sock.close()


if __name__ == '__main__':

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # server address
    server_address = (socket.gethostbyname(socket.gethostname()), 10000)

    print('Старт сервера на {} порт {}'.format(*server_address))
    sock.bind(server_address)
    sock.listen(10)

    while True:
        connection, client_address = sock.accept()
        thr = Thread(target=log_in, args=(connection, client_address))
        thr.start()
