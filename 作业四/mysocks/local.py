import typing
import socket
import asyncio
import logging

from securesocket import SecureSocket, Address

Connection = socket.socket
logger = logging.getLogger(__name__)

class local(SecureSocket):
    def __init__(self, loop: asyncio.AbstractEventLoop, listenAddr: Address, remoteAddr: Address) -> None:
        super().__init__(loop = loop)
        self.listenAddr = listenAddr
        self.remoteAddr = remoteAddr

    async def listen(self, didListen: typing.Callable = None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(self.listenAddr)
            listener.listen(socket.SOMAXCONN)
            listener.setblocking(False)

            logger.info('Listen to %s:%d' % self.listenAddr)
            if didListen:
                didListen(listener.getsockname())

            while True:
                connection, address = await self.loop.sock_accept(listener)
                logger.info('Receive %s:%d', *address)
                asyncio.ensure_future(self.handleConn(connection))

    async def handleConn(self, connection: Connection):
        remoteServer = await self.dialRemote()

        def cleanUp(task):
            remoteServer.close()
            connection.close()

        # TODO: finish here
        # local2remote = asyncio.ensure_future()

    async def dialRemote(self):
        try:
            remoteConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remoteConn.setblocking(False)
            await self.loop.sock_connect(remoteConn, self.remoteAddr)
        except Exception as err:
            raise ConnectionError('链接到远程服务器 %s:%d 失败:\n%r' % (*self.remoteAddr,
                                                              err))
        return remoteConn

