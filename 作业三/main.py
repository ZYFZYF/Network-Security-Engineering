from scapy.layers.inet import *
from scapy.sendrecv import send

if __name__ == '__main__':
    ip = IP(dst='188.166.199.77')
    payloads = ['GET /ti', 'be', 'ta', 'lk',
                '.php ',
                'HTTP/1.1\r\nHost: lab3.jinzihao.me',
                '\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Macintosh; ',
                'Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, ',
                'like Gecko) Chrome/78.0.3904.87 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3\r\nAccept-Encoding: gzip, deflate\r\nAccept-Language: zh-CN,zh;q=0.9\r\n\r\n']
    port = RandNum(1024, 65535)
    SYN = ip / TCP(sport=port, dport=80, flags='S', seq=42)
    ACK = sr1(SYN)
    ack_num = ACK.seq + 1
    send_length = 0
    for p in payloads:
        fragment = ip / TCP(sport=ACK.dport, dport=80, flags='A', seq=ACK.ack + send_length, ack=ack_num) / p
        send(fragment)
        send_length += len(p)
        time.sleep(3)
