import socket
import cv2
import numpy
import keyboard as k
import time
from pynput import keyboard, mouse
from threading import Thread

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
        # try:
        #     data = "KEYBOARD|" + key.char + "|PRESS"
        # except AttributeError:
        #     data = "KEYBOARD|" + str(key) + "|PRESS"

        self.sock.sendall(data.encode())
        print(data)

    def on_release(self, key):
        data = "KEYBOARD|" + str(key) + "|RELEASE"
        # try:
        #     data = "KEYBOARD|" + key.char + "|RELEASE"
        # except AttributeError:
        #     data = "KEYBOARD|" + str(key) + "|RELEASE"

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
        time.sleep(0.005)
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

        t = Thread(target=self.recv_image)
        t.start()
        print("image receiver registered")

    def recv_image(self):
        while True:
            #String형의 이미지를 수신받아서 이미지로 변환 하고 화면에 출력
            length = self.recvAll(16)

            if length == None:
                print("recv_image : break")
                break

            stringData = self.recvAll(int(length))
            data = numpy.fromstring(stringData, dtype=numpy.uint8)

            decimg = cv2.imdecode(data, 1)

            cv2.imshow('CLIENT', decimg)

            if cv2.waitKey(1) == ord('q'):
                break

        cv2.destroyAllWindows()

    def recvAll(self, count):
        buffer = b''

        while count:
            temp = self.sock.recv(count)

            if not temp:
                return None

            buffer += temp
            count -= len(temp)

        return buffer

def esc_pressed():
    k.wait('esc')
    print("client end")
    exit()

if __name__ == '__main__':
    sock = socket.socket()
    sock.connect(("192.168.0.11", 1080))
    sock.sendall("client".encode())

    while True:
        msg = input(">> ")

        if msg == "break":
            break

        sock.sendall(msg.encode())

    keyDector = KeyDetector(sock)
    mouseseDector = MouseDetector(sock)
    imageReceiver = ImageReceiver(sock)

    # t = Thread(target=esc_pressed)
    # t.start()

    print("register finished")

    # t.join()

    k.wait('esc')

    sock.sendall("FINISHED".encode())
    keyDector.listener.stop()
    mouseseDector.listener.stop()

    sock.close()

    print("client end")
