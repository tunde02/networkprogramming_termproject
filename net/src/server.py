import socket
import keyboard
from threading import Thread

def runServer(connects, ip='127.0.0.1', port=1080):
    with socket.socket() as sock:
        sock.bind((ip, port))

        print("Server started...")
        
        while True:
            sock.listen(3)
            conn, addr = sock.accept()
            print("client accessed")
            connects.append(conn)

            t = Thread(target=echoHandler, args=(conn, connects, addr))
            t.start()

        print("Server turned off")
        sock.close()

def echoHandler(conn, connects, addr, terminator='finished'):
    BUFSIZE = 1024

    while True:
        data = conn.recv(BUFSIZE)
        msg = data.decode()

        if msg == terminator:
            print("terminated")
            conn.close()
            break

        print('Received : {} << {}'.format(msg, addr))

def esc_pressed():
    keyboard.wait('esc')
    exit()

if __name__ == '__main__':
    t = Thread(target=esc_pressed)
    t.start()
    connects = []
    runServer(connects)