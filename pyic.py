# -*- encoding: utf-8 -*-
"""
   Simple Python Irc Client library

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

VERSION = "PyIC 0.2"

import socket

def clean_usr( usr ):
    return usr.replace( "@", "" )

# Retrieve a single line from the socket
def getline( sock ):
    l = ""
    while 1:
        c = sock.recv( 1 )
        if ( len( c ) < 1 ):
            raise Exception( "Connection closed" )
            
        if ( c == "\n" ):
            break
            
        elif ( c != "\r" ):
            l += c
    return l

########################################################################
# Irc Client main class
class irc_client:

    motd = ""
    msgBuff = []
    
    ####################################################################
    # Shows Message Of The Day
    def get_motd( self ):
        return self.motd

    ####################################################################
    # Set's channel mode
    def set_chanmode( self,
                      channel,
                      mode,
                      data = None ):
                           
        if (data == None):
            self.sock.send( "MODE " + channel + " " + mode + "\r\n" )

        else:
            self.sock.send( "MODE " + channel + " " + mode + " " +
                                                str( data ) + "\r\n" )

    ####################################################################
    # Set's user own mode
    def set_mode( self, 
                  mode ):
                      
        self.sock.send( "MODE " + self.nick + " " + mode + "\r\n" )

    ####################################################################
    # Send's a ping to a server or user 
    # (have to check messages for the answer)
    def ping( self,
              to ):
                  
        self.sock.send( "PING " + to + "\r\n" )

    ####################################################################
    # Collect's WHOIS/WHOWAS data
    def collect_who_data( self ):

        m = self.getmsg( True )
        data = { 'channels': [ ] }
        while ( m.type != RPL_ENDOFWHOWAS ) and \
              ( m.type != RPL_ENDOFWHOIS  ) and \
              ( m.type != ERR_NOSUCHNICK  ):
                               
            if ( m.type == RPL_WHOISUSER ):
                 d = m.msg.split( ":" )
                 data[ 'real_name' ] = d[ 1 ]
                 
                 d = d[ 0 ].split( " " )
                 
                 data[ 'nick' ] = d[ 0 ]
                 data[ 'user' ] = d[ 1 ]
                 data[ 'host' ] = d[ 2 ]
                
            elif ( m.type == RPL_WHOWASUSER ):
                 d = m.msg.split( ":" )
                 data[ 'real_name' ] = d[ 1 ]
                 
                 d = d[ 0 ].split( " " )
                 
                 data[ 'nick' ] = d[ 0 ]
                 data[ 'user' ] = d[ 1 ]
                 data[ 'host' ] = d[ 2 ]
                
            elif ( m.type == RPL_WHOISSERVER ): 
                 d = m.msg.split( ":" )
                 data[ 'server_info' ] = d[ 1 ]

                 d = d[ 0 ].split( " " )
                 
                 data[ 'server' ] = d[ 1 ]

            elif ( m.type == RPL_WHOISOPERATOR ): 
                 data[ 'isOp' ] = True
                
            elif ( m.type == RPL_WHOISIDLE ): 
                 d = m.msg.split( ":" )
                 data[ 'idle' ] = d[ 1 ]

                 d = d[ 0 ].split( " " )
                 
                 data[ 'time' ] = d[ 1 ]

            elif ( m.type == RPL_WHOISCHANNELS ): 
                 d = m.msg.split( ":" )
                 data[ 'channels' ] += d[ 1 ].strip().split( " " )

            else:
                self.msgBuff.append( m )
                
            m = self.getmsg( True )
            
        return data

    ####################################################################
    # Ask's for user information
    def send_whois( self,
                    user ):
                  
        self.sock.send( "WHOIS " + user + "\r\n")

    ####################################################################
    # Reads for user information
    def whois( self,
               user ):
                   
        self.send_whois( user )
        
        data = self.collect_who_data( )
           
        return data

    ####################################################################
    # Ask's for user (that no longer exists) information
    def send_whowas( self,
                     user ):
                    
        self.sock.send( "WHOWAS " + user + "\r\n" )
        
    ####################################################################
    # Reads for former user information
    def whowas( self, 
                user ):
        self.send_whowas( user )
        
        data = self.collect_who_data( )
        
        return data
    
    ####################################################################
    # Set's a channel topic
    def set_topic( self,
                   channel,
                   topic ):
                       
        self.sock.send( "TOPIC " + channel + " :" + topic + "\r\n" )

    ####################################################################
    # Retrieves a channel topic (has to check messages then)
    def retr_topic( self,
                    channel ):
                       
        self.sock.send( "TOPIC " + channel + "\r\n" )

    ####################################################################
    # Reads the current topic on a channel
    def get_topic( self,
                   channel ):

        self.retr_topic( channel )
        while ( True ):
            m = self.getmsg( True )
            if ( m.type == RPL_TOPIC ):
                return m.msg.split( ":" )[ -1 ]
                
            elif ( m.type == RPL_NOTOPIC ):
                return False
                
            self.msgBuff.append( m )
        

    ####################################################################
    # Retrieves a nick list
    def retr_names( self,
                    channel ):
                       
        self.sock.send( "NAMES " + channel + "\r\n" )

    ####################################################################
    # Reads the nick list
    def get_users( self,
                   channel ):
                       
        self.retr_names( channel )
        
        data = []
        m = self.getmsg( True )
        
        while ( m.type != RPL_ENDOFNAMES ):
            
            if ( m.type == RPL_NAMEREPLY ):
                data += m.msg.split( ":" )[ -1 ].split( " " )
                
            else:
                self.msgBuff.append( m )

            m = self.getmsg( True )

        return data

    ####################################################################
    # Retrieves a channel list
    def retr_channels( self ):
        
        self.sock.send( "LIST\r\n" )
            
    ####################################################################
    # Reads the channel list
    def get_channels( self ):
        self.retr_channels( )
        
        channels = []
        m = self.getmsg( True )
        
        while ( m.type != RPL_LISTEND ):
            if ( m.type == RPL_LISTSTART ):
                pass
            
            elif ( m.type == RPL_LIST ):
                
                if ( ":" in m.msg ):
                    i = m.msg.index( ":" )
                    topic = m.msg[ i + 1 : ]
                    d = m.msg[ : i ].strip( ).split( " " )
                    if ( len( d ) > 1 ):
                        channels.append( ( d[ 0 ], d[ 1 ], topic ) )
                 
            else:
                self.msgBuff.append( m )
                
            m = self.getmsg( True )
            
        return channels

    ####################################################################
    # Invites someone to a channel
    def invite( self,
                nick,
                channel ):
                    
        self.sock.send( "INVITE " + nick + " " + channel + "\r\n" )

    ####################################################################
    # Removes a user from a channel
    def kick( self,
              channel,
              nick,
              comment = None ):
                  
        if ( comment == None ):
            self.sock.send( "KICK " + channel + " " + nick + "\r\n" )
            
        else:
            self.sock.send( "KICK " + channel + " " + nick + " : " + 
                                            str( comment ) + "\r\n" )  

    ####################################################################
    # Quit the channel
    def quit_channel( self,
                      channel ):
                          
        self.sock.send( "PART " + channel + "\r\n" )

    ####################################################################
    # Quit's the server
    def quit( self,
              msg = "Client quit" ):
                  
        self.sock.send( "QUIT :" + str( msg ) + "\r\n" )
        self.sock.close( )

    ####################################################################
    # Joins a channel
    def join( self,
              channel,
              passwd = None ):
                  
        if ( channel[ 0 ] == "#" ):
            channel = channel[ 1 : ]

        if ( passwd == None ):
            self.sock.send( "JOIN #" + channel + "\r\n" )
        else:
            self.sock.send( "JOIN &" + channel + " " + passwd + "\r\n" )

    ####################################################################
    # Changes the nickname
    def change_nick( self,
                     nick ):
                         
        self.nick = nick
        self.sock.send( "NICK " + nick + "\r\n" )

    ####################################################################
    # Ask's for the MOTD
    def refresh_motd( self ):
        self.sock.send( "MOTD\r\n" )

    ####################################################################
    # Receives a message (and transparently answers to server ping's)
    def getmsg( self,
                fresh = False ):
                    
        if ( not fresh ) and ( len( self.msgBuff ) > 0 ):
            return self.msgBuff.pop( 0 )

        while ( True ):
            
            s = getline( self.sock )
            if ( len( s ) > 3 ):
                if ( s.lower()[ 0:4 ] == "ping" ):
                    self.pong( s )
                    continue
               
            m = irc_msg( s )

            if ( "version" in  m.ctcp_msg.lower() ):
                self.sendVer( m.by )
                continue

            elif ( m.type == RPL_MOTD ):
                self.motd += m.msg + "\n"
                continue

            elif ( m.type == RPL_MOTDSTART ):
                self.motd = ""
                continue

            return m

    ####################################################################
    # Sends a message ( msg ) to a receiver ( to ), which can 
    # be a channel or a user
    def sendmsg( self,
                 to,
                 msg ):
                     
        self.sock.send("PRIVMSG "+to+" :"+msg+"\r\n")

    ####################################################################
    # Same as sendmsg, but MUSTN'T be answered
    def notice( self,
                to,
                msg ):
                    
        self.sock.send( "NOTICE " + to + " :" + msg + "\r\n" )

    ####################################################################
    # Answers a ping
    def pong( self,
              ping ):
                  
        self.sock.send( "PONG" + ping[ 4: ] + "\r\n" )

    ####################################################################
    # Answers a version request
    def sendVer( self,
                 by ):
                     
        self.notice( by, chr( 1 ) + VERSION + chr( 1 ) )

    ####################################################################
    # Connecting to the server and login
    def connect_to_server( self,
                           passwd = None,
                           serverpasswd = None ):
                               
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        
        self.sock.connect(( self.server, self.port ))
        
        if ( serverpasswd != None ):
            
            self.sock.send( "PASS " + serverpasswd + "\r\n" )
            
        self.change_nick( self.nick )
        
        m = self.getmsg( )

        self.sock.send( "USER " + self.username + " " + self.username2 +
                    " " + self.server + ": " + self.fullname + "\r\n" )

        while ( m.type != RPL_ENDOFMOTD ):
            m = self.getmsg( )
                    
        if ( passwd != None ):
            self.sendmsg( "NickServ", "IDENTIFY " + passwd )

    ####################################################################
    # Object constructor
    def __init__( self,
                  nick,
                  server,
                  port = 6667,
                  username = "user",
                  username2 = "user",
                  fullname = "user Name",
                  serverpasswd = None,
                  passwd = None ):
                      
        self.nick = nick
        self.server = server
        self.port = port
        self.username = username
        self.username2 = username2
        self.fullname = fullname
        self.connect_to_server( passwd, serverpasswd )
