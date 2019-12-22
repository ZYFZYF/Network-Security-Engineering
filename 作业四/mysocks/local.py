import typing
import socket
import asyncio
import logging

from securesocket import SecureSocket, Address, Connection
from cipher import Cipher, VerifyFailed

logger = logging.getLogger(__name__)

class Local(SecureSocket):
    def __init__(self, loop: asyncio.AbstractEventLoop, pub_key_path: str, pri_key_path: str, pub_key_path2: str, listenAddr: Address, remoteAddr: Address) -> None:
        super().__init__(loop, pub_key_path, pri_key_path, pub_key_path2)
        self.listenAddr = listenAddr
        self.remoteAddr = remoteAddr
        aes_test = b'j(5\xf7!\xccv\xd8T\xf7\xa3\x9c\x13\xf9\x9e\xa0'
        self.cipher.aes_util.SetKey(aes_test)

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

        local2remote = asyncio.ensure_future(
            self.decodeCopy(connection, remoteServer))
        remote2local = asyncio.ensure_future(
            self.encodeCopy(remoteServer, connection))
        task = asyncio.ensure_future(
            asyncio.gather(
                local2remote,
                remote2local,
                loop=self.loop,
                return_exceptions=True))
        task.add_done_callback(cleanUp)

    async def dialRemote(self):
        try:
            remoteConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remoteConn.setblocking(False)
            await self.loop.sock_connect(remoteConn, self.remoteAddr)
        except Exception as err:
            raise ConnectionError('链接到远程服务器 %s:%d 失败:\n%r' % (*self.remoteAddr,
                                                              err))
        return remoteConn

def main():
    loop = asyncio.get_event_loop()
    listenAddr = Address('127.0.0.1', 1080)
    remoteAddr = None
    local = Local(loop, "rsa.pub", "rsa.key", "rsa.pub2", listenAddr, remoteAddr)

    def didListen(address):
        print('Listen to %s:%d\n' % address)

    asyncio.ensure_future(local.listen(didListen))
    loop.run_forever()

if __name__ == "__main__":
    main()