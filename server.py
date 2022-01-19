import socket
from commands import *  # commands
from threading import Thread
import sqlite3
from json import dumps
from time import sleep
from pygame.sprite import Group


# for any func without log_in()
def close_connection(login):
    players[login].close()
    del players[login]
    print('disconnected with ' + login)


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
        sock.setblocking(True)
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
            players[login] = sock
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
    try:
        player_info = get_player_info(login)
        sock.setblocking(True)
        sock.sendall((CMD_PLAYER_INFO_IN_MENU + dumps(player_info) + Delimiter).encode())
        mes = sock.recv(10).decode()
        if len(mes) == 0:
            close_connection(login)
        elif mes[-1] == Delimiter:
            if mes.startswith(CMD_FIND_MATCH):
                try:
                    event_id = int(mes[len(CMD_FIND_MATCH)])
                    brawler_id = int(mes[len(CMD_FIND_MATCH) + 1:-1])
                    if check_player_brawler(login, brawler_id):
                        rooms[event_id].append((login, brawler_id))
                        sock.sendall((CMD_PLAYERS_IN_ROOM + '1/10' + Delimiter).encode())
                        if len(rooms[event_id]) == 1:
                            match_finder(event_id)
                    else:
                        close_connection(login)
                except ValueError:
                    close_connection(login)

            # maybe another command in future
            elif False:
                pass
            else:
                close_connection(login)

        else:
            close_connection(login)
    except ConnectionError:
        close_connection(login)


def match_finder(event_id):
    sleep(1)
    number_of_players = len(rooms[event_id])
    while rooms[event_id]:
        try:
            if len(rooms[event_id]) >= amount_of_players_for_event[event_id]:
                room = []
                for i in range(amount_of_players_for_event[event_id]):
                    players[rooms[event_id][i][0]].sendall((CMD_PLAYERS_IN_ROOM + '10/10' + Delimiter).encode())
                    room.append(rooms[event_id][i])
                for i in room:
                    rooms[event_id].remove(i)
                thr = Thread(target=game_funcs[event_id], args=(room,))
                thr.start()
            else:
                # if len(rooms[event_id]) != number_of_players:
                number_of_players = len(rooms[event_id])
                for i in range(len(rooms[event_id])):
                    players[rooms[event_id][i][0]].sendall(
                        (CMD_PLAYERS_IN_ROOM + f'{number_of_players}/10' + Delimiter).encode())
                sleep(1)
        except ConnectionError:
            close_connection(rooms[event_id][i][0])
            rooms[event_id].remove(rooms[event_id][i])


def showdown_game(room: list):

    # init
    from ServerClasses import cell_size, Wall, Bush, Skeletons, Chest, PowerCrystal, Shelly
    print(room)
    print('game_starts')

    map_name = 'RockwallBrawl.txt'

    for player in room:
        players[player[0]].setblocking(False)
        try:
            players[player[0]].sendall(CMD_GAME_map + map_name + Delimiter)
        except ConnectionError:
            close_connection(player[0])
            room.remove(player)

    brawlers = {}  # {login : BrawlerClass}
    players_start_cords = []  # [(x, y)]

    brawlers_group = Group()
    walls_group = Group()
    breakable_blocks = Group()

    # map import
    with open('data/maps/' + map_name) as file:
        lines = file.readlines()
    for x in range(len(lines)):
        for y in range(len(lines[x])):
            if lines[x][y] == 'X':
                Bush(x * cell_size, y * cell_size, breakable_blocks)
            elif lines[x][y] == '#':
                Wall(x * cell_size, y * cell_size, walls_group, breakable_blocks)
            elif lines[x][y] == 'P':
                players_start_cords.append((x * cell_size, y * cell_size))


    # import brawlers
    con = sqlite3.connect("BrawlStars.db")
    cur = con.cursor()
    for index, i in enumerate(room):
        brawler_name = cur.execute(f'''SELECT name FROM brawlers WHERE id = {i[1]}''').fetchone()[0]
        if brawler_name == 'shelly':
            brawlers[i[0]] = Shelly(players_start_cords[index][0], players_start_cords[index][1], brawlers_group)
    print(brawlers['sasha'].speed)


if __name__ == '__main__':

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (socket.gethostbyname(socket.gethostname()), 10000)
    print('Старт сервера на {} порт {}'.format(*server_address))
    sock.bind(server_address)
    sock.listen(10)

    # events: showdown(event_id = 0)
    rooms = [[]]  # list of rooms where players are waiting match, ind = event_id
    players = {}  # players[player_login] = player socket
    amount_of_players_for_event = {0: 1}  # amount_of_players_for_event[event_id] = amount_of_players
    game_funcs = [showdown_game]  # game_funcs[event_id] = func for this event

    while True:
        connection, client_address = sock.accept()
        thr = Thread(target=log_in, args=(connection, client_address))
        thr.start()
