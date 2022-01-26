import menuWindow
import startWindow
import mainGame


sock = None
extra_message = ''
login, password = None, None
brawler = "shelly"
run = "reg"
while run:
    try:
        if run == "reg":
            run, sock, login, password = startWindow.main()
        elif run == "menu":
            run, sock, extra_message = menuWindow.main(sock, brawler, extra_text=extra_message)
        elif run == "game":
            try:
                run, sock, brawler, screen, place, extra_message = mainGame.main(sock, extra_message, login)
                run, sock = mainGame.end(sock, brawler, place, screen)
            except ConnectionError:
                startWindow.server_error_window()
                run = "reg"
        elif run == "play_again":
            run, sock, extra_message = menuWindow.main(sock, brawler, play_again=True, extra_text=extra_message)
        else:
            run = False
    except ZeroDivisionError:
        run = "reg"
