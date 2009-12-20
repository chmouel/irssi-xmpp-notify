#!/usr/bin/python
# -*-*- encoding: utf-8 -*-*-
# Chmouel Boudjnah <chmouel@chmouel.com>
# TEST '#chmouel: chmouelb' 'chmouel: another xx'
import xmpp
import sys
import re
import os
import stat
import ConfigParser

class NotConnected(Exception):
    def __str__(self):
        return 'Could not connect to the Jabber Server'

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
    jid = config.get('auth', 'jid')
    password = config.get('auth', 'password')
    destination_jid = config.get('auth', 'destination_jid')
    mynickname = config.get('misc', 'mynickname')

    if not jid or not password or not destination_jid:
        return ret

    return {
        'jid' : jid,
        'password' : password,
        'destination_jid' : destination_jid,
        'mynickname' : mynickname
        }
    
class XMPPClient(object):
    def __init__(self, jid, password):
        self.resource = "BOT"
        self.password = password
        self.jid=xmpp.protocol.JID(jid)
        self.client=xmpp.Client(self.jid.getDomain(),debug=[])

    def connect(self):
        cnx = self.client.connect()
        if not cnx:
            raise NotConnected
        
        auth=self.client.auth(self.jid.getNode(),
                              self.password,
                              resource=self.resource)
        if not auth:
            raise NotConnected

        return True

    def send(self, tojid, text):
        id=self.client.send(xmpp.protocol.Message(tojid, text))


def main():
    config = parse_config(os.path.expanduser("~/.xmpp-notify.ini"))
    if not config:
        print "configs is not complete"
        sys.exit(1)
    
    x = XMPPClient(config['jid'], config['password'])
    x.connect()

    line = " ".join(sys.argv[1:])
    if not line:
        sys.exit(0)
    regexp=re.compile("^#(?P<channel>[^\s]+):\s*\s*(?P<sender>[^\s]*)\s*(?P<message>.*)$")
    line = line.strip()
    match = regexp.match(line)
    if not match: sys.exit(0)
    msg=match.group("message")
    if config['mynickname'] and msg.startswith("%s: " % (config['mynickname'])):
        msg = msg.replace("%s: " % (config['mynickname']), "")
    x.send(config['destination_jid'], "From %s on #%s: %s" % (match.group("sender"),
                               match.group("channel"),
                               msg))


if __name__ == '__main__':
    main()
