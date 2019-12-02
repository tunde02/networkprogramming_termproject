import tkinter


class ClientGUI:
    def __init__(self):
        self.initUI()

    def initUI(self):
        self.window=tkinter.Tk()
        self.window.title("Client")
        self.window.geometry("400x200+300+300")
        self.window.resizable(False, False)

        self.ip_entry = tkinter.Entry(self.window, width=10, borderwidth=4)
        self.ip_entry.insert(0, "127.0.0.1")
        self.port_entry = tkinter.Entry(self.window, width=10, borderwidth=4)
        self.port_entry.insert(0, "1080")

        self.connect_btn = tkinter.Button(self.window, text="Connect", width=10, height=2, overrelief="solid")
        quit_btn = tkinter.Button(self.window, text="Quit", width=10, height=2, overrelief="solid", command=self.window.destroy)
        # self.window.protocol("WM_DELETE_WINDOW", self.close_window)

        self.ip_entry.place(x=115, y=50)
        self.port_entry.place(x=215, y=50)
        self.connect_btn.place(x=115, y=100)
        quit_btn.place(x=215, y=100)

    def start_window(self):
        self.window.mainloop()

    def close_window(self):
        self.window.destroy()


class GameListGUI:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.initUI()

    def initUI(self):
        self.window=tkinter.Tk()
        self.window.title("Game List")
        self.window.geometry("600x700+300+200")
        self.window.resizable(False, False)

        addr_wrapper = tkinter.Frame(self.window, bd=1, relief="solid")
        addr_frame = tkinter.Frame(addr_wrapper)
        ip_label = tkinter.Label(addr_frame, text="IP : " + self.ip, relief="solid", width=25, height=2, bd=1)
        port_label = tkinter.Label(addr_frame, text="Port : " + str(self.port), relief="solid", width=15, height=2, bd=1)

        btn_wrapper = tkinter.Frame(self.window, bd=1, relief="solid")
        btn_frame = tkinter.Frame(btn_wrapper)
        self.disconnect_btn = tkinter.Button(btn_frame, text="Disconnect", width=20, height=2, overrelief="solid")
        self.quit_btn = tkinter.Button(btn_frame, text="Quit", width=20, height=2, overrelief="solid", command=self.window.destroy)

        # Game List
        list_frame = tkinter.Frame(self.window, bd=1, relief="solid")
        self.remote_btn = tkinter.Button(list_frame, text="Remote Control (0)", state="disabled", width=20, height=2, overrelief="solid")
        self.kart_btn = tkinter.Button(list_frame, text="Kart Rider (0)", state="disabled", width=20, height=2, overrelief="solid")

        # Set Layout
        ip_label.grid(row=0, column=0)
        port_label.grid(row=0, column=1)
        addr_frame.pack()
        addr_wrapper.pack(side="top", fill="both")

        self.remote_btn.pack()
        self.kart_btn.pack()
        list_frame.pack(expand=True, fill="both")

        self.disconnect_btn.grid(row=0, column=0, padx=25)
        self.quit_btn.grid(row=0, column=1, padx=25)
        btn_frame.pack()
        btn_wrapper.pack(side="bottom", fill="both")

    def start_window(self):
        self.window.mainloop()

    def close_window(self):
        self.window.destroy()

    def change_list(self, hosts):
        if int(hosts) <= 0:
            self.remote_btn.config(text="Remote Control (" + hosts + ")", state="disabled")
            self.kart_btn.config(text="Kart Rider (" + hosts + ")", state="disabled")
        else:
            self.remote_btn.config(text="Remote Control (" + hosts + ")", state="normal")
            self.kart_btn.config(text="Kart Rider (" + hosts + ")", state="normal")


if __name__ == "__main__":
    # window = ClientGUI()
    window = GameListGUI("192.168.56.11", 1080)
    window.start_window()