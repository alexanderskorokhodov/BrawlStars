import menuWindow
import startWindow


run = True
while run:
    run, sock, login, password = startWindow.main()
    run, sock, extra_message = menuWindow.main(sock, login, password)
    if run:
        import mainGame
        mainGame.main(sock, extra_message, login)
