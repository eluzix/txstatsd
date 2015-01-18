"""
The MIT License (MIT)

Copyright (c) 2015 eluzix

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import random

from twisted.internet import reactor

from twisted.internet.protocol import DatagramProtocol
from twisted.python import log


__author__ = 'eluzix'


class StatsdClient(DatagramProtocol):
    """
    Shameless copy of statsd client implemented for twisted.
    """

    def __init__(self):
        self.host_tuple = ('127.0.0.1', 8125)

    def timing(self, stat, delta, rate=1):
        """Send new timing information. `delta` is in milliseconds."""
        self._send_stat(stat, '%d|ms' % delta, rate)

    def incr(self, stat, count=1, rate=1):
        """Increment a stat by `count`."""
        self._send_stat(stat, '%s|c' % count, rate)

    def decr(self, stat, count=1, rate=1):
        """Decrement a stat by `count`."""
        self.incr(stat, -count, rate)

    def gauge(self, stat, value, rate=1, delta=False):
        """Set a gauge value."""
        if value < 0 and not delta:
            if rate < 1:
                if random.random() > rate:
                    return
            self._send_stat(stat, '0|g', 1)
            self._send_stat(stat, '%s|g' % value, 1)
        else:
            prefix = '+' if delta and value >= 0 else ''
            self._send_stat(stat, '%s%s|g' % (prefix, value), rate)

    def set(self, stat, value, rate=1):
        """Set a set value."""
        self._send_stat(stat, '%s|s' % value, rate)

    def _prepare(self, stat, value, rate):
        if rate < 1:
            if random.random() > rate:
                return
            value = '%s|@%s' % (value, rate)

        return '%s:%s' % (stat, value)

    def _send_stat(self, stat, value, rate):
        try:
            self.transport.write(self._prepare(stat, value, rate), self.host_tuple)
        except Exception as e:
            log.err(e, 'error sending stats to socket')


statsd = StatsdClient()
reactor.listenUDP(0, statsd)
