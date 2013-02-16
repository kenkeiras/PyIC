# -*- encoding: utf-8 -*-
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


from helpers import multiple_line_end, multiple_line, codes
from dcc import ntop, int2uint4, clean_msg, decompose_dcc_offer, dcc_download

import socket
import select


VERSION = "0.3"


def clean_usr(usr):
    if usr.startswith("@"):
        return usr[1:]
    elif usr.startswith("+"):
        return usr[1:]
    else:
        return usr


def getline(sock, timeout=None):
    """Retrieve a single line from the socket"""
    l = ""
    while True:
        i, o, e = select.select([sock], [], [], timeout)
        if timeout is not None and i == []:
            l = None
            break
        else:
            r = sock.recv(1)
            if (len(r) < 1):
                raise Exception("Connection closed")
            if (r == "\n"):
                break
            elif (r != "\r"):
                l += r
    return l


class split_msg(object):
    """Irc message type containing the basic information"""
    by = ""           # Sender nickname
    origin = ""       # Sender info: user@host
    to = ""           # Receiver (you... or the channel)
    private = False  # Is client to client
    type = ""        # Type of message
    msg = ""
    multiline = False
    multiline_end = False
    ctcp = False
    ctcp_msg = ""
    raw = ""

    # Constructor
    def __init__(self, s):
        #":by!origin type to:msg"

        if not s:
            return None

        self.raw = s
        block = s.split(' ', 2)

        block[0] = block[0][1:]
        if ("!" in block[0]):
            first = block[0].split('!')
            self.by = first[0]
            self.origin = first[1]
        else:
            self.by = block[0]

        if  block[1].endswith(":"):
            clean = block[1][:-1].upper()
        else:
            clean = block[1].upper()
        self.type = clean
        if (self.type in multiple_line):
            multiline = True
            if (self.type in multiple_line_end):
                multiline_end = True

        if (len(block[2]) > 0):
            parts = block[2].split(' ', 1)
            self.to = parts[0]
            if len(parts) == 2 and parts[1].startswith(":"):
                    self.msg = parts[1][1:]
            elif len(parts) == 2:
                    self.msg = parts[1]

        s = self.msg
        i = -1
        if (chr(1) in s):
            i = s.index(chr(1))
        if (i >= 0) and (i <= len(s)):
            self.ctcp = True
            self.ctcp_msg = s[i + 1:]
            if (chr(1) in self.ctcp_msg):
                i = self.ctcp_msg.index(chr(1))
            else:
                return
            if (i >= 0) and (i <= len(self.ctcp_msg)):
                self.ctcp_msg = self.ctcp_msg[:i]
            dcc = decompose_dcc_offer(self.ctcp_msg)
            if (dcc is not False):
                self.ip = dcc[0]
                self.port = dcc[1]
                self.file = ""
                self.turbo = dcc[3]
                self.size = dcc[4]
                try:
                    self.file += dcc[2]
                except:
                    pass
                self.type = codes["DCC_SEND_OFFER"]
                return


class irc_client(object):
    """Irc Client main class"""
    motd = ""
    msgBuff = []

    def send(self, deliver):
        """Send a message through the socket"""
        self.sock.send(deliver + "\r\n")

    def get_motd(self):
        """Show the Message Of The Day"""
        return self.motd

    def away(self, status=None):
        if status is None:
            self.send("AWAY")
        else:
            self.send("AWAY " + status)

    def set_chanmode(self, channel, mode, data=None):
        """Set channel mode"""
        if data is None:
            self.send("MODE " + channel + " " + mode)
        else:
            self.send("MODE " + channel + " " + mode + " " + str(data))

    def set_mode(self, mode):
        """Set own user mode"""
        self.send("MODE " + self.nick + " " + mode)

    def ping(self, to):
        """Send a ping to a server or user"""
        self.send("PING " + to)

    def collect_who_data(self):
        """Collect WHOIS/WHOWAS data"""
        m = self.getmsg(True)
        data = {"channels": []}
        while (m.type != codes["RPL_ENDOFWHOWAS"]) and \
               (m.type != codes["RPL_ENDOFWHOIS"]) and \
               (m.type != codes["ERR_NOSUCHNICK"]):

            if (m.type == codes["RPL_WHOISUSER"]):
                d = m.msg.split(":")
                data["real_name"] = d[1]
                d = d[0].split(" ")
                data["nick"] = d[0]
                data["user"] = d[1]
                data["host"] = d[2]
            elif (m.type == codes["RPL_WHOWASUSER"]):
                d = m.msg.split(":")
                data["real_name"] = d[1]
                d = d[0].split(" ")
                data["nick"] = d[0]
                data["user"] = d[1]
                data["host"] = d[2]
            elif (m.type == codes["RPL_WHOISSERVER"]):
                d = m.msg.split(":")
                data["server_info"] = d[1]
                d = d[0].split(" ")
                data["server"] = d[1]
            elif (m.type == codes["RPL_WHOISOPERATOR"]):
                data["isOp"] = True
            elif (m.type == codes["RPL_WHOISIDLE"]):
                d = m.msg.split(":")
                data["idle"] = d[1]
                d = d[0].split(" ")
                data["time"] = d[1]
            elif (m.type == codes["RPL_WHOISCHANNELS"]):
                d = m.msg.split(":")
                data["channels"] += d[1].strip().split(" ")
            else:
                self.msgBuff.append(m)

            m = self.getmsg(True)
        return data

    def send_whois(self, user):
        """Ask for user information"""
        self.send("WHOIS " + user)

    def whois(self, user):
        """Read for user information"""
        self.send_whois(user)
        data = self.collect_who_data()
        return data

    def send_whowas(self, user):
        """Ask for user (that no longer exists) information"""
        self.send("WHOWAS " + user)

    def whowas(self, user):
        """ Read for former user information"""
        self.send_whowas(user)
        data = self.collect_who_data()
        return data

    def set_topic(self, channel, topic):
        """Set a channel topic"""
        self.send("TOPIC " + channel + " :" + topic)

    def retr_topic(self, channel):
        """Retrieves a channel topic (has to check messages then)"""
        self.send("TOPIC " + channel)

    def get_topic(self, channel):
        """ Reads the current topic on a channel"""
        self.retr_topic(channel)
        while (True):
            m = self.getmsg(True)
            if (m.type == codes["RPL_TOPIC"]):
                return m.msg.split(":")[-1]
            elif (m.type == codes["RPL_NOTOPIC"]):
                return False
            self.msgBuff.append(m)

    def retr_names(self, channel):
        """Retrieves a nick list"""
        self.send("NAMES " + channel)

    def get_users(self, channel):
        """ Reads the nick list"""
        self.retr_names(channel)
        data = []
        m = self.getmsg(True)
        while (m.type != codes["RPL_ENDOFNAMES"]):
            if (m.type == codes["RPL_NAMEREPLY"]):
                data += m.msg.split(":")[-1].strip().split(" ")
            else:
                self.msgBuff.append(m)
            m = self.getmsg(True)
        return data

    def retr_channels(self):
        """Retrieves a channel list"""
        self.send("LIST")

    def get_channels(self):
        """Read the channel list"""
        self.retr_channels()
        channels = []
        m = self.getmsg(True)
        while (m.type != codes["RPL_LISTEND"]):
            if (m.type == codes["RPL_LISTSTART"]):
                pass
            elif (m.type == codes["RPL_LIST"]):
                if (":" in m.msg):
                    i = m.msg.index(":")
                    topic = m.msg[i + 1:]
                    d = m.msg[: i].strip().split(" ")
                    if (len(d) > 1):
                        channels.append((d[0], d[1], topic))
            else:
                self.msgBuff.append(m)
            m = self.getmsg(True)
        return channels

    def invite(self, nick, channel):
        """Invite someone to a channel"""
        self.send("INVITE " + nick + " " + channel)

    def kick(self, channel, nick, comment=None):
        """Remove a user from a channel"""
        if comment is None:
            self.send("KICK " + channel + " " + nick)
        else:
            self.send("KICK " + channel + " " + nick + " : " + str(comment))

    def leave_channel(self, channel):
        """Quit the channel"""
        self.send("PART " + channel)

    def quit(self, msg="Client quit"):
        """ Quit the server"""
        self.send("QUIT :" + str(msg))
        self.sock.close()

    def join(self, channel, passwd=None):
        """Join a channel"""
        if channel.startswith("#") or channel.startswith("&"):
            if passwd is None:
                self.send("JOIN " + channel)
            else:
                self.send("JOIN " + channel + " " + passwd)
        else:
            print "Error " + channel + " " + passwd

    def change_nick(self, nick):
        """Changes the nickname"""
        self.nick = nick
        self.send("NICK " + nick)

    def refresh_motd(self):
        """Ask for the MOTD"""
        self.send("MOTD")

    def getmsg(self, fresh=False, timeout=None):
        """Receives a message (and transparently answers to server ping)"""
        if (not fresh) and (len(self.msgBuff) > 0):
            return self.msgBuff.pop(0)
        while True:
            s = getline(self.sock, timeout)
            if s is None:
                return None
            if (len(s) > 3):
                if (s.lower()[0:4] == "ping"):
                    self.pong(s)
                    continue
            m = split_msg(s)
            if m is None:
                return None
            else:
                if ("version" in m.ctcp_msg.lower()):
                    self.sendVer(m.by)
                    continue
                elif (m.type == codes["RPL_MOTD"]):
                    self.motd += m.msg + "\n"
                    continue
                elif (m.type == codes["RPL_MOTDSTART"]):
                    self.motd = ""
                    continue
                return m

    def sendmsg(self, to, msg):
        """Send a message (msg) to a receiver (to), which can
        be a channel or a user"""
        self.send("PRIVMSG " + to + " :" + msg)

    def notice(self, to, msg):
        """Same as sendmsg, but MUSTN'T be answered"""
        self.send("NOTICE " + to + " :" + msg)

    def pong(self, ping):
        """Answer a ping"""
        self.send("PONG" + ping[4:])

    def sendVer(self, by):
        """Answer a version request"""
        self.notice(by, chr(1) + VERSION + chr(1))

    def connect_to_server(self, serverpwd, pwd, use_ssl):
        """Connecting to the server and login"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if use_ssl:
            import ssl
            self.sock = ssl.wrap_socket(self.sock)
        self.sock.connect((self.server, self.port))
        if (serverpwd is not None):
            self.send("PASS " + serverpwd)
        self.change_nick(self.nick)
        m = self.getmsg()
        self.send("USER " + self.username + " " + self.username2 +
                    " " + self.server + ": " + self.fullname)
        while (m.type not in (codes["RPL_ENDOFMOTD"], codes["ERR_NOMOTD"])):
            m = self.getmsg()
        if (pwd is not None):
            self.sendmsg("NickServ", "IDENTIFY " + pwd)

    def __init__(self,
                  nick,
                  server,
                  port=6667,
                  ssl=False,
                  username="user",
                  username2="user",
                  fullname="user Name",
                  serverpwd=None,
                  pwd=None):
        """Object constructor"""
        self.nick = nick
        self.server = server
        self.port = port
        self.ssl = ssl
        self.username = username
        self.username2 = username2
        self.fullname = fullname
        self.connect_to_server(pwd, serverpwd, ssl)
