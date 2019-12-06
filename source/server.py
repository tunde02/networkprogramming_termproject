import socket
from threading import Thread


class ClientHandler:
    BUFSIZE = 1024
    terminator = "FINISHED"

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.host = None
        self.connection_index = -1

        t = Thread(target=self.recv_msg)
        t.start()

    def recv_msg(self):
        while True:
            try:
                data = self.sock.recv(self.BUFSIZE)
            except ConnectionResetError:
                print("Client{}와의 연결이 끊겼습니다".format(self.addr))
                disconnect_clnt(self)
                break

            msg = data.decode().split("|")

            if msg[0] == self.terminator:
                print("Client{}가 접속을 종료하였습니다".format(self.addr))
                disconnect_clnt(self)
                break
            elif msg[0] == "CONNECT":
                self.connection_index = link(self)
                self.host.sendall(("GAME|" + msg[1] + "|").encode())
            elif msg[0] == "DISCONNECT":
                unlink(self.connection_index)
                continue

            if self.host is not None:
                try:
                    self.host.sendall(data)
                except OSError:
                    unlink(self.connection_index)


class HostHandler:
    BUFSIZE = 1024
    terminator = "FINISHED"

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.client = None
        self.connection_index = -1

        t = Thread(target=self.recv_msg)
        t.start()

    def recv_msg(self):
        while True:
            try:
                length = self.sock.recv(32) # 64
            except ConnectionResetError:
                print("Host{}와의 연결이 끊겼습니다".format(self.addr))
                disconnect_host(self)
                break

            try:
                msg = length.decode().split("|")
                if msg[0] == "SCREENSIZE":
                    self.client.sendall(length)
                    continue
                elif msg[0] == self.terminator:
                    print("Host{}가 접속을 종료하였습니다".format(self.addr))
                    disconnect_host(self)
                    break
            except UnicodeDecodeError:
                print("Unicode Error")
                pass

            try:
                string_data = self.recv_image(int(length))
            except ValueError:
                continue

            # host와 연결된 client에게 이미지를 그대로 보냄
            try:
                self.client.send(str(len(string_data)).ljust(16).encode())
                self.client.send(string_data)
            except AttributeError:
                continue
            except OSError:
                self.sock.sendall("DISCONNECT|".encode())

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


def run_server(ip='127.0.0.1', port=1080):
    global hosts, clnts, connections, linkable_hosts

    with socket.socket() as sock:
        sock.bind((ip, port))

        print("Server Started...")

        while True:
            sock.listen(3)
            conn, addr = sock.accept()

            sock_type = conn.recv(10)

            if sock_type.decode() == "client":
                print("New Client Accessed - {}".format(addr))
                new_clnt = ClientHandler(sock=conn, addr=addr)
                clnts.append(new_clnt)

                if len(hosts) > 0:
                    notice_clients()
            else:
                print("New Host Accessed - {}".format(addr))
                new_host = HostHandler(sock=conn, addr=addr)
                hosts.append(new_host)
                linkable_hosts += 1

                connections.append(0)

                if len(clnts) > 0:
                    notice_clients()

        sock.close()


def disconnect_clnt(clnt):
    global clnts, connections

    if clnt.connection_index != -1:
        unlink(clnt.connection_index)

    clnts.remove(clnt)
    clnt.sock.close()


def disconnect_host(host):
    global hosts, connections, linkable_hosts

    if host.connection_index != -1:
        unlink(host.connection_index)

    hosts.remove(host)
    host.sock.close()

    notice_clients()


def link(clnt):
    '''
    연결 가능한 Host를 찾아 Client와 연결하고
    connection_index를 반환
    '''

    global clnts, hosts, connections, linkable_hosts

    print("Client와 Host의 연결을 시작합니다")

    # 연결 가능한 Host가 없으면 link()를 호출할 수도 없으므로 예외처리 필요 없음
    connection_index = connections.index(0)
    clnt_index = clnts.index(clnt)

    # 연결을 관리하기위한 conneciton 생성
    connections[connection_index] = (clnt_index, connection_index)

    # Client와 Host 연결
    clnts[clnt_index].host = hosts[connection_index].sock
    clnts[clnt_index].connection_index = connection_index
    hosts[connection_index].client = clnts[clnt_index].sock
    hosts[connection_index].connection_index = connection_index

    linkable_hosts -= 1

    notice_clients()

    return connection_index


def unlink(connection_index):
    '''
    인자값으로 들어온 connection_index를 이용해 해당 인덱스의
    연결을 끊음
    '''

    global clnts, hosts, connections, linkable_hosts

    print("Client와 Host의 연결을 종료합니다")

    clnt_index = connections[connection_index][0]
    host_index = connections[connection_index][1]

    clnts[clnt_index].host = None
    clnts[clnt_index].connection_index = -1
    hosts[host_index].client = None
    hosts[connection_index].connection_index = -1

    # Client와 Host에게 연결이 끊어졌음을 알림
    try:
        clnts[clnt_index].sock.sendall("DISCONNECT|".encode())
    except OSError:
        # print("Client에게 DISCONNECT 메시지 전송 실패")
        pass

    try:
        hosts[host_index].sock.sendall("DISCONNECT|".encode())
        linkable_hosts += 1
    except OSError:
        # print("Host에게 DISCONNECT 메시지 전송 실패")
        pass

    connections[connection_index] = 0

    notice_clients()


def notice_clients():
    '''
    Host와 연결되어 있지 않은 모든 Client들에게
    연결 가능한 Host의 수를 알리는 함수
    '''

    global clnts, linkable_hosts

    notice = "HOSTS|" + str(linkable_hosts) + "|"

    for c in clnts:
        if c.connection_index == -1:
            c.sock.sendall(notice.encode())


if __name__ == '__main__':
    clnts = []
    hosts = []
    connections = []
    linkable_hosts = 0

    run_server("192.168.0.11")

    print("Server End")