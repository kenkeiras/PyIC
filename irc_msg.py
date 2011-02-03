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

from irc_codes import *
from dcc import *

# Irc message type containing the basic information
class irc_msg:
    by = "" # Sender nickname
    origin = "" # Sender info
    to = "" # Receiver (you... or the channel)
    private = False # Is client to client
    type = "" # Type of message
    msg = ""
    multiline = False
    multiline_end = False
    ctcp = False
    ctcp_msg = ""
    def __init__(self,s):
        # Extracting "FROM"
        if (s[0]==":"):
            s = s[1:]
        i=-1
        try:
            i = s.index(" ")
        except:
            i=-1
        if (i<0) or (i>=len(s)):
            return 
        self.by = s[:i]
        s = s[i+1:]
        i=-1
        try:
            i = self.by.index("!")
        except:
            i=-1
        if (i>=0) and (i<len(self.by)):
            self.origin = self.by[i+1:]
            self.by = self.by[:i]

        # Extracting "TYPE"
        i=-1
        try:
            i = s.index(" ")
        except:
            i=-1
        if (i<0) or (i>len(s)):
            return 
        self.type = s[:i]
        s = s[i+1:]

        # Extracting "TO"
        i=-1
        try:
            i = s.index(" ")
        except:
            i=-1
        if (i<0) or (i>len(s)):
            return 
        self.to = s[:i]
        s = s[i+1:]

        try:
            if (s[0] == ":"):
                s = s[1:]
            elif (s[0:2] == " :"):
                s = s[2:]

        except:
            pass

        self.msg = s

        # Extracting "CTCP"
        i=-1
        try:
            i = s.index(chr(1))
        except:
            i=-1
        if (i>=0) and (i<=len(s)):
            self.ctcp = True
            self.ctcp_msg = s[i+1:]

            i = self.ctcp_msg.index(chr(1))
            if (i>=0) and (i<=len(self.ctcp_msg)):
                self.ctcp_msg = self.ctcp_msg [:i]
            dcc = decompose_dcc_offer(self.ctcp_msg)
            if (dcc!=False):
                self.ip = dcc[0]
                self.port = dcc[1]
                self.file = ""
                self.turbo = dcc[3]
                self.size = dcc[4]
                try:
                    self.file += dcc[2]
                except:
                    pass
                self.type = DCC_SEND_OFFER
                return

        # Creo que esto sera mejor pasarlo a un diccionario :-/
        # Userlist
        if (self.type == RPL_LISTSTART):
            multiline = True
        elif (self.type == RPL_LIST):
            multiline = True
        elif (self.type == RPL_LISTEND):
            multiline = True
            multiline_end = True

        # Message of the day
        elif (self.type == RPL_MOTDSTART):
            multiline = True
        elif (self.type == RPL_MOTD):
            multiline = True
        elif (self.type == RPL_ENDOFMOTD):
            multiline = True
            multiline_end = True

        # WHOIS
        elif (self.type == RPL_WHOISUSER):
            multiline = True
        elif (self.type == RPL_WHOISSERVER):
            multiline = True
        elif (self.type == RPL_WHOISOPERATOR):
            multiline = True
        elif (self.type == RPL_WHOISIDLE):
            multiline = True
        elif (self.type == RPL_WHOISCHANNELS):
            multiline = True
        elif (self.type == RPL_ENDOFWHO):
            multiline = True
            multiline_end = True

        # WHOWAS
        elif (self.type == RPL_WHOWASUSER):
            multiline = True
        elif (self.type == RPL_ENDOFWHOWAS):
            multiline = True
            multiline_end = True

        # WHO
        elif (self.type == RPL_WHOREPLY):
            multiline = True
        elif (self.type == RPL_ENDOFWHO):
            multiline = True
            multiline_end = True

        # Names
        elif (self.type == RPL_NAMEREPLY):
            multiline = True
        elif (self.type == RPL_ENDOFNAMES):
            multiline = True
            multiline_end = True

        # Links
        elif (self.type == RPL_LINKS):
            multiline = True
        elif (self.type == RPL_ENDOFLINKS):
            multiline = True
            multiline_end = True

        # Banlist
        elif (self.type == RPL_BANLIST):
            multiline = True
        elif (self.type == RPL_ENDOFBANLIST):
            multiline = True
            multiline_end = True

        # Info
        elif (self.type == RPL_INFO):
            multiline = True
        elif (self.type == RPL_ENDOFINFO):
            multiline = True
            multiline_end = True

        # Users
        elif (self.type == RPL_USERS):
            multiline = True
        elif (self.type == RPL_ENDOFUSERS):
            multiline = True
            multiline_end = True


