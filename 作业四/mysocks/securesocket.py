import socket
import asyncio
import typing
from collections import namedtuple

Address = namedtuple('Address', 'ip port')
Connection = socket.socket

class SecureSocket(object):
    """
    A socket for receiving and sending data
    """
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop or asyncio.get_event_loop()