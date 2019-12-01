import socket
import keyboard
from threading import Thread


def run_server(ip='127.0.0.1', port=1080):
    with socket.socket() as sock:
        sock.bind((ip, port))

        print("Server Started...")

        clnts = []
        hosts = []
        connects = []
        while True:
            sock.listen(3)
            conn, addr = sock.accept()
            # connects.append(clntSock)

            sock_type = conn.recv(10)

            if sock_type.decode() == "client":
                print("New Client Accessed")
                new_clnt = ClientHandler(sock=conn, addr=addr)
                clnts.append(new_clnt)
                new_clnt.connects = connects
                new_clnt.hosts = hosts

                if len(hosts) > 0:
                    notice_clients(clnts, hosts)
            else:
                print("New Host Accessed")
                new_host = HostHandler(sock=conn, addr=addr)
                hosts.append(new_host)
                connects.append(False)
                print("see my len : {}".format(len(connects)))
                if len(clnts) > 0:
                    clnts[0].hosts = hosts
                    clnts[0].connects = connects
                    notice_clients(clnts, hosts)

        sock.close()
        print("Server end")


def find_host(connects):
    print("===connects' len : {}===".format(len(connects)))
    i = 0
    for temp in connects:
        if temp is False:
            print("find host! : {}".format(i))
            return i
        i = i + 1


def notice_clients(clnts, hosts):
    notice = "HOSTS|" + str(len(hosts))
    for i in clnts:
        i.sock.sendall(notice.encode())


class ClientHandler:
    BUFSIZE = 1024
    terminator = "FINISHED"
    hosts = []
    connects = []

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.host = None
        self.c_index = 0

        t = Thread(target=self.recv_msg)
        t.start()

    def recv_msg(self):
        while True:
            try:
                data = self.sock.recv(self.BUFSIZE)
            except ConnectionAbortedError:
                break

            msg = data.decode().split("|")

            if msg[0] == self.terminator:
                print("Client Exited")
                self.sock.close()
                if len(self.connects) > 0:
                    self.connects[self.c_index] = False
                    self.c_index = 0
                break
            elif msg[0] == "CONNECT":
                print("match client to host : " + str(data))
                self.match_host(msg[1])
                # break

            if self.host is not None:
                self.host.sock.sendall(data)

            # print('Received : {} << {}'.format(msg, self.addr))
            # self.host.sendall(data)

    def match_host(self, game):
        self.c_index = find_host(self.connects)
        print("===gello?===")
        self.host = self.hosts[self.c_index]
        self.connects[self.c_index] = True
        self.host.match_client(self.sock)
        print("GAME|" + game)
        self.host.sock.sendall(("GAME|" + game).encode())
        # while True:
        #     data = self.sock.recv(self.BUFSIZE)
        #     msg = data.decode()

        #     if msg == self.terminator:
        #         print("terminated")
        #         self.host.sendall("FINISHED".encode())
        #         self.sock.close()
        #         break
        #     # print("send client's msg to host")
        #     self.host.sendall(data)


class HostHandler:
    BUFSIZE = 1024
    terminator = "FINISHED"

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.client = None

        t = Thread(target=self.recv_msg)
        t.start()

    def recv_msg(self):
        # while True:
        #     trigger = self.sock.recv(1024)
        #     if trigger.decode() == "s":
        #         self.match_client()
        #         self.deliver_image()
        #         break
        while True:
            # String형의 이미지를 수신받아서 이미지로 변환하고 화면에 출력
            length = self.sock.recv(64)

            if length is None:
                print("deliver_image length is None break")
                break
            elif length.decode().split("|")[0] == "SCREENSIZE":
                print("===send size to client===")
                self.client.send(length)
                continue

            string_data = self.recv_image(int(length))
            # host와 연결된 client에게 그대로 보냄
            self.client.send(str(len(string_data)).ljust(16).encode())
            self.client.send(string_data)

    def match_client(self, sock):
        self.client = sock

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
            try:
                temp = self.sock.recv(count)
            except ConnectionAbortedError:
                return None
            except ConnectionResetError:
                return None

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