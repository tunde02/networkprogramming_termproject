import socket
import cv2
import numpy
import keyboard as k
import time
from pynput import keyboard, mouse
from threading import Thread

'''
class KeyDetector:
    key = ""
    sock = None

    def __init__(self, sock):
        self.sock = sock
        keyboard.on_press(self.send_pressed_key)
        keyboard.on_release(self.send_released_key)
        print("key detector registered")

    def send_pressed_key(self, e):
        self.key = e.name
        data = str(self.key + " pressed")
        self.sock.sendall(data.encode())
        print(data)

    def send_released_key(self, e):
        self.key = e.name
        data = str(self.key + " released")
        self.sock.sendall(data.encode())
        print(data)
'''

class KeyDetector:
    sock = None
    listener = None

    def __init__(self, sock):
        self.sock = sock
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        print("key detector registered")

    def on_press(self, key):
        data = str(key) + " pressed"
        self.sock.sendall(data.encode())
        print(data)

    def on_release(self, key):
        data = str(key) + " released"
        self.sock.sendall(data.encode())
        print(data)

'''
class MouseDetector:
    mousesePos = (0, 0)
    sock = None

    def __init__(self, sock):
        self.mousesePos = pg.position()
        self.sock = sock
        t = Thread(target=self.detect_mousese_position)
        t.start()
        print("mousese detector registered")

    def detect_mousese_position(self):
        while True:
            currentPos = pg.position()
            diff = max([abs(self.mousesePos[0] - currentPos[0]), abs(self.mousesePos[1] - currentPos[1])])

            if currentPos == (0, 0):
                break

            if diff > 25:
                self.mousesePos = currentPos
                self.sock.sendall(str(self.mousesePos).encode())
                print('mousese position : ({0}, {1})'.format(self.mousesePos[0], self.mousesePos[1]))
'''

class MouseDetector:
    sock = None
    listener = None

    def __init__(self, sock):
        self.sock = sock
        self.listener = mouse.Listener(
            # on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        self.listener.start()
        print("mousese detector registered")
    
    def on_move(self, x, y):
        data = str((x, y))
        self.sock.sendall(data.encode())
        print("mousese position : " + data)

    def on_click(self, x, y, button, pressed):
        data = str((x, y))

        if button == mouse.Button.left:
            data += " Left mousese Button"
        elif button == mouse.Button.right:
            data += " Right mousese Button"

        if pressed:
            data += " Pressed"
        else:
            data += " Released"

        self.sock.sendall(data.encode())
        print(data)

    def on_scroll(self, x, y, dx, dy):
        data = "mousese Scrolled "

        if dy < 0:
            data += "Down"
        else:
            data += "Up"

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
    sock.connect(("127.0.0.1", 1080))

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
