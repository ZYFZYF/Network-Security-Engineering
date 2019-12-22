import typing
import socket
import asyncio
import logging

from securesocket import SecureSocket, Address, Connection
from cipher import Cipher, VerifyFailed

logger = logging.getLogger(__name__)

class Local(SecureSocket):
    def __init__(self, loop: asyncio.AbstractEventLoop, pub_key_path: str, pri_key_path: str, 
                 pub_key_path2: str, listenAddr: Address, remoteAddr: Address) -> None:
        super().__init__(loop, pub_key_path, pri_key_path, pub_key_path2)
        self.listenAddr = listenAddr
        self.remoteAddr = remoteAddr
        aes_test = b'j(5\xf7!\xccv\xd8T\xf7\xa3\x9c\x13\xf9\x9e\xa0'
        self.cipher.aes_util.SetKey(aes_test)

    async def listen(self, didListen: typing.Callable = None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:  # 设置监听网络TCP请求
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 打开地址重用
            listener.bind(self.listenAddr)  # 将socket与监听地址绑定，所有发送到这个地址的都会被我们的local读取和使用
            listener.listen(socket.SOMAXCONN)  # 进行完 tcp 三次握手之后，相应的连接会放到服务器相应 socket 的队列，此处设置的就是队列大小（本质上相当于没设）
            listener.setblocking(False)

            logger.info('Listen to %s:%d' % self.listenAddr)
            if didListen:
                didListen(listener.getsockname())

            while True:
                connection, address = await self.loop.sock_accept(listener)  # 从握手完成的里面选取一个，开始与墙外服务器建立通信
                logger.info('Receive %s:%d', *address)
                asyncio.ensure_future(self.handleConn(connection))

    async def handleConn(self, connection: Connection):  # 通信建立之后就开始用两个协程在两边传东西
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

    async def dialRemote(self):  # 创建到墙外服务器的连接
        try:
            remote_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_connection.setblocking(False)
            await self.loop.sock_connect(remote_connection, self.remoteAddr)
        except Exception as err:
            raise ConnectionError('链接到远程服务器 %s:%d 失败:\n%r' % (*self.remoteAddr,
                                                              err))
        return remote_connection

def main():
    loop = asyncio.get_event_loop()
    listenAddr = Address('127.0.0.1', 1080)
    #TODO: fill the addr
    server_ip = ""
    remoteAddr = Address(server_ip, 8388)
    local = Local(loop, "rsa.pub", "rsa.key", "rsa.pub2", listenAddr, remoteAddr)

    def didListen(address):
        print('Listen to %s:%d\n' % address)

    asyncio.ensure_future(local.listen(didListen))
    loop.run_forever()

if __name__ == "__main__":
    main()
