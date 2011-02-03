#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# PyIC example

from pyic import *

botName = "HelloBot"

server = "localhost"
channel = "#bot_testing"
saludo = "Hello"


irc = irc_client( botName, server )

# Esperar por que acabe de "presentarse" el servidor
while ( True ):
    msg = irc.getmsg( )
    if ( msg.type == RPL_ENDOFMOTD ): # Fin del mensaje del dia
        break
        
    elif (msg.type == ERR_NOMOTD): # No hay mensaje del dia
        break

print "Joining", channel
irc.join( channel ) # Se une al canal

print "Greeting :)}"
irc.notice( channel, saludo + " " + channel ) # Saluda al canal

# no usa irc.msg() para evitar que los bot's respondan

# Saluda a todos los que hay en el canal
while ( True ):
    msg = irc.getmsg( )

    if ( msg.type.upper( ) == "JOIN" ): # Alguien mas entro al canal
    
        if ( msg.by != botName ):

            print "'" + msg.by + "'", "has arrived"
            irc.notice( channel, saludo + " " + msg.by )
