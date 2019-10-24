import socket
import time

from dnslib import DNSRecord

forward_addr = ("8.8.8.8", 53)  # dns and port

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(0.5)
qname = "google.com"  # query
q = DNSRecord.question(qname)

t0 = time.time()
client.sendto(bytes(q.pack()), forward_addr)

i = 0

try:
    while True:
        i += 1
        data, _ = client.recvfrom(1024)
        t1 = time.time()
        d = DNSRecord.parse(data)
        print("response" + str(i), "in time=" + str(int((t1 - t0) * 1000)) + "ms:")
        for addr in d.rr:
            print("    " + str(addr.rdata))
except socket.timeout as e:
    print("exited...")
