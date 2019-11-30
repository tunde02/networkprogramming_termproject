import socket
import keyboard
from threading import Thread


def run_server(ip='192.168.0.11', port=1080):
    with socket.socket() as sock:
        sock.bind((ip, port))

        print("Server started...")

        clnts = []
        hosts = []
        while True:
            sock.listen(3)
            conn, addr = sock.accept()
            # connects.append(clntSock)

            sock_type = conn.recv(10)

            if sock_type.decode() == "client":
                print("client accessed")
                new_clnt = ClientHandler(sock=conn, addr=addr)
                clnts.append(conn)
                new_clnt.hosts = hosts
            else:
                print("host accessed")
                new_host = HostHandler(sock=conn, addr=addr)
                hosts.append(conn)
                new_host.clnts = clnts

        print("Server end")
        sock.close()


class ClientHandler:
    BUFSIZE = 1024
    terminator = "FINISHED"
    hosts = []

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.host = None

        t = Thread(target=self.deliver_msg)
        t.start()

    def deliver_msg(self):
        while True:
            data = self.sock.recv(self.BUFSIZE)
            msg = data.decode()

            if msg == self.terminator:
                print("terminated")
                self.sock.close()
                break
            elif msg == "KEYBOARD|'h'|PRESS":
                self.sock.recv(self.BUFSIZE) # eat release listener
                print("match client to host")
                self.match_host()
                break
            print('Received : {} << {}'.format(msg, self.addr))
            # self.host.sendall(data)

    def match_host(self):
        self.host = self.hosts[0]
        while True:
            data = self.sock.recv(self.BUFSIZE)
            msg = data.decode()

            if msg == self.terminator:
                print("terminated")
                self.host.sendall("FINISHED".encode())
                self.sock.close()
                break
            # print("send client's msg to host")
            self.host.sendall(data)


class HostHandler:
    BUFSIZE = 1024
    terminator = "FINISHED"
    clnts = []

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.client = None

        t = Thread(target=self.recv_host)
        t.start()

    def recv_host(self):
        while True:
            trigger = self.sock.recv(1024)
            if trigger.decode() == "s":
                self.match_client()
                self.deliver_image()
                break

    def match_client(self):
        self.client = self.clnts[0]

    def deliver_image(self):
        while True:
            # String형의 이미지를 수신받아서 이미지로 변환하고 화면에 출력
            length = self.recv_image(16)

            if length is None:
                print("deliver_image length is None break")
                break
            elif length.decode() == "FINISHED":
                print("host terminated")
                self.sock.close()
                break

            string_data = self.recv_image(int(length))
            # host와 연결된 client에게 그대로 보냄
            self.client.send(str(len(string_data)).ljust(16).encode())
            self.client.send(string_data)

    def recv_image(self, count):
        buffer = b''

        while count:
            temp = self.sock.recv(count)

            if not temp:
                return None

            buffer += temp
            count -= len(temp)

        return buffer


def esc_pressed():
    keyboard.wait('esc')


if __name__ == '__main__':
    t = Thread(target=esc_pressed)
    t.start()

    run_server()

    t.join()

    print("server end")