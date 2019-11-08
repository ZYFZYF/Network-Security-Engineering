from scapy.layers.inet import *
from scapy.sendrecv import send

p0 = 'GET /tibe'
p1 = 'talk.php HTTP/1.1\r\nHost: lab3.jinzihao.me\r\nConnection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3\r\nAccept-Encoding: gzip, deflate\r\nAccept-Language: zh-CN,zh;q=0.9\r\n\r\n'

sp = random.randint(1024, 65535)
ip = IP(dst='188.166.199.77')
SYN = TCP(sport=sp, dport=80, flags='S', seq=10)
SYNACK = sr1(ip / SYN)
my_ack = SYNACK.seq + 1
next_seq = SYN.seq + 1
ACK = TCP(ack=my_ack, seq=next_seq, sport=sp, dport=80, flags='A')
send(ip / ACK)
time.sleep(1)
RST = TCP(ack=my_ack, seq=next_seq, sport=sp, dport=80, flags='RA')
send(ip / RST)
time.sleep(2)
SYN = TCP(sport=sp, dport=80, flags='S', seq=11)
SYNACK = sr1(ip / SYN)
my_ack = SYNACK.seq + 1
next_seq = SYN.seq + 1
ACK = TCP(ack=my_ack, seq=next_seq, sport=sp, dport=80, flags='A')
send(ip / ACK)
PUSH = TCP(ack=my_ack, seq=next_seq, sport=sp, dport=80, flags='PA')
send(ip / PUSH / p0)
next_seq = ACK.seq + len(p0)
time.sleep(2)
PUSH = TCP(ack=my_ack, seq=next_seq, sport=sp, dport=80, flags='PA')
send(ip / PUSH / p1)
next_seq = ACK.seq + len(p1)
time.sleep(2)
RST = TCP(ack=my_ack, seq=next_seq, sport=sp, dport=80, flags='RA')
send(ip / RST)
