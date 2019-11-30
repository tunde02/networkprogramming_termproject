import socket
import cv2
import numpy
import keyboard as k
import time
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
        self.sock.sendall(data.encode())
        print(data)

    def on_release(self, key):
        data = "KEYBOARD|" + str(key) + "|RELEASE"
        self.sock.sendall(data.encode())
        print(data)


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
        self.sock.sendall(data.encode())
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
        print(data)

    def on_scroll(self, x, y, dx, dy):
        data = "MOUSE|SCROLL"

        if dy < 0:
            data += "|DOWN"
        else:
            data += "|UP"

        self.sock.sendall(data.encode())
        print(data)


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


def esc_pressed():
    k.wait('esc')
    print("client end")
    exit()


def register_funcs(sock):
    key_detector = KeyDetector(sock)
    mouse_detector = MouseDetector(sock)
    image_receiver = ImageReceiver(sock)

    print("register finished")
    return key_detector, mouse_detector, image_receiver


def start_gui():
    print("start gui")
    connection_window = client_gui.ClientGUI()
    connection_window.connect_btn.config(command=lambda: connect_to(connection_window))
    connection_window.start_window()


def connect_to(connection_window):
    print("client connect to server")

    ip = connection_window.ip_entry.get()
    port = int(connection_window.port_entry.get())
    # print("ip : {}, port : {}".format(ip, port))

    sock = socket.socket()
    sock.connect((ip, port))

    sock.sendall("client".encode())

    key_detector, mouse_detector, image_receiver = register_funcs(sock)

    connection_window.close_window()

    list_window = client_gui.GameListGUI(ip, port)
    list_window.window.protocol("WM_DELETE_WINDOW", lambda: disconnect(list_window, sock, key_detector, mouse_detector, image_receiver))
    list_window.disconnect_btn.config(command=lambda: disconnect(list_window, sock, key_detector, mouse_detector, image_receiver))
    list_window.quit_btn.config(command=lambda: (disconnect(list_window, sock, key_detector, mouse_detector, image_receiver)))
    list_window.start_window()


def disconnect(list_window, sock, key_detector, mouse_detector, image_receiver):
    key_detector.listener.stop()
    mouse_detector.listener.stop()
    image_receiver.stop_recv()

    sock.sendall("FINISHED".encode())
    sock.close()

    print("disconnected")

    list_window.close_window()

    start_gui()


if __name__ == '__main__':
    # connection_window = client_gui.ClientGUI()
    # connection_window.connect_btn.config(command=connect_to)
    # connection_window.start_window()
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
