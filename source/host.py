import socket
import cv2
import numpy
import keyboard as k
import pyautogui as pg
from pynput import keyboard, mouse
from pynput.keyboard import Key
from PIL import ImageGrab
from threading import Thread

keyDict = {
    "Key.space": Key.space, 
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
    "Key.scroll_lock": Key.scroll_lock
}

def recv_control(sock):
    keyController = keyboard.Controller()
    mouseController = mouse.Controller()

    while True:
        data = sock.recv(1024)
        msg = data.decode().split('|')

        if msg[2] != "MOVE":
            print('Received : {} {} {}'.format(msg[0], msg[1], msg[2]))

        if msg[0] == "FINISHED":
            print("host terminated")
            sock.close()
            break

        if msg[0] == "KEYBOARD":
            if msg[2] == "PRESS":
                if len(msg[1]) == 1:
                    # keyController.press(msg[1])
                    pg.keyDown(msg[1])
                elif msg[1] == "<21>":
                    pg.keyDown("hanguel")
                elif msg[1] == "<25>":
                    pg.keyDown("hanja")
                else:
                    keyController.press(keyDict[msg[1]])
                    # pg.keyDown(msg[1][4:len(msg[1]) - 1])
            elif msg[2] == "RELEASE":
                if len(msg[1]) == 1:
                    # keyController.release(msg[1])
                    pg.keyUp(msg[1])
                elif msg[1] == "<21>":
                    pg.keyUp("hanguel")
                elif msg[1] == "<25>":
                    pg.keyUp("hanja")
                else:
                    keyController.release(keyDict[msg[1]])
                    # pg.keyUp(msg[1][4:len(msg[1]) - 1])
        elif msg[0] == "MOUSE":
            if msg[1] == "LMB":
                if msg[2] == "PRESS":
                    # print("MOUSE|{}|PRESS".format(msg[1]))
                    mouseController.press(mouse.Button.left)
                elif msg[2] == "RELEASE":
                    # print("MOUSE|{}|RELEASE".format(msg[1]))
                    mouseController.release(mouse.Button.left)
            elif msg[1] == "RMB":
                if msg[2] == "PRESS":
                    # print("MOUSE|{}|PRESS".format(msg[1]))
                    mouseController.press(mouse.Button.right)
                elif msg[2] == "RELEASE":
                    # print("MOUSE|{}|RELEASE".format(msg[1]))
                    mouseController.release(mouse.Button.right)
            elif msg[1] == "SCROLL":
                if msg[2] == "UP":
                    # print("MOUSE|{}|UP".format(msg[1]))
                    mouseController.scroll(0, 1)
                elif msg[2] == "DOWN":
                    # print("MOUSE|{}|DOWN".format(msg[1]))
                    mouseController.scroll(0, -1)
            else:
                mouseController.position = msg[1].split(",")[0], msg[1].split(",")[1]

def screen_send_thread(sock):
    while True:
        imgGrab = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
        cv_img = cv2.cvtColor(numpy.array(imgGrab), cv2.COLOR_RGB2BGR)
        #추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', cv_img, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()

        #String 형태로 변환한 이미지를 socket을 통해서 전송
        sock.send(str(len(stringData)).ljust(16).encode())
        sock.send(stringData)

if __name__ == "__main__":
    sock = socket.socket()
    sock.connect(("192.168.0.11", 1080))
    sock.sendall("host".encode())

    print("waiting key s")
    k.wait("s")

    sock.sendall("s".encode())

    t1 = Thread(target=screen_send_thread, args=[sock])
    t2 = Thread(target=recv_control, args=[sock])

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("host end")