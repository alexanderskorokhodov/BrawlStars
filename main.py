import menuWindow
import startWindow

try:
    run = True
    while run:
        run, sock, login, password = startWindow.main()
        run, sock, extra_message = menuWindow.main(sock, login, password)
        if run:
            in_game = True
            while in_game:
                try:
                    import mainGame

                    run, sock, brawler, screen, place, extra_message = mainGame.main(sock, extra_message, login)
                    if not run:
                        break
                    res, sock, extra_message = mainGame.end(sock, brawler, place, screen, extra_message)
                    if not res:
                        break
                except ConnectionError:
                    startWindow.server_error_window()
                    in_game = False

except:
    pass
