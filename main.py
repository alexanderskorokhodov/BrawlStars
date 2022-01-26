import menuWindow
import startWindow
import mainGame


sock = None
extra_message = None
login, password = None, None
brawler = "shelly"
run = "reg"
while run:
    try:
        if run == "reg":
            run, sock, login, password = startWindow.main()
        elif run == "menu":
            run, sock, extra_message = menuWindow.main(sock, login, password, brawler)
        elif run == "game":
            try:
                run, sock, brawler, screen, place, extra_message = mainGame.main(sock, extra_message, login)
                run, sock, extra_message = mainGame.end(sock, brawler, place, screen, extra_message)
            except ConnectionError:
                startWindow.server_error_window()
                run = "reg"
        elif run == "play_again":
            run, sock, extra_message = menuWindow.main(sock, login, password, brawler, play_again=True)
        else:
            run = False
    except:
        run = "reg"
