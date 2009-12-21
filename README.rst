============================
 XMPP Notfication for IRSSI
============================

:Homepage:  http://blog.chmouel.com/2009/12/20/xmpp-notification-for-irssi-running-in-a-screen-on-a-remote-host/
:Credits:   Copyright 2009--2010 Chmouel Boudjnah <chmouel@chmouel.com>
:Licence:   BSD

Installation
============

You need to have python-twisted-words installed you can install from source from here

    http://twistedmatrix.com/trac/wiki/Downloads

or on Debian or Ubuntu installed directly from the apt repositories :

    aptitude install python-twisted-words

Place the file irssi-script/xmpp-notify.pl in your
~/.irssi/scripts/autorun/ directory and place the file
bin/xmpp-notify.py in /usr/local/bin/ (or somewhere else as long you
adjust the irssi variable xmpp-notify.py to the proper path).

Config
======

- On the first run the xmpp-notify.py script will create a file in
  your home directory called ~/.xmpp-notify.ini containing::

    [auth]
    jid = your_jabber_id@jabber-domain.com
    password = your_password
    destination_jid = the_destination_jid@jabber-domain.com

    [misc]
    mynickname = mynick

- Fill them with the proper information and make sure the jid and
  destination_jid can talk to each others with a desktop client.
