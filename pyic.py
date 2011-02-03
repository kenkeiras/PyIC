"""
    Simple irc client

    Copyright (c) 2010 kenkeiras <kenkeiras@gmail.com>
    Under GPLv3 license (or later)

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

from irc_msg import *
from irc_codes import *

VERSION = "PyIC 0.1"

import socket

# Retrieve a single line from the socket
def getline(s):
    l=""
    while 1:
        c=s.recv(1)
        if (len(c)<1):
            raise Exception("Connection closed")
        if (c=="\n"):
            break
        elif (c!="\r"):
            l+=c
    return l

# Irc Client main class
class irc_client:

    # Set's channel mode
    def set_chanmode(self,channel,mode,data = None):
        if (data == None):
            self.sock.send("MODE "+channel+" "+mode+"\r\n")
        else:
            self.sock.send("MODE "+channel+" "+mode+" "+str(data)+"\r\n")

    # Set's user own mode
    def set_mode(self,mode):
        self.sock.send("MODE "+self.nick+" "+mode+"\r\n")

    # Send's a ping to a server or user (have to check messages for the answer)
    def ping(self,to):
        self.sock.send("PING "+to+"\r\n")

    # Ask's for user information
    def whois(self,user):
        self.sock.send("WHOIS "+nick+"\r\n")

    # Ask's for user (that no longer exists) information
    def whowas(self,user):
        self.sock.send("WHOWAS "+nick+"\r\n")
    
    # Set's a channel topic
    def set_topic(self,channel,topic):
        self.sock.send("TOPIC "+channel+" "+topic+"\r\n")

    # Retrieves a channel topic (has to check messages then)
    def get_topic(self,channel):
        self.sock.send("TOPIC "+channel+"\r\n")

    # Retrieves a nick list
    def get_names(self,channel):
        self.sock.send("NAMES "+channel+"\r\n")

    # Retrieves a channel list
    def get_channels(self):
        self.sock.send("LIST\r\n")

    # Invites someone to a channel
    def invite(self,nick,channel):
        self.sock.send("INVITE "+nick+" "+channel+"\r\n")

    # Removes a user from a channel
    def kick(self,channel,nick,comment=None):
        if (comment == None ):
            self.sock.send("KICK "+channel+" "+nick+"\r\n")
        else:
            self.sock.send("KICK "+channel+" "+nick+" : "+str(comment)+"\r\n")

    # Quit the channel
    def quit_channel(self,channel):
        self.sock.send("PART "+channel+"\r\n")

    # Quit's the server
    def quit(self,msg = "Client quit"):
        self.sock.send("QUIT :"+str(msg)+"\r\n")
        self.sock.close()

    # Joins a channel
    def join(self,channel,passwd=None):
        if (channel[0] == "#"):
            channel = channel[1:]
        if (passwd == None):
            self.sock.send("JOIN #"+channel+"\r\n")
        else:
            self.sock.send("JOIN &"+channel+" "+passwd+"\r\n")

    # Changes the nickname
    def chng_nick(self,nick):
        self.nick = nick
        self.sock.send("NICK "+nick+"\r\n")

    # Receives a message (and transparently answers to server ping's)
    def getmsg(self):
        while 1:
            s = getline(self.sock)
            try:
                if (s.lower()[0:4] == "ping"):
                    self.pong(s)
                    continue
            except:
                pass
            m = irc_msg(s)
            try:
                if ("version" in  m.ctcp_msg.lower()):
                    self.sendVer(m.by)
                    continue
            except:
                pass
            return m


    # Sends a message (msg) to a receiver (to), that can be a channel or a user
    def sendmsg(self,to,msg):
        self.sock.send("PRIVMSG "+to+" :"+msg+"\r\n")

    # Same as sendmsg, but MUSTN'T be answered
    def notice(self,to,msg):
        self.sock.send("NOTICE "+to+" :"+msg+"\r\n")

    # Answers a ping
    def pong(self,ping):
        self.sock.send("PONG"+ping[4:]+"\r\n")

    # Answers a version request
    def sendVer(self,by):
        self.notice(by,chr(1)+VERSION+chr(1))

    # Connecting to the server and login
    def connect_to_server(self,passwd,serverpasswd):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((self.server,self.port))
        if (serverpasswd != None):
            self.sock.send("PASS "+serverpasswd+"\r\n")
        self.getmsg()
        self.chng_nick(self.nick)
        self.sock.send("USER "+self.username+" "+self.username2+" "+self.server+": "+self.fullname+"\r\n")
        if (passwd != None):
            self.sendmsg("NickServ","IDENTIFY "+passwd)

    # Object builder
    def __init__(self,nick,server,port=6667,username="user",username2="user",
        fullname="user Name",serverpasswd=None,passwd=None):
        self.nick = nick
        self.server = server
        self.port = port
        self.username = username
        self.username2 = username2
        self.fullname = fullname
        self.connect_to_server(passwd,serverpasswd)
