import socket
import cv2
import numpy
import keyboard as k
import pyautogui as pg
import time
from pynput import keyboard, mouse
from pynput.keyboard import Key
from PIL import ImageGrab
from threading import Thread
import tests

keyDict = {
    "Key.alt_l": Key.alt_l,
    "Key.alt_r": Key.alt_r,
    "Key.backspace": Key.backspace,
    "Key.caps_lock": Key.caps_lock,
    "Key.cmd": Key.cmd,
    "Key.ctrl_l": Key.ctrl_l,
    "Key.ctrl_r": Key.ctrl_r,
    "Key.delete": Key.delete,
    "Key.down": Key.down,
    "Key.end": Key.end,
    "Key.enter": Key.enter,
    "Key.esc": Key.esc,
    "Key.f1": Key.f1,
    "Key.f2": Key.f2,
    "Key.f3": Key.f3,
    "Key.f4": Key.f4,
    "Key.f5": Key.f5,
    "Key.f6": Key.f6,
    "Key.f7": Key.f7,
    "Key.f8": Key.f8,
    "Key.f9": Key.f9,
    "Key.f10": Key.f10,
    "Key.f11": Key.f11,
    "Key.f12": Key.f12,
    "Key.home": Key.home,
    "Key.left": Key.left,
    "Key.page_down": Key.page_down,
    "Key.page_up": Key.page_up,
    "Key.right": Key.right,
    "Key.shift_l": Key.shift_l,
    "Key.shift_r": Key.shift_r,
    "Key.space": Key.space,
    "Key.tab": Key.tab,
    "Key.up": Key.up,
    "Key.insert": Key.insert,
    "Key.num_lock": Key.num_lock,
    "Key.pause": Key.pause,
    "Key.print_screen": Key.print_screen,
    "Key.scroll_lock": Key.scroll_lock,
    "Key.alt": Key.alt,
    "Key.alt_gr": Key.alt_gr,
    "Key.cmd_l": Key.cmd_l,
    "Key.cmd_r": Key.cmd_r,
    "Key.ctrl": Key.ctrl,
    "Key.f13": Key.f13,
    "Key.f14": Key.f14,
    "Key.f15": Key.f15,
    "Key.f16": Key.f16,
    "Key.f17": Key.f17,
    "Key.f18": Key.f18,
    "Key.f19": Key.f19,
    "Key.f20": Key.f20,
    "Key.shift": Key.shift,
    "Key.menu": Key.menu
}


def recv_msg(sock):
    key_controller = keyboard.Controller()
    mouse_controller = mouse.Controller()
    img_sender = None

    while True:
        try:
            data = sock.recv(1024)
        except ConnectionAbortedError:
            break

        msg = data.decode().split("|")

        # if msg[2] != "MOVE":
        #     print('Received : {}|{}|{}'.format(msg[0], msg[1], msg[2]))

        if msg[0] == "DISCONNECT":
            print("client disconnected")
            img_sender.isConnected = False
            continue
        elif msg[0] == "GAME":
            if msg[1] == "REMOTE":
                img_sender = start_remote_control()
            elif msg[1] == "KART":
                img_sender = start_kart()

        if msg[0] == "KEYBOARD":
            if msg[2] == "PRESS":
                if len(msg[1]) == 3: 
                    key_controller.press(msg[1][1])
                elif msg[1] == "<21>":
                    pg.keyDown("hanguel")
                elif msg[1] == "<25>":
                    pg.keyDown("hanja")
                else:
                    key_controller.press(keyDict[msg[1]])
            elif msg[2] == "RELEASE":
                if len(msg[1]) == 3:
                    key_controller.release(msg[1][1])
                elif msg[1] == "<21>":
                    pg.keyUp("hanguel")
                elif msg[1] == "<25>":
                    pg.keyUp("hanja")
                else:
                    key_controller.release(keyDict[msg[1]])

        elif msg[0] == "MOUSE":
            if msg[1] == "LMB":
                if msg[2] == "PRESS":
                    mouse_controller.press(mouse.Button.left)
                elif msg[2] == "RELEASE":
                    mouse_controller.release(mouse.Button.left)
            elif msg[1] == "RMB":
                if msg[2] == "PRESS":
                    mouse_controller.press(mouse.Button.right)
                elif msg[2] == "RELEASE":
                    mouse_controller.release(mouse.Button.right)
            elif msg[1] == "SCROLL":
                if msg[2] == "UP":
                    mouse_controller.scroll(0, 10)
                elif msg[2] == "DOWN":
                    mouse_controller.scroll(0, -10)
            else:
                mouse_controller.position = msg[1].split(",")[0], msg[1].split(",")[1]


class ImgSender:
    isConnected = True

    def __init__(self, sock, screen_box):
        self.sock = sock
        self.screen_box = screen_box

        t = Thread(target=self.screen_send_thread)
        t.start()

    def screen_send_thread(self):
        while self.isConnected:
            # 스크린샷 찍기
            imgGrab = ImageGrab.grab(bbox=self.screen_box)
            cv_img = cv2.cvtColor(numpy.array(imgGrab), cv2.COLOR_RGB2BGR)

            # 스크린샷에 커서 그리기
            cv2.circle(cv_img, pg.position(), 7, (255, 0, 0), -1)

            # 추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, imgencode = cv2.imencode('.jpg', cv_img, encode_param)
            data = numpy.array(imgencode)
            stringData = data.tostring()

            # String 형태로 변환한 이미지를 socket을 통해서 전송
            self.sock.send(str(len(stringData)).ljust(16).encode())
            self.sock.send(stringData)


def start_remote_control():
    print("remote control started")
    sock.sendall("SCREENSIZE|1920,1080".encode())

    img_sender = ImgSender(sock, (0, 0, 1920, 1080))
    
    return img_sender


def start_kart():
    windows = tests.getWindowSizes()
    for win in windows:
        if win[2] == "NexonPlug":
            x = win[1][0] + 300
            y = win[1][1] + 40
            mC = mouse.Controller()
            kC = keyboard.Controller()
            mC.position = (x, y)
            mC.click(mouse.Button.left)
            # time.sleep(3)
            # kC.press(Key.left)
            # kC.release(Key.left)
            # kC.press(Key.enter)
            # kC.release(Key.enter)
            break

    kart_window = []
    isFound = False
    while not isFound:
        windows = tests.getWindowSizes()
        for win in windows:
            if win[2] == "KartRider Client":
                kart_window = win
                isFound = True
                break
        time.sleep(0.3)

    print("kart started")

    screen_x = kart_window[1][0]
    screen_y = kart_window[1][1]
    screen_width = kart_window[1][2]
    screen_height = kart_window[1][3]

    msg = "SCREENSIZE|" + str(screen_width) + "," + str(screen_height)
    sock.sendall(msg.encode())
    img_sender = ImgSender(sock, (screen_x, screen_y, screen_x + screen_width, screen_y + screen_height))
    
    return img_sender


if __name__ == "__main__":
    sock = socket.socket()
    # 192.168.0.11
    sock.connect(("127.0.0.1", 1080))
    sock.sendall("host".encode())

    recv_msg(sock)

    print("host end")