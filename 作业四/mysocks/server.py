import typing
import socket
import asyncio
import logging

from securesocket import SecureSocket, Address, Connection
from cipher import Cipher, VerifyFailed


class Server(SecureSocket):
    def __init__(self, loop: asyncio.AbstractEventLoop, pub_key_path: str, pri_key_path: str,
                 pub_key_path2: str, listenAddr: Address) -> None:
        super().__init__(loop, pub_key_path, pri_key_path, pub_key_path2)
        self.listenAddr = listenAddr
        aes_test = b'j(5\xf7!\xccv\xd8T\xf7\xa3\x9c\x13\xf9\x9e\xa0'
        self.cipher.aes_util.SetKey(aes_test)

    async def listen(self, didListen: typing.Callable = None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.setblocking(False)
            listener.bind(self.listenAddr)  # 服务器此处监听的应当是客户端发送的目标地址和端口
            listener.listen(socket.SOMAXCONN)

            print('Listen to %s:%d' % self.listenAddr)
            if didListen:
                didListen(listener.getsockname())

            while True:  # 处理方法和客户端一样
                connection, address = await self.loop.sock_accept(listener)
                print('Receive %s:%d', *address)
                asyncio.ensure_future(self.handleConn(connection))

    async def handleConn(self, connection: Connection):  # 握手完成之后要先用socks5协议来解析真正的访问目标
        """
        Handle the connection from LsLocal.
        """
        """
        SOCKS Protocol Version 5 https://www.ietf.org/rfc/rfc1928.txt
        The localConn connects to the dstServer, and sends a ver
        identifier/method selection message:
                    +----+----------+----------+
                    |VER | NMETHODS | METHODS  |
                    +----+----------+----------+
                    | 1  |    1     | 1 to 255 |
                    +----+----------+----------+
        The VER field is set to X'05' for this ver of the protocol.  The
        NMETHODS field contains the number of method identifier octets that
        appear in the METHODS field.
        """
        buf = await self.decodeRead(connection)  # 读一个socks5的request
        if not buf or buf[0] != 0x05:
            connection.close()
            return
        """
        The dstServer selects from one of the methods given in METHODS, and
        sends a METHOD selection message:
                    +----+--------+
                    |VER | METHOD |
                    +----+--------+
                    | 1  |   1    |
                    +----+--------+
        If the selected METHOD is X'FF', none of the methods listed by the
        client are acceptable, and the client MUST close the connection.

        The values currently defined for METHOD are:

                o  X'00' NO AUTHENTICATION REQUIRED
                o  X'01' GSSAPI
                o  X'02' USERNAME/PASSWORD
                o  X'03' to X'7F' IANA ASSIGNED
                o  X'80' to X'FE' RESERVED FOR PRIVATE METHODS
                o  X'FF' NO ACCEPTABLE METHODS

        The client and server then enter a method-specific sub-negotiation.
        """
        await self.encodeWrite(connection, bytearray((0x05, 0x00)))  # 写回去的是不需要认证
        """
        The SOCKS request is formed as follows:
            +----+-----+-------+------+----------+----------+
            |VER | CMD |  RSV  | ATYP | DST.ADDR | DST.PORT |
            +----+-----+-------+------+----------+----------+
            | 1  |  1  | X'00' |  1   | Variable |    2     |
            +----+-----+-------+------+----------+----------+
        Where:

          o  VER    protocol version: X'05'
          o  CMD
             o  CONNECT X'01'
             o  BIND X'02'
             o  UDP ASSOCIATE X'03'
          o  RSV    RESERVED
          o  ATYP   address type of following address
             o  IP V4 address: X'01'
             o  DOMAINNAME: X'03'
             o  IP V6 address: X'04'
          o  DST.ADDR       desired destination address
          o  DST.PORT desired destination port in network octet
             order
        """
        buf = await self.decodeRead(connection)  # 这次读到了真正的地址，开始建立与真正地址的连接
        if len(buf) < 7:
            connection.close()
            return

        if buf[1] != 0x01:
            connection.close()
            return

        dstIP = None

        dstPort = buf[-2:]
        dstPort = int(dstPort.hex(), 16)

        dstFamily = None

        if buf[3] == 0x01:
            # ipv4
            dstIP = socket.inet_ntop(socket.AF_INET, buf[4:4 + 4])
            dstAddress = Address(ip=dstIP, port=dstPort)
            print('get ipv4 request %s:%s', dstIP, dstPort)
            dstFamily = socket.AF_INET
        elif buf[3] == 0x03:
            # domain
            dstIP = buf[5:-2].decode()
            dstAddress = Address(ip=dstIP, port=dstPort)
            print('get domain request %s:%s', dstIP, dstPort)

        elif buf[3] == 0x04:
            # ipv6
            dstIP = socket.inet_ntop(socket.AF_INET6, buf[4:4 + 16])
            dstAddress = (dstIP, dstPort, 0, 0)
            dstFamily = socket.AF_INET6
            print('get ipv6 request %s:%s', dstIP, dstPort)

        else:
            print("something strange, close connection")
            connection.close()
            return

        dstServer = None
        if dstFamily:
            try:
                dstServer = socket.socket(
                    family=dstFamily, type=socket.SOCK_STREAM)
                dstServer.setblocking(False)
                await self.loop.sock_connect(dstServer, dstAddress)
            except OSError:
                if dstServer is not None:
                    dstServer.close()
                    dstServer = None
        else:
            host, port = dstAddress
            print('try to get ip of domain %s:%s', host, port)
            for res in await self.loop.getaddrinfo(host, port):
                dstFamily, socktype, proto, _, dstAddress = res
                print(f'get response dstFamily = {dstFamily}, socetType = {socktype} proto = {proto}')
                try:
                    dstServer = socket.socket(dstFamily, socktype, proto)
                    dstServer.setblocking(False)
                    await self.loop.sock_connect(dstServer, dstAddress)
                    break
                except OSError:
                    if dstServer is not None:
                        dstServer.close()
                        dstServer = None

        if dstFamily is None:
            return
        """
        The SOCKS request information is sent by the client as soon as it has
        established a connection to the SOCKS server, and completed the
        authentication negotiations.  The server evaluates the request, and
        returns a reply formed as follows:

                +----+-----+-------+------+----------+----------+
                |VER | REP |  RSV  | ATYP | BND.ADDR | BND.PORT |
                +----+-----+-------+------+----------+----------+
                | 1  |  1  | X'00' |  1   | Variable |    2     |
                +----+-----+-------+------+----------+----------+

            Where:

                o  VER    protocol version: X'05'
                o  REP    Reply field:
                    o  X'00' succeeded
                    o  X'01' general SOCKS server failure
                    o  X'02' connection not allowed by ruleset
                    o  X'03' Network unreachable
                    o  X'04' Host unreachable
                    o  X'05' Connection refused
                    o  X'06' TTL expired
                    o  X'07' Command not supported
                    o  X'08' Address type not supported
                    o  X'09' to X'FF' unassigned
                o  RSV    RESERVED
                o  ATYP   address type of following address
        """
        await self.encodeWrite(connection,
                               bytearray((0x05, 0x00, 0x00, 0x01, 0x00, 0x00,
                                          0x00, 0x00, 0x00, 0x00)))  # 告诉对方已经建立了？

        def cleanUp(task):
            """
            Close the socket when they succeeded or had an exception.
            """
            dstServer.close()
            connection.close()

        # 开启两个协程在两者之间传递信息
        conn2dst = asyncio.ensure_future(
            self.decodeCopy(dstServer, connection))
        dst2conn = asyncio.ensure_future(
            self.encodeCopy(connection, dstServer))
        task = asyncio.ensure_future(
            asyncio.gather(
                conn2dst, dst2conn, loop=self.loop, return_exceptions=True))
        task.add_done_callback(cleanUp)


def main():
    loop = asyncio.get_event_loop()
    listenAddr = Address('0.0.0.0', 8848)
    server = Server(loop, "rsa.pub2", "rsa.key2", "rsa.pub", listenAddr)

    def didListen(address):
        print('Listen to %s:%d\n' % address)

    asyncio.ensure_future(server.listen(didListen))
    loop.run_forever()


if __name__ == "__main__":
    main()
