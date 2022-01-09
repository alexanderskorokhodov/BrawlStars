import menuWindow
import startWindow

res, sock, login, password = startWindow.main()
if res:
    menuWindow.main(sock, login, password)
