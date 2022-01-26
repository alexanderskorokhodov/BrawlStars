import menuWindow
import startWindow

sock = None
extra_message = None
login, password = None, None
try:
    run = "reg"
    while run:
        if run == "reg":
            run, sock, login, password = startWindow.main()
        elif run == "menu":
            run, sock, extra_message = menuWindow.main(sock, login, password)
        elif run == "game":
            in_game = True
            try:
                import mainGame
                run, sock, brawler, screen, place, extra_message = mainGame.main(sock, extra_message, login)
                run, sock, extra_message = mainGame.end(sock, brawler, place, screen, extra_message)
            except ConnectionError:
                startWindow.server_error_window()
                run = "menu"
        elif run == "play_again":
            run, sock, extra_message = menuWindow.main(sock, login, password, play_again=True)
        else:
            run = "reg"
except:
    pass
