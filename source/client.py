import socket
import cv2
import numpy
import time
import client_gui
from PIL import Image
from pynput import keyboard, mouse
from threading import Thread


class KeyDetector:
    '''
    키보드를 입력하면 그 Key를 포함한
    메시지를 생성하여 서버로 전송
    '''

    def __init__(self, sock):
        self.sock = sock
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )

        self.listener.start()

    def on_press(self, key):
        data = "KEYBOARD|" + str(key) + "|PRESS|"
        try:
            self.sock.sendall(data.encode())
        except ConnectionAbortedError:
            self.listener.stop()
        except ConnectionResetError:
            self.listener.stop()

    def on_release(self, key):
        data = "KEYBOARD|" + str(key) + "|RELEASE|"
        try:
            self.sock.sendall(data.encode())
        except ConnectionAbortedError:
            self.listener.stop()
        except ConnectionResetError:
            self.listener.stop()


class MouseDetector:
    '''
    마우스를 클릭하거나 움직이면 그 event를 포함한
    메시지를 생성하여 서버로 전송
    '''

    def __init__(self, sock):
        self.sock = sock
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )

        self.listener.start()

    def on_move(self, x, y):
        data = "MOUSE|" + str(x) + "," + str(y) + "|MOVE|"
        try:
            self.sock.sendall(data.encode())
        except ConnectionAbortedError:
            self.listener.stop()
        except ConnectionResetError:
            self.listener.stop()
        time.sleep(0.01)

    def on_click(self, x, y, button, pressed):
        data = "MOUSE|"

        if button == mouse.Button.left:
            data += "LMB|"
        elif button == mouse.Button.right:
            data += "RMB|"

        if pressed:
            data += "PRESS|"
        else:
            data += "RELEASE|"

        try:
            self.sock.sendall(data.encode())
        except ConnectionAbortedError:
            self.listener.stop()
        except ConnectionResetError:
            self.listener.stop()

    def on_scroll(self, x, y, dx, dy):
        data = "MOUSE|SCROLL|"

        if dy < 0:
            data += "DOWN|"
        else:
            data += "UP|"

        try:
            self.sock.sendall(data.encode())
        except ConnectionAbortedError:
            self.listener.stop()
        except ConnectionResetError:
            self.listener.stop()


class Receiver:
    '''
    recv_type에 따라
    서버로부터 메시지를 받거나 이미지를 받음
    '''

    recv_type = 1 # msg: 1, img: 2
    isConnected = True
    key_detector = None
    mouse_detector = None

    def __init__(self, sock, ip, port, list_window, screen_window):
        self.sock = sock
        self.ip = ip
        self.port = port
        self.list_window = list_window
        self.screen_window = screen_window
        self.screen_size = ""

        t = Thread(target=self.recv_from, daemon=True)
        t.start()

    def recv_from(self):
        while self.isConnected:
            if self.recv_type == 1:
                try:
                    data = self.sock.recv(256)
                    print("received data {}:".format(data))
                except ConnectionAbortedError:
                    print("서버와의 연결이 끊어졌습니다")
                    break
                except ConnectionResetError:
                    print("서버와의 연결이 끊어졌습니다")
                    break
                except OSError:
                    print("서버와의 연결이 끊어졌습니다")
                    break

                try:
                    msg = data.decode().split("|")
                except UnicodeDecodeError:
                    continue

                if msg[0] == "HOSTS":
                    # ListGUI의 Host 수 갱신
                    self.list_window.change_list(msg[1])
                elif msg[0] == "SCREENSIZE":
                    self.screen_size = msg[1]
                elif msg[0] == "DISCONNECT":
                    print("Host와의 연결 종료 확인")
                    continue
                else:
                    print("Invalid msg from server : {}".format(data))
            elif self.recv_type == 2:
                try:
                    length = self.recv_all(16)
                except ConnectionAbortedError:
                    break
                except ConnectionResetError:
                    break

                if len(length) == 0:
                    self.recv_type = 1
                    self.finish()
                    break

                string_data = self.recv_all(int(length))
                data = numpy.fromstring(string_data, dtype=numpy.uint8)

                decimg = cv2.imdecode(data, 1)

                cv2.imshow("CLIENT", decimg)

                if cv2.waitKey(1) == 27:
                    print("HOST와의 연결을 종료합니다")

                    cv2.destroyAllWindows()

                    self.sock.sendall("DISCONNECT|".encode())
                    self.recv_type = 1
                    self.unregister_funcs()

    def recv_all(self, count):
        buffer = b''

        while count:
            try:
                temp = self.sock.recv(count)
            except ConnectionAbortedError:
                break
            except ConnectionResetError:
                break

            if not temp:
                return None

            buffer += temp
            count -= len(temp)

        return buffer

    def finish(self):
        self.isConnected = False

    def register_funcs(self):
        self.key_detector = KeyDetector(self.sock)
        self.mouse_detector = MouseDetector(self.sock)

        print("키보드, 마우스 리스너 등록 완료")

    def unregister_funcs(self):
        self.key_detector.listener.stop()
        self.mouse_detector.listener.stop()

        print("키보드, 마우스 리스너 등록 해제")


def start_gui():
    '''
    Client의 처음 GUI를 띄워줌
    '''

    connection_window = client_gui.ClientGUI()
    connection_window.connect_btn.config(command=lambda: connect_to(connection_window))
    connection_window.start_window()


def start_list_gui(sock, ip, port):
    '''
    Game List GUI를 띄우고 새로운 Receiver 생성
    '''

    list_window = client_gui.GameListGUI(ip, port)

    receiver = Receiver(sock, ip, port, list_window, None)

    list_window.window.protocol("WM_DELETE_WINDOW", lambda: disconnect(list_window, sock))
    list_window.disconnect_btn.config(command=lambda: disconnect(list_window, sock))
    list_window.remote_btn.config(command=lambda: start_game_gui(sock, "REMOTE", list_window, receiver))
    list_window.kart_btn.config(command=lambda: start_game_gui(sock, "KART", list_window, receiver))

    list_window.start_window()


def start_game_gui(sock, game, list_window, receiver):
    '''
    Game을 선택하면 그것을 서버로 전송하고
    List GUI를 숨기고 종료할 때까지 대기
    '''

    print("Start Game : {}".format(game))

    receiver.recv_type = 2
    msg = "CONNECT|" + game + "|"

    sock.sendall(msg.encode())

    receiver.register_funcs()

    # List GUI를 숨기고 대기
    list_window.window.withdraw()

    while receiver.recv_type == 2:
        time.sleep(1)

    list_window.window.deiconify()


def connect_to(connection_window):
    '''
    Client GUI의 ip와 port를 얻어와 소켓을 생성하고
    서버와 연결, 그리고 List GUI를 띄움
    '''

    ip = connection_window.ip_entry.get()
    port = int(connection_window.port_entry.get())

    sock = socket.socket()
    sock.connect((ip, port))

    sock.sendall("client".encode())

    connection_window.close_window()

    start_list_gui(sock, ip, port)


def disconnect(list_window, sock):
    '''
    서버에 연결을 종료한다는 메시지를 보내고
    서버와 연결된 소켓을 닫은 다음 처음의 GUI를 띄움
    '''

    try:
        sock.sendall("FINISHED|".encode())
    except ConnectionResetError:
        pass

    sock.close()

    list_window.close_window()

    start_gui()


if __name__ == '__main__':
    # ip = ""
    # port = 0

    start_gui()