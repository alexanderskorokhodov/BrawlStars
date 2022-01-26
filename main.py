import menuWindow
import startWindow
import mainGame

sock = None
extra_message = ''
login, password = None, None
try:
    run = "reg"
    while run:
        if run == "reg":
            run, sock, login, password = startWindow.main()
        elif run == "menu":
            run, sock, extra_message = menuWindow.main(sock, extra_text=extra_message)
        elif run == "game":
            in_game = True
            try:
                run, sock, brawler, screen, place, extra_message = mainGame.main(sock, extra_message, login)
                print(extra_message, 111)
                run, sock = mainGame.end(sock, brawler, place, screen)
            except ConnectionError:
                startWindow.server_error_window()
                run = "menu"
        elif run == "play_again":
            run, sock, extra_message = menuWindow.main(sock, play_again=True, extra_text=extra_message)
        else:
            run = "reg"
except:
    pass
