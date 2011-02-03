"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import threading
import socket

# For sending 4 byte's throught a socket
def int2uint4(n):
    u = ""
    for i in range(0,4):
            u = chr(n%256) + u
            n /= 256
    return u

# DCC download thread
class dcc_download(threading.Thread):
    def __init__(self,msg,func=None,buffsize=1024):
        self.buffsize = buffsize
        self.turbo = msg.turbo
        self.ip = msg.ip
        self.port = msg.port
        self.f = open(msg.file,"wb")
        self.func = func
        self.size = msg.size

        threading.Thread.__init__(self)

    def run(self):
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((self.ip,self.port))
        r_size = 0
        while (r_size < self.size ) or  ( self.size == -1 ):
            c = sock.recv(self.buffsize)
            if (not self.turbo):
                try:
                    r_size += len(c)
                    sock.send(int2uint4(len(c)))
                except:
                    break
            if (len(c)<1):
                break
            self.f.write(c)
        if ( r_size >= self.size ):
            sock.send(int2uint4( 0 ))
        self.f.close()
        sock.close()
        if (self.func != None):
            self.func()

# Cleans the message
def clean_msg(s):
    charList = [chr(1),chr(2),chr(3),chr(4),chr(5),chr(6),chr(7),chr(8),chr(9)]
    for c in charList:
        s=s.replace(c,'')
    return s

# Converts a port number to a string
def ntop(i):
    ip=""
    ip+=str((i/16777216) %256 )+"."
    ip+=str((i/65536) %256 )+"."
    ip+=str((i/256) %256 )+"."
    ip+=str(i%256)
    return ip

# Get DCC offer
def decompose_dcc_offer(m):
    try:
        l = m.index("DCC SEND")
        turbo = False
    except:
        try:
            l = m.index("DCC TSEND")
            turbo = True
        except:
            return False
    try:
        aux = m[m.index(" ",l+4):]
        while (aux[0]==" "):
            aux = aux[1:]

        if (aux[0]=="\""):
            fname = aux[ 1 : aux.index("\"",1) ]
            aux = aux[ aux.index("\"",1) + 1 : ]
        elif (aux[0]=="\'"):
            fname = aux[ 1 : aux.index("\'",1) ]
            aux = aux[ aux.index("\'",1) + 1 : ]
        else:
            fname = aux[ : aux.index(" ")]
            aux = aux[aux.index(" ")+1 : ]

	# For avoid path's in the filename
        fname = fname.split("/")[-1]
        fname = fname.split("\\")[-1]

        while (aux[0]==" "):
            aux = aux[1:]

        ip = int(aux[ : aux.index(" ")])

        aux = aux[aux.index(" ")+1 : ]
        port = int(aux[ : aux.index(" ")])

        ip = ntop(ip)
        try:
            aux = aux[aux.index(" ")+1:]
            size = int(aux)
            return (ip,port,fname,turbo,size)
        except:
            pass
        if (ip!=""):
            return (ip,port,fname,turbo,-1)
    except:
        pass
    return False
