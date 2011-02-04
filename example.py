#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# PyIC example

from pyic import *

botName = "HelloBot" # NickName

server = "irc.freenode.net" # IRC server
channel = "#bot_testing" # IRC channel
greet = "Hello"
topic = "PyIC testing"

print "Connecting..."

irc = irc_client( botName, server ) # Connect

print "Message of the day:"
print irc.get_motd( )

print "Reading channel list"
print len( irc.get_channels( ) ), "channels"


print "Joining", channel
irc.join( channel ) # Joins the channel

irc.notice( channel, greet + " " + channel ) # talks to the channel
# use notice in order to avoid automatic responses

# Reads the user list
for usr in irc.get_users( channel ):
    
    
    print '"' + usr + '" data'
    
    print irc.whois( clean_usr( usr ) ) # Shows the user data
    
    irc.notice( channel, greet + " " + usr ) # talks to the user


print "Setting channel topic"
irc.set_topic( channel, topic )

print "Topic:", irc.get_topic( channel )

print "Waiting for users..."
# Greets who enters the channel
while ( True ):
    
    msg = irc.getmsg( )
    
    if ( msg.type.upper( ) == "JOIN" ): # Someone entered the channel
    
        if ( msg.by != botName ):

            print "'" + msg.by + "'", "has arrived"
            irc.notice( channel, greet + " " + msg.by )
            print irc.whois( msg.by )
