import menuWindow
import startWindow


run = True
while run:
    run, sock, login, password = startWindow.main()
    run, sock = menuWindow.main(sock, login, password)
    if run:
        import game
        game.main(sock)
