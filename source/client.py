import socket
import keyboard
import pyautogui as pg
import time
from pynput import keyboard as qwe
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

    def __init__(self, sock):
        self.sock = sock
        listener = qwe.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()

    def on_press(self, key):
        data = str(key) + " pressed"
        self.sock.sendall(data.encode())
        print(data)

    def on_release(self, key):
        data = str(key) + " released"
        self.sock.sendall(data.encode())
        print(data)


class MouseDetector:
    mousePos = (0, 0)
    sock = None

    def __init__(self, sock):
        self.mousePos = pg.position()
        self.sock = sock
        t = Thread(target=self.detect_mouse_position)
        t.start()
        print("mouse detector registered")

    def detect_mouse_position(self):
        while True:
            currentPos = pg.position()
            diff = max([abs(self.mousePos[0] - currentPos[0]), abs(self.mousePos[1] - currentPos[1])])

            if currentPos == (0, 0):
                break

            if diff > 25:
                self.mousePos = currentPos
                self.sock.sendall(str(self.mousePos).encode())
                print('mouse position : ({0}, {1})'.format(self.mousePos[0], self.mousePos[1]))

def esc_pressed():
    keyboard.wait('esc')
    print("client end")
    exit()

if __name__ == '__main__':
    sock = socket.socket()
    sock.connect(("127.0.0.1", 1080))
    
    # k = KeyDetector(sock)
    k = KeyDetector(sock)
    m = MouseDetector(sock)

    print("register finished")