#!/usr/bin/env python
# Testing bot for Kontalk XMPP


from twisted.internet import reactor
from twisted.words.xish import domish

import sys, time, demjson

from kontalk.xmppserver import util, xmlstream2
import bot_utils


class Handler:
    def __init__(self, config):
        self.config = config
        self._stats = {}

    def print_stats(self):
        print
        print "%-30s %5s" % ('key', 'value')
        print '-'*36
        for k, v in self._stats.iteritems():
            print "%-30s %5d" % (k, v)

    def authenticated(self):
        """Server just authenticated us."""
        pass

    def ready(self):
        """Client just sent initial presence."""

        print "Now available."

        for action in self.config['actions']:
            name = action['name']
            del action['name']
            try:
                timeout = action['timeout']
                del action['timeout']
            except:
                timeout = -1
            try:
                fn = getattr(self, name)
                if timeout >= 0:
                    reactor.callLater(timeout, fn, **action)
                else:
                    fn(**action)
            except:
                import traceback
                traceback.print_exc()

    def message(self, stanza):
        """Message stanza received."""

        #print "message from %s" % (stanza['from'], )
        if type(self.config['behavior']['ack']) == int:
            delay = self.config['behavior']['ack']
            if stanza.getAttribute('type') == 'chat':
                if stanza.request and stanza.request.uri == 'urn:xmpp:server-receipts':
                    self.stats('messages:incoming')

                    def sendReceipt(stanza):
                        receipt = domish.Element((None, 'message'))
                        receipt['type'] = 'chat'
                        receipt['to'] = stanza['from']
                        child = receipt.addElement(('urn:xmpp:server-receipts', 'received'))
                        child['id'] = stanza.request['id']
                        self.client.send(receipt)
                        self.stats('messages:confirmed')
                    reactor.callLater(delay, sendReceipt, stanza)

                # received ack
                elif stanza.received and stanza.received.uri == 'urn:xmpp:server-receipts':
                    ack = domish.Element((None, 'message'))
                    ack['to'] = stanza['from']
                    ack['type'] = 'chat'
                    child = ack.addElement(('urn:xmpp:server-receipts', 'ack'))
                    child['id'] = stanza['id']
                    self.client.send(ack)
                    self.stats('messages:delivered')

                elif stanza.sent and stanza.sent.uri == 'urn:xmpp:server-receipts':
                    self.stats('messages:sent')

    def presence(self, stanza):
        """Presence stanza received."""
        pass

    def iq(self, stanza):
        """IQ stanza received."""
        pass

    def stats(self, key, inc=1):
        if not key in self._stats:
            self._stats[key] = inc
        else:
            self._stats[key] += inc

    def sendTextMessage(self, peer, content, request=False):
        """Sends a text message with an optional receipt request."""

        jid = self.client.xmlstream.authenticator.jid
        message = domish.Element((None, 'message'))
        message['id'] = 'kontalk' + util.rand_str(8, util.CHARSBOX_AZN_LOWERCASE)
        message['type'] = 'chat'
        if peer:
            message['to'] = peer
        else:
            message['to'] = jid.userhost()
        message.addElement((None, 'body'), content=content)
        if request:
            message.addElement(('urn:xmpp:server-receipts', 'request'))
        self.client.send(message)
        self.stats('messages:outgoing')
        if request:
            self.stats('messages:pending')
        else:
            self.stats('messages:sent')

    def messageLoop(self, peer, contentFmt='%d', request=False, delay=0, count=0):
        self._loopCount = 0
        self._loopAckCount = 0
        self._loopStart = time.time()
        def _stats(stanza):
            self._loopAckCount += 1
            if self._loopAckCount >= count:
                # remove observer
                self.client.xmlstream.removeObserver("/message/received", _stats)
                diff = time.time() - self._loopStart
                self.stats('messages:loopsPerSecond', self._loopAckCount / diff)
                print "%d loops in %.2f seconds" % (self._loopAckCount, diff)
                print "messages: %.2f loops/second" % (self._loopAckCount / diff, )

        def _count():
            self._loopCount += 1
            if self._loopCount < count:
                reactor.callLater(delay, _count)
            self.sendTextMessage(peer, contentFmt % (self._loopCount, ), request)

        # WARNING this is very specific to this method
        self.client.xmlstream.addObserver("/message/received", _stats)
        reactor.callLater(delay, _count)

    def bounceIncrement(self, peer, request=False, begin=False, delay=0, count=0):
        self._bounceIncStart = time.time()
        self._bounceIncAvg = 0
        self._bounceCount = 0
        def _count(stanza):
            try:
                i = int(str(stanza.body))
                if count > 0 and i < count:
                    self._bounceIncAvg += (time.time() - self._bounceIncStart)
                    self._bounceCount += 1
                    reactor.callLater(delay, self.sendTextMessage, peer, str(i+1), request)
                else:
                    self.stats('messages:bouncesPerSecond', self._bounceIncAvg / self._bounceCount)
            except:
                pass
        self.client.xmlstream.addObserver("/message", _count)

        if begin:
            self.sendTextMessage(peer, "1", request)

    def quit(self):
        self.client.xmlstream.sendFooter()


# load configuration
fp = open(sys.argv[1], 'r')
config = demjson.decode(fp.read(), allow_comments=True)
fp.close()

handler = Handler(config)
c = bot_utils.Client(config, handler)

reactor.run()

# reactor quit, print statistics
handler.print_stats()