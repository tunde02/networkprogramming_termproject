import socket
import cv2
import numpy
import keyboard as k
import time
from PIL import Image, ImageTk
from pynput import keyboard, mouse
from threading import Thread
import client_gui


class KeyDetector:
    sock = None
    listener = None

    def __init__(self, sock):
        self.sock = sock
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        print("key detector registered")

    def on_press(self, key):
        data = "KEYBOARD|" + str(key) + "|PRESS"
        try:
            self.sock.sendall(data.encode())
        except ConnectionResetError:
            self.sock.close()
        # print(data)

    def on_release(self, key):
        data = "KEYBOARD|" + str(key) + "|RELEASE"
        try:
            self.sock.sendall(data.encode())
        except ConnectionResetError:
            self.sock.close()
        # print(data)


class MouseDetector:
    sock = None
    listener = None

    def __init__(self, sock):
        self.sock = sock
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        self.listener.start()
        print("mousese detector registered")
    
    def on_move(self, x, y):
        data = "MOUSE|" + str(x) + "," + str(y) + "|MOVE"
        try:
            self.sock.sendall(data.encode())
        except ConnectionResetError:
            self.sock.close()
        time.sleep(0.01)
        # print(data)

    def on_click(self, x, y, button, pressed):
        data = ""

        if button == mouse.Button.left:
            data += "MOUSE|LMB"
        elif button == mouse.Button.right:
            data += "MOUSE|RMB"

        if pressed:
            data += "|PRESS"
        else:
            data += "|RELEASE"

        self.sock.sendall(data.encode())
        # print(data)

    def on_scroll(self, x, y, dx, dy):
        data = "MOUSE|SCROLL"

        if dy < 0:
            data += "|DOWN"
        else:
            data += "|UP"

        self.sock.sendall(data.encode())
        # print(data)


class ImageReceiver:
    def __init__(self, sock):
        self.sock = sock
        self.isConnected = True

        t = Thread(target=self.recv_image)
        t.start()
        print("image receiver registered")

    def recv_image(self):
        while True:
            # if self.isConnected == False:
            #     break

            # String형의 이미지를 수신받아서 이미지로 변환 하고 화면에 출력
            length = self.recv_all(16)

            if len(length) == 0:
                print("recv_image : break")
                break

            string_data = self.recv_all(int(length))
            data = numpy.fromstring(string_data, dtype=numpy.uint8)

            decimg = cv2.imdecode(data, 1)

            cv2.imshow('CLIENT', decimg)

            if cv2.waitKey(1) == ord('q'):
                break

        cv2.destroyAllWindows()

    def recv_all(self, count):
        buffer = b''

        while count:
            try:
                temp = self.sock.recv(count)
            except ConnectionAbortedError:
                break

            if not temp:
                return None

            buffer += temp
            count -= len(temp)

        return buffer

    def stop_recv(self):
        self.isConnected = False


class Receiver:
    recv_type = 1 # msg: 1, img: 2
    isConnected = True
    screen_size = ""
    key_detector = None
    mouse_detector = None

    def __init__(self, sock, ip, port, list_window, screen_window):
        self.sock = sock
        self.ip = ip
        self.port = port
        self.list_window = list_window
        self.screen_window = screen_window

        print("^^receiver start^^")
        t = Thread(target=self.recv_from, daemon=True)
        t.start()
        # t.join()

    def recv_from(self):
        while self.isConnected:
            if self.recv_type == 1:
                try:
                    data = self.sock.recv(256)
                    print("received data :".format(data))
                except OSError:
                    print("OS error")
                    break

                msg = data.decode().split("|")

                if msg[0] == "HOSTS":
                    # change list GUI
                    self.list_window.change_list(msg[1])
                elif msg[0] == "SCREENSIZE":
                    print("size : " + msg[1])
                    self.screen_size = msg[1]
                else:
                    print("Invalid msg from server : {}".format(data))
                    pass
            elif self.recv_type == 2:
                try:
                    length = self.recv_all(16)
                except ConnectionAbortedError:
                    print("helo?")
                    break

                if len(length) == 0:
                    print("finished")
                    self.recv_type = 1
                    self.finish()
                    break
                # elif length.decode() == "HOSTS":
                #     continue

                string_data = self.recv_all(int(length))
                data = numpy.fromstring(string_data, dtype=numpy.uint8)

                decimg = cv2.imdecode(data, 1)
                # screen_img = ImageTk.PhotoImage(Image.fromarray(decimg, "RGB"))
                # print("=====img type : {}=====".format(type(screen_img)))

                # self.screen_window.screen_label.config(image=screen_img)

                cv2.imshow('CLIENT', decimg)

                if cv2.waitKey(1) == 27:
                    cv2.destroyAllWindows()
                    print("disconnect with HOST")
                    self.sock.sendall("DISCONNECT".encode())
                    self.recv_type = 1
                    self.unregister_funcs()
                    # start_list_gui(self.sock, self.ip, self.port)
                    continue
        print("^^receiver end^^")


    def recv_all(self, count):
        buffer = b''

        while count:
            try:
                temp = self.sock.recv(count)
            except ConnectionAbortedError:
                break

            if not temp:
                return None

            buffer += temp
            count -= len(temp)

        return buffer

    def change_receiver_type(self, recv_type):
        # print("====change receiver type to {}====".format(recv_type))
        self.recv_type = recv_type

    def finish(self):
        self.isConnected = False

    def register_funcs(self):
        self.key_detector = KeyDetector(self.sock)
        self.mouse_detector = MouseDetector(self.sock)

        print("register finished")

    def unregister_funcs(self):
        self.key_detector.listener.stop()
        self.mouse_detector.listener.stop()


def start_gui():
    print("start gui")

    connection_window = client_gui.ClientGUI()
    connection_window.connect_btn.config(command=lambda: connect_to(connection_window))
    connection_window.start_window()


def start_list_gui(sock, ip, port):
    list_window = client_gui.GameListGUI(ip, port)

    receiver = Receiver(sock, ip, port, list_window, None)

    list_window.window.protocol("WM_DELETE_WINDOW", lambda: disconnect(list_window, sock))
    list_window.disconnect_btn.config(command=lambda: disconnect(list_window, sock))
    list_window.quit_btn.config(command=lambda: disconnect(list_window, sock))
    list_window.remote_btn.config(command=lambda: start_game_gui(sock, "REMOTE", list_window, receiver))
    list_window.kart_btn.config(command=lambda: start_game_gui(sock, "KART", list_window, receiver))
    list_window.start_window()


def start_game_gui(sock, game, list_window, receiver):
    print("start game gui - {}".format(game))
    receiver.change_receiver_type(2)
    msg = "CONNECT|" + game
    print("<send to server : {}>".format(msg))
    sock.sendall(msg.encode())

    # screen_size = receiver.screen_size
    # print("=====screen_size : {}=====".format(screen_size))
    # receiver.key_detector, receiver.mouse_detector = register_funcs(sock)
    receiver.register_funcs()

    # list_window.close_window()
    list_window.window.withdraw()

    while receiver.recv_type == 2:
        # print("h")
        time.sleep(1)
    print("reopen list")
    list_window.window.deiconify()

    # screen_window = client_gui.ScreenGUI(game, receiver.screen_size)
    # receiver.screen_window = screen_window
    # add btn listeners
    # screen_window.window.protocol("WM_DELETE_WINDOW", lambda: (key_detector.listener.stop(), mouse_detector.listener.stop(), screen_window.close_window(), receiver.disconnect()))
    # screen_window.start_window()


def connect_to(connection_window):
    print("client connect to server")

    ip = connection_window.ip_entry.get()
    port = int(connection_window.port_entry.get())
    # print("ip : {}, port : {}".format(ip, port))

    sock = socket.socket()
    sock.connect((ip, port))

    sock.sendall("client".encode())

    # list_window = client_gui.GameListGUI(ip, port)

    # receiver = Receiver(sock, list_window, None)

    connection_window.close_window()
    start_list_gui(sock, ip, port)

    # list_window.window.protocol("WM_DELETE_WINDOW", lambda: disconnect(list_window, sock))
    # list_window.disconnect_btn.config(command=lambda: disconnect(list_window, sock))
    # list_window.quit_btn.config(command=lambda: disconnect(list_window, sock))
    # list_window.lol_btn.config(command=lambda: start_game_gui(sock, "LOL", list_window, receiver))
    # list_window.kart_btn.config(command=lambda: start_game_gui(sock, "KART", list_window, receiver))
    # list_window.start_window()


def disconnect(list_window, sock):
    try:
        sock.sendall("FINISHED".encode())
    except ConnectionResetError:
        pass
    except OSError:
        pass
    sock.close()

    print("disconnected")

    list_window.close_window()

    start_gui()


if __name__ == '__main__':
    # connection_window = client_gui.ClientGUI()
    # connection_window.connect_btn.config(command=connect_to)
    # connection_window.start_window()
    ip = ""
    port = 0

    start_gui()

    # sock = socket.socket()
    # sock.connect(("192.168.0.11", 1080))
    # sock.sendall("client".encode())

    # k.wait('b')

    # key_detector = KeyDetector(sock)
    # mouse_detector = MouseDetector(sock)
    # image_receiver = ImageReceiver(sock)

    # # t = Thread(target=esc_pressed)
    # # t.start()

    # print("register finished")

    # # t.join()

    # k.wait('esc')

    # sock.sendall("FINISHED".encode())
    # key_detector.listener.stop()
    # mouse_detector.listener.stop()

    # sock.close()

    # print("client end")
