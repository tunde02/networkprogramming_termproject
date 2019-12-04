import socket
import cv2
import numpy
import keyboard as k
import pyautogui as pg
import hWnd_calculator as hwndCal
import time
from pynput import keyboard, mouse
from pynput.keyboard import Key
from PIL import ImageGrab
from threading import Thread


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

class MsgReceiver:
    isConnected = True

    def __init__(self, sock):
        self.sock = sock

        t = Thread(target=self.recv_msg, daemon=True)
        t.start()

    def recv_msg(self):
        key_simulator = KeySimulator()
        mouse_simulator = MouseSimulator()
        img_sender = None

        while self.isConnected:
            try:
                data = self.sock.recv(1024)
            except ConnectionAbortedError:
                self.sock.close()
                return
            except ConnectionResetError:
                self.sock.close()
                return

            msg = data.decode().split("|")

            if msg[0] == "DISCONNECT":
                print("클라이언트와의 연결이 끊어졌습니다.")
                img_sender.isConnected = False
                key_simulator.quit_game()
                continue
            elif msg[0] == "GAME": # 게임 실행
                if msg[1] == "REMOTE":
                    img_sender = start_remote_control(mouse_simulator)
                elif msg[1] == "KART":
                    img_sender = start_kart(mouse_simulator)
                elif msg[1] == "DONTSTARVE":
                    img_sender = start_dont_starve(mouse_simulator)
                elif msg[1] == "PORTAL":
                    img_sender = start_portal(mouse_simulator)
                elif msg[1] == "UNDERTALE":
                    img_sender = start_undertale(mouse_simulator)
                elif msg[1] == "DODGE":
                    img_sender = start_dodge(mouse_simulator)
            elif msg[0] == "KEYBOARD": # 키보드 조작 수행
                key_simulator.simulate_key(msg)
            elif msg[0] == "MOUSE": # 마우스 조작 수행
                mouse_simulator.simulate_mouse(msg)

        print("서버와의 접속을 종료합니다")
        self.sock.sendall("FINISHED".encode())
        self.sock.close()


class ImgSender:
    isConnected = True

    def __init__(self, sock, screen_box):
        self.sock = sock
        self.screen_box = screen_box

        print("img sender start")
        t = Thread(target=self.screen_send_thread)
        t.start()

    def screen_send_thread(self):
        while self.isConnected:
            # 스크린샷 찍기
            # time.sleep(0.025)
            try:
                imgGrab = ImageGrab.grab(bbox=self.screen_box)
            except OSError:
                continue

            cv_img = cv2.cvtColor(numpy.array(imgGrab), cv2.COLOR_RGB2BGR)

            # 스크린샷에 커서 그리기
            cv2.circle(cv_img, pg.position(), 7, (255, 0, 0), -1)

            # 추출한 이미지를 String 형태로 인코딩
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, imgencode = cv2.imencode('.jpg', cv_img, encode_param)
            data = numpy.array(imgencode)
            stringData = data.tostring()

            # String 형태로 인코딩한 이미지를 socket을 통해 전송
            try:
                self.sock.send(str(len(stringData)).ljust(16).encode())
                self.sock.send(stringData)
            except ConnectionResetError:
                print("서버와의 연결이 끊어졌습니다")
                break
            except OSError:
                print("서버와의 연결이 끊어졌습니다")
                break


class KeySimulator:
    def __init__(self):
        self.key_controller = keyboard.Controller()

    def simulate_key(self, op):
        '''
        서버로부터 받은 msg를 split()하여 받은
        op에 따라 알맞은 키보드 명령을 수행
        특수키를 처리하기 위해 keyDict 사용
        한/영, 한자 키를 처리하기 위해 pyautogui를 사용
        '''

        if op[2] == "PRESS":
            if len(op[1]) == 3:
                self.key_controller.press(op[1][1])
            elif op[1] == "<21>":
                pg.keyDown("hanguel")
            elif op[1] == "<25>":
                pg.keyDown("hanja")
            else:
                self.key_controller.press(keyDict[op[1]])
        elif op[2] == "RELEASE":
            if len(op[1]) == 3:
                self.key_controller.release(op[1][1])
            elif op[1] == "<21>":
                pg.keyUp("hanguel")
            elif op[1] == "<25>":
                pg.keyUp("hanja")
            else:
                self.key_controller.release(keyDict[op[1]])

    def quit_game(self):
        with self.key_controller.pressed(Key.alt):
            self.key_controller.press(Key.f4)


class MouseSimulator:
    def __init__(self):
        self.mouse_controller = mouse.Controller()
        self.screen_x = 0
        self.screen_y = 0

    def simulate_mouse(self, op):
        '''
        서버로부터 받은 msg를 split()하여 받은
        op에 따라 알맞은 마우스 명령을 수행
        '''

        if op[1] == "LMB":
            if op[2] == "PRESS":
                self.mouse_controller.press(mouse.Button.left)
            elif op[2] == "RELEASE":
                self.mouse_controller.release(mouse.Button.left)
        elif op[1] == "RMB":
            if op[2] == "PRESS":
                self.mouse_controller.press(mouse.Button.right)
            elif op[2] == "RELEASE":
                self.mouse_controller.release(mouse.Button.right)
        elif op[1] == "SCROLL":
            if op[2] == "UP":
                self.mouse_controller.scroll(0, 25)
            elif op[2] == "DOWN":
                self.mouse_controller.scroll(0, -25)
        else:
            self.mouse_controller.position = (int(op[1].split(",")[0]) + self.screen_x, int(op[1].split(",")[1]) + self.screen_y)

    def set_screen_pos(self, pos):
        self.screen_x = pos[0]
        self.screen_y = pos[1]


def start_remote_control(mouse_simulator):
    print("Remote Control Start!")
    try:
        sock.sendall("SCREENSIZE|1920,1080".encode())
    except ConnectionResetError:
        return None

    img_sender = ImgSender(sock, (0, 0, 1920, 1080))

    mouse_simulator.mouse_controller.position = (0, 0)
    mouse_simulator.set_screen_pos((0, 0))

    return img_sender


def start_kart(mouse_simulator):
    windows = hwndCal.getWindowSizes()
    # 넥슨 플러그 window를 찾아 카트를 실행
    for win in windows:
        if win[2] == "NexonPlug":
            x = win[1][0] + 300
            y = win[1][1] + 40
            mouse_simulator.position = (x, y)
            mouse_simulator.click(mouse.Button.left)
            break

    # 실행된 카트 window를 찾기
    game_window = []
    isFound = False
    while not isFound:
        windows = hwndCal.getWindowSizes()
        for win in windows:
            if win[2] == "KartRider Client":
                game_window = win
                isFound = True
                break
        time.sleep(0.3)

    print("KartRider Start")

    screen_x = game_window[1][0]
    screen_y = game_window[1][1]
    screen_width = game_window[1][2]
    screen_height = game_window[1][3]

    # 카트window의 사이즈를 서버에 전송
    msg = "SCREENSIZE|" + str(screen_width) + "," + str(screen_height)
    sock.sendall(msg.encode())

    img_sender = ImgSender(sock, (screen_x, screen_y, screen_x + screen_width, screen_y + screen_height))

    mouse_simulator.mouse_controller.position = (screen_x, screen_y)
    mouse_simulator.set_screen_pos((screen_x, screen_y))

    return img_sender


def start_dont_starve(mouse_simulator):
    global folder_x, folder_y

    mouse_simulator.mouse_controller.position = (folder_x + 240, folder_y + 250)
    mouse_simulator.mouse_controller.click(mouse.Button.left, 2)

    # 실행된 게임 window 찾기
    game_window = []
    isFound = False
    while not isFound:
        windows = hwndCal.getWindowSizes()
        for win in windows:
            if win[2] == "Don't Starve Together":
                game_window = win
                isFound = True
                break
        time.sleep(0.3)

    print("Don't Starve Start")

    screen_x = game_window[1][0]
    screen_y = game_window[1][1]
    screen_width = game_window[1][2]
    screen_height = game_window[1][3]

    # 게임 window의 사이즈를 서버에 전송
    msg = "SCREENSIZE|" + str(screen_width) + "," + str(screen_height)
    sock.sendall(msg.encode())

    img_sender = ImgSender(sock, (screen_x, screen_y, screen_x + screen_width, screen_y + screen_height))

    mouse_simulator.mouse_controller.position = (screen_x, screen_y)
    mouse_simulator.set_screen_pos((screen_x, screen_y))

    return img_sender


def start_portal(mouse_simulator):
    global folder_x, folder_y

    mouse_simulator.mouse_controller.position = (folder_x + 360, folder_y + 250)
    mouse_simulator.mouse_controller.click(mouse.Button.left, 2)

    # 실행된 게임 window 찾기
    game_window = []
    isFound = False
    while not isFound:
        windows = hwndCal.getWindowSizes()
        for win in windows:
            if win[2] == "Portal":
                game_window = win
                isFound = True
                break
        time.sleep(0.3)

    print("Portal Start")

    screen_x = game_window[1][0]
    screen_y = game_window[1][1]
    screen_width = game_window[1][2]
    screen_height = game_window[1][3]

    # 게임 window의 사이즈를 서버에 전송
    msg = "SCREENSIZE|" + str(screen_width) + "," + str(screen_height)
    sock.sendall(msg.encode())

    img_sender = ImgSender(sock, (screen_x, screen_y, screen_x + screen_width, screen_y + screen_height))

    mouse_simulator.mouse_controller.position = (screen_x, screen_y)
    mouse_simulator.set_screen_pos((screen_x, screen_y))

    return img_sender


def start_undertale(mouse_simulator):
    global folder_x, folder_y

    mouse_simulator.mouse_controller.position = (folder_x + 480, folder_y + 250)
    mouse_simulator.mouse_controller.click(mouse.Button.left, 2)

    # 실행된 게임 window 찾기
    game_window = []
    isFound = False
    while not isFound:
        windows = hwndCal.getWindowSizes()
        for win in windows:
            if win[2] == "UNDERTALE":
                game_window = win
                isFound = True
                break
        time.sleep(0.3)

    print("Undertale Start")

    screen_x = game_window[1][0]
    screen_y = game_window[1][1]
    screen_width = game_window[1][2]
    screen_height = game_window[1][3]

    # 게임 window의 사이즈를 서버에 전송
    msg = "SCREENSIZE|" + str(screen_width) + "," + str(screen_height)
    sock.sendall(msg.encode())

    img_sender = ImgSender(sock, (screen_x, screen_y, screen_x + screen_width, screen_y + screen_height))

    mouse_simulator.mouse_controller.position = (screen_x, screen_y)
    mouse_simulator.set_screen_pos((screen_x, screen_y))

    return img_sender


def start_dodge(mouse_simulator):
    global folder_x, folder_y

    mouse_simulator.mouse_controller.position = (folder_x + 600, folder_y + 250)
    mouse_simulator.mouse_controller.click(mouse.Button.left, 2)

    # 실행된 게임 window 찾기
    game_window = []
    isFound = False
    while not isFound:
        windows = hwndCal.getWindowSizes()
        for win in windows:
            if win[2] == "닷지 1.9":
                game_window = win
                isFound = True
                break
        time.sleep(0.3)

    print("Dodge Start")

    screen_x = game_window[1][0]
    screen_y = game_window[1][1]
    screen_width = game_window[1][2]
    screen_height = game_window[1][3]

    # 게임 window의 사이즈를 서버에 전송
    msg = "SCREENSIZE|" + str(screen_width) + "," + str(screen_height)
    sock.sendall(msg.encode())

    img_sender = ImgSender(sock, (screen_x, screen_y, screen_x + screen_width, screen_y + screen_height))

    mouse_simulator.mouse_controller.position = (screen_x, screen_y)
    mouse_simulator.set_screen_pos((screen_x, screen_y))

    return img_sender


def wait_terminate_key():
    k.wait("F5")
    msg_receiver.isConnected = False


if __name__ == "__main__":
    sock = socket.socket()
    sock.connect(("192.168.0.11", 1080))
    sock.sendall("host".encode())
    print("Host Start")

    folder_x = 0
    folder_y = 0
    windows = hwndCal.getWindowSizes()
    # games 폴더 window를 찾아 위치 저장
    for win in windows:
        if win[2] == "games":
            folder_x = win[1][0]
            folder_y = win[1][1]
            break

    t = Thread(target=wait_terminate_key)
    t.start()

    msg_receiver = MsgReceiver(sock)