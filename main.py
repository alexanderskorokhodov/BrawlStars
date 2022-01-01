import menuWindow
import startWindow

res, sock = startWindow.main()
if res:
    menuWindow.main(sock)
