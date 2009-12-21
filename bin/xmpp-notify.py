#!/usr/bin/python
# -*- coding: utf-8 -*-
# Chmouel Boudjnah <chmouel@chmouel.com>
# TEST '#chmouel: chmouelb' 'chmouel: another xx'
# TEST2 'Private message from chmouelb -hey dude'
import stat
import ConfigParser
import os
import sys
import re

from twisted.internet import reactor
from twisted.names.srvconnect import SRVConnector
from twisted.words.xish import domish
from twisted.words.protocols.jabber import xmlstream, client, jid


class XMPPClientConnector(SRVConnector):
    def __init__(self, reactor, domain, factory):
        SRVConnector.__init__(self, reactor, 'xmpp-client', domain, factory)

    def pickServer(self):
        host, port = SRVConnector.pickServer(self)
        if not self.servers and not self.orderedServers:
            port = 5222
        return host, port

class SendMessage(object):
    def __init__(self, client_jid, secret, to_jid, message, check_online=True):
        self.client_jid = client_jid
        self.to_jid = to_jid
        self.message = message
        self.check_online = check_online
        
        f = client.XMPPClientFactory(client_jid, secret)
        f.addBootstrap(xmlstream.STREAM_CONNECTED_EVENT, self.connected)
        f.addBootstrap(xmlstream.STREAM_END_EVENT, self.disconnected)
        f.addBootstrap(xmlstream.STREAM_AUTHD_EVENT, self.authenticated)
        f.addBootstrap(xmlstream.INIT_FAILED_EVENT, self.init_failed)
        connector = XMPPClientConnector(reactor, client_jid.host, f)
        connector.connect()

    def connected(self, xs):
        self.xmlstream = xs
        self.xmlstream.addObserver('/presence', self.presence)

    def presence(self, elem):
        if not self.check_online:
            self.send_the_message()
            return
        
        availability = elem.getAttribute("type")
        if availability and availability == 'unavailable':
            return
        fromjid,ressource = elem.getAttribute("from").split("/")
        if fromjid == self.to_jid:
            self.send_the_message()

    def send_the_message(self):
	message = domish.Element(('jabber:client','message'))
	message["to"] = self.to_jid.full()
	message["from"] = self.client_jid.full()
	message["type"] = "chat"
	message.addElement("body", "jabber:client", self.message)
	self.xmlstream.send(message)
        
    def disconnected(self, xs):
        reactor.stop()

    def authenticated(self, xs):
        presence = domish.Element((None, 'presence'))
        xs.send(presence)
        reactor.callLater(5, xs.sendFooter)

    def init_failed(self, failure):
        print "Authentication failed."
        self.xmlstream.sendFooter()

def parse_config(config_file):
    if not os.path.exists(config_file):
        config = ConfigParser.ConfigParser()
        config.add_section("misc")
        config.set("misc", "mynickname", "")
        config.add_section("auth")
        config.set("auth", "jid", "")
        config.set("auth", "password", "")
        config.set("auth", "destination_jid", "")
        config.write(open(config_file, 'w'))
        return

    filemode = stat.S_IMODE(os.stat(config_file).st_mode) & 0777
    if filemode != 384:
        os.chmod(config_file, 0600)    

    ret={}
    config = ConfigParser.ConfigParser()
    cfh = config.read(config_file)
    if not cfh:
        return ret
    thejid = config.get('auth', 'jid')
    password = config.get('auth', 'password')
    destination_jid = config.get('auth', 'destination_jid')
    mynickname = config.get('misc', 'mynickname')

    if not thejid or not password or not destination_jid:
        return ret

    return {
        'jid' : jid.JID(thejid),
        'password' : password,
        'destination_jid' : jid.JID(destination_jid),
        'mynickname' : mynickname
        }
        
def main():
    config = parse_config(os.path.expanduser("~/.xmpp-notify.ini"))
    if not config:
        print "configs is not complete"
        sys.exit(1)
    
    line = " ".join(sys.argv[1:])
    if not line:
        sys.exit(0)

    line = line.strip()
    regexp=re.compile("^#(?P<channel>[^\s]+):\s*\s*(?P<sender>[^\s]*)\s*(?P<message>.*)$")
    match = regexp.match(line)

    if line.startswith("Private message from "):
        msg = line.replace("Private message from ", "")
    elif match:
        msg=match.group("message")
        if config['mynickname'] and msg.startswith("%s: " % (config['mynickname'])):
            msg = msg.replace("%s: " % (config['mynickname']), "")
    else:
        print "No match on: %s" % line
        sys.exit(0)

    c = SendMessage(config['jid'], config['password'],
                    config['destination_jid'],
                    msg,
                    check_online=False)
    reactor.run()

if __name__ == '__main__':
    main()

