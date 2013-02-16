# DCC

from threading import Thread
import socket


def ntop(i):
    """Converts a port number to a string"""
    ip = ""
    ip += str((i / 16777216) % 256) + "."
    ip += str((i / 65536) % 256) + "."
    ip += str((i / 256) % 256) + "."
    ip += str(i % 256)
    return ip


def int2uint4(n):
    """For sending 4 byte's throught a socket"""
    u = ""
    for i in range(0, 4):
            u = chr(n % 256) + u
            n /= 256
    return u


def clean_msg(s):
    """Cleans the message"""
    for c in range(1, 10):
        s = s.replace(ord(c), '')
    return s


def decompose_dcc_offer(m):
    """Get DCC offer"""""

    if ("DCC SEND" in m):
        l = m.index("DCC SEND")
        turbo = False
    else:
        if ("DCC TSEND" in m):
            l = m.index("DCC TSEND")
            turbo = True
        else:
            return False
    if (" " in m):
        aux = m[m.index(" ", l + 4):]
        if (len(aux) < 1):
            return False
        while (aux[0] == " "):
            aux = aux[1:]
            if (len(aux) < 1):
                return False
        if (aux[0] == '"'):
            if ('"' in aux[1:]):
                fname = aux[1: aux.index('"', 1)]
                aux = aux[aux.index('"', 1) + 1:]
            else:
                return False
        elif (aux[0] == "'"):
            if ("'" in aux[1:]):
                fname = aux[1: aux.index("'", 1)]
                aux = aux[aux.index("'", 1) + 1:]
        elif (' ' in aux):
            fname = aux[: aux.index(" ")]
            aux = aux[aux.index(" ") + 1:]
        else:
            return False
    # To avoid path's in the filename
        fname = fname.split("/")[-1]
        fname = fname.split("\\")[-1]
        if (len(aux) < 1):
            return False
        while (aux[0] == " "):
            aux = aux[1:]
        if (len(aux) > 1) and (" " in aux):
            ip = int(aux[: aux.index(" ")])
            aux = aux[aux.index(" ") + 1:]
            port = int(aux[: aux.index(" ")])
            ip = ntop(ip)
            if (" " in aux):
                aux = aux[aux.index(" ") + 1:]
                size = int(aux)
                return (ip, port, fname, turbo, size)
            if (ip != ""):
                return (ip, port, fname, turbo, -1)
        else:
            return False
    return False


class dcc_download(Thread):
    # Constructor
    def __init__(self,
                  msg,
                  func=None,
                  buffsize=1024):

        Thread.__init__(self)

        self.buffsize = buffsize
        self.turbo = msg.turbo
        self.ip = msg.ip
        self.port = msg.port
        self.f = open(msg.file, "wb")
        self.func = func
        self.size = msg.size

    # Here starts the thread
    def run(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.port))
        r_size = 0
        while (r_size < self.size) or (self.size == -1):
            c = sock.recv(self.buffsize)
            if (not self.turbo):
                try:
                    r_size += len(c)
                    sock.send(int2uint4(len(c)))
                except:
                    break
            if (len(c) < 1):
                break
            self.f.write(c)
        if (r_size >= self.size):
            sock.send(int2uint4(0))
        self.f.close()
        sock.close()
        if (self.func is not None):
            self.func()
