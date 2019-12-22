import socket
import asyncio
import typing
import logging
from collections import namedtuple
from cipher import Cipher, VerifyFailed

BUFFER_SIZE = 1024
Address = namedtuple('Address', 'ip port')
Connection = socket.socket

logger = logging.getLogger(__name__)


class SecureSocket(object):

    def __init__(self, loop: asyncio.AbstractEventLoop, pub_key_path: str, pri_key_path: str, pub_key_path2: str):
        self.loop = loop or asyncio.get_event_loop()
        self.cipher = Cipher(pub_key_path, pri_key_path, pub_key_path2)

    async def decodeRead(self, conn: Connection):
        data = await self.loop.sock_recv(conn, BUFFER_SIZE)
        bs = bytes(data)
        bs = self.cipher.decode(bs)
        print('%s:%d decodeRead %r', *conn.getsockname(), bs)
        return bs

    async def encodeWrite(self, conn: Connection, bs: bytes):
        print('%s:%d encodeWrite %s', *conn.getsockname(), bytes(bs).decode('utf-8'))
        # bs = bs.copy()
        bs = self.cipher.encode(bs)
        await self.loop.sock_sendall(conn, bs)

    async def encodeCopy(self, dst: Connection, src: Connection):
        """
        It encodes the data flow from the src and sends to dst.
        """
        print('encodeCopy %s:%d => %s:%d',
              *src.getsockname(), *dst.getsockname())

        while True:
            data = await self.loop.sock_recv(src, BUFFER_SIZE)
            if not data:
                break

            await self.encodeWrite(dst, bytes(data))

    async def decodeCopy(self, dst: Connection, src: Connection):
        """
        It decodes the data flow from the src and sends to dst.
        """
        print('decodeCopy %s:%d => %s:%d',
              *src.getsockname(), *dst.getsockname())
        while True:
            bs = await self.decodeRead(src)
            if not bs:
                break

            await self.loop.sock_sendall(dst, bs)
