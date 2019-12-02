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
                new_clnt = ClientHandler(sock=conn, addr=addr, clnt_index=len(clnts))
                clnts.append(new_clnt)
                new_clnt.clnts = clnts
                new_clnt.hosts = hosts
                new_clnt.connects = connects

                if len(hosts) > 0:
                    notice_clients(clnts, hosts)
            else:
                print("New Host Accessed")
                new_host = HostHandler(sock=conn, addr=addr, host_index=len(hosts))
                hosts.append(new_host)
                connects.append(False)
                new_host.clnts = clnts
                new_host.hosts = hosts
                new_host.connects = connects
                
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
            print("find host at : {}".format(i))
            return i
        i = i + 1


def notice_clients(clnts, hosts):
    notice = "HOSTS|" + str(len(hosts))
    for i in clnts:
        if i is not None:
            i.sock.sendall(notice.encode())


class ClientHandler:
    BUFSIZE = 1024
    terminator = "FINISHED"
    clnts = []
    hosts = []
    connects = []

    def __init__(self, sock, addr, clnt_index):
        self.sock = sock
        self.addr = addr
        self.host = None
        self.clnt_index = clnt_index
        self.connects_index = 0

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
                self.clnts[self.clnt_index] = None
                if len(self.connects) > 0:
                    self.connects[self.connects_index] = False
                    self.connects_index = 0
                break
            elif msg[0] == "CONNECT":
                print("match client to host : " + str(data))
                self.connect_host(msg[1])
                # break
            elif msg[0] == "DISCONNECT":
                print("disconnect client with host")
                self.disconnect_host()
                continue

            if self.host is not None:
                self.host.sock.sendall(data)

            # print('Received : {} << {}'.format(msg, self.addr))
            # self.host.sendall(data)

    def connect_host(self, game):
        self.connects_index = find_host(self.connects)
        self.host = self.hosts[self.connects_index]
        self.connects[self.connects_index] = True
        self.host.connect_client(self.sock)

        print("GAME|" + game)
        self.host.sock.sendall(("GAME|" + game).encode())
    
    def disconnect_host(self):
        self.host.sock.sendall("DISCONNECT".encode())
        self.host.disconnect_client()
        print("disconnection message sent")
        self.host = None
        self.connects[self.connects_index] = False

        self.sock.sendall(str("HOSTS|" + str(len(self.hosts))).encode())


class HostHandler:
    BUFSIZE = 1024
    terminator = "FINISHED"
    clnts = []
    hosts = []
    connects = []

    def __init__(self, sock, addr, host_index):
        self.sock = sock
        self.addr = addr
        self.client = None
        self.host_index = host_index
        self.connects_index = 0

        t = Thread(target=self.recv_msg)
        t.start()

    def recv_msg(self):
        while True:
                # msg = self.sock.recv(64)

                # if msg is None:
                #     print("deliver_image length is None break")
                #     break
                # elif msg.decode().split("|")[0] == "SCREENSIZE":
                #     print("===send size to client===")
                #     self.client.send(msg)
                #     continue
            # String형의 이미지를 수신받아서 이미지로 변환하고 화면에 출력
            length = self.sock.recv(64)
            # print(length)
            # if length[0] == b"\x":
            #     print("deliver_image length is None break")
            #     break
            try:
                msg = length.decode().split("|")
                if msg[0] == "SCREENSIZE":
                    print("===send size to client===")
                    self.client.send(length)
                    continue
                elif msg[0] == self.terminator:
                    self.client.sendall("DISCONNECT".encode())
                    break
            except UnicodeDecodeError:
                print("unicode error")
                pass

            # if self.client is None:
            #     continue

            string_data = self.recv_image(int(length))

            # host와 연결된 client에게 그대로 보냄
            try:
                self.client.send(str(len(string_data)).ljust(16).encode())
                self.client.send(string_data)
            except AttributeError:
                continue

        self.sock.close()
        print("hosthandler end")

    def connect_client(self, sock):
        self.client = sock

    def disconnect_client(self):
        self.client.sendall("DISCONNECT".encode())
        # self.client.disconnect_host()
        # print("disconnection message sent")
        self.client = None
        self.connects[self.connects_index] = False

        notice_clients(self.clnts, self.hosts)

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