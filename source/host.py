import socket
import cv2
import numpy
import keyboard as k
from pynput import keyboard, mouse
from PIL import ImageGrab
from threading import Thread

def recv_control(sock):
    keyController = keyboard.Controller()
    mouseController = mouse.Controller()

    while True:
        data = sock.recv(1024)
        msg = data.decode().split('|')

        if msg[0] == "FINISHED":
            print("host terminated")
            sock.close()
            break

        if msg[0] == "KEYBOARD":
            if msg[2] == "PRESS":
                # print("KEYBOARD|{}|PRESS".format(msg[1]))
                keyController.press(msg[1])
            elif msg[2] == "RELEASE":
                # print("KEYBOARD|{}|RELEASE".format(msg[1]))
                keyController.release(msg[1])
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
                    mouseController.release(mouse.Button.left)
            elif msg[1] == "SCROLL":
                if msg[2] == "UP":
                    # print("MOUSE|{}|UP".format(msg[1]))
                    mouseController.scroll(0, 2)
                elif msg[2] == "DOWN":
                    # print("MOUSE|{}|DOWN".format(msg[1]))
                    mouseController.scroll(0, -2)

        print('Received : {}'.format(data.decode()))

def screen_send_thread(sock):
    while True:
        imgGrab = ImageGrab.grab(bbox=(480, 100, 1170, 724))
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
    sock.connect(("127.0.0.1", 1080))
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