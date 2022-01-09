import socket
from commands import *  # commands
from threading import Thread
import sqlite3
from json import dumps


def log_in(sock, id):

    def check_password(login, password):
        con = sqlite3.connect("BrawlStars.db")
        cur = con.cursor()
        result = cur.execute(f"""SELECT password FROM passwords WHERE login = '{login}'""").fetchone()
        con.close()
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
            cur.execute(f"""INSERT INTO players_brawlers(login, brawler_id, cups, power, power_points) VALUES('{login}', 1, 0, 1, 0)""")
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
            menu(sock, id, login)
    except ConnectionError:
        sock.close()


def menu(sock, id, login):

    def get_player_info(login):
        info = {}
        con = sqlite3.connect("BrawlStars.db")
        cur = con.cursor()
        for item in ('nickname', 'money', 'all_cups'):
            info[item] = cur.execute(f"""SELECT {item} FROM players WHERE login = '{login}'""").fetchone()[0]
        info['brawlers'] = {}
        for i in cur.execute(f"""SELECT brawler_id FROM players_brawlers WHERE login = '{login}'""").fetchall():
            info['brawlers'][cur.execute(f"""SELECT name FROM brawlers WHERE id = {i[0]}""").fetchone()[0]] = cur.execute(f"""SELECT cups, power, power_points, brawler_id FROM players_brawlers WHERE brawler_id = {i[0]} AND login = '{login}'""").fetchone()
        con.close()
        return info

    def check_player_brawler(login, id):
        con = sqlite3.connect("BrawlStars.db")
        cur = con.cursor()
        if cur.execute(f"""SELECT id FROM players_brawlers WHERE brawler_id = {id} AND login = '{login}'""").fetchone() is None:
            con.close()
            return False
        else:
            con.close()
            return True

    player_info = get_player_info(login)
    print(dumps(player_info))
    sock.sendall((CMD_PLAYER_INFO_IN_MENU + dumps(player_info) + Delimiter).encode())
    mes = sock.recv(10).decode()
    if mes[-1] == Delimiter:
        if mes.startswith(CMD_TO_LOG_IN):
            try:
                event_id = int(mes[len(CMD_FIND_MATCH)])
                brawler_id = int(mes[len(CMD_FIND_MATCH) + 1:-1])
                if check_player_brawler(login, brawler_id):
                    print('starts to find math for ' + login)
                else:
                    sock.close()
            except ValueError:
                sock.close()
    else:
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
