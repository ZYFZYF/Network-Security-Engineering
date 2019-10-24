import socket
import time

import pandas as pd
from dns import resolver
from dnslib import DNSRecord


def clean_dns(domain, verbose=True):
    target_addr = ('8.8.8.8', 53)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_time = time.time()
    client.sendto(DNSRecord.question(domain).pack(), target_addr)
    client.settimeout(1)
    cnt = 0
    ret = ''
    if verbose:
        print('start to query {}'.format(domain))
    try:
        while True:
            cnt += 1
            response, _ = client.recvfrom(1024)
            recv_time = time.time()
            ret = [str(x.rdata) for x in DNSRecord.parse(response).rr if x.rtype == 1]
            if verbose:
                print(
                    '    {}th arrived, cost {}ms, response is {}'.format(cnt, int((recv_time - send_time) * 1000), ret))
    except socket.timeout as e:
        pass
    finally:
        client.close()
    if verbose:
        print('query end. result is {}'.format(ret))
    return ret


def dns_proxy(query):
    target_addr = ('8.8.8.8', 53)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(query, target_addr)
    client.settimeout(1)
    cnt = 0
    ret = ''
    try:
        while True:
            cnt += 1
            ret, _ = client.recvfrom(1024)
    except socket.timeout as e:
        pass
    finally:
        client.close()

    return ret


def direct_dns(domain):
    try:
        response = resolver.query(domain)
        return [y.address for x in response.response.answer for y in x.items if y.rdtype == 1]
    except resolver.NoAnswer as e:
        return []
    except resolver.NoNameservers as e:
        return []


def test():
    start_time = time.time()
    data = []
    lines = open('results.txt').readlines()
    for (ind, line) in enumerate(lines):
        domain = line.strip().split(' ')[0]
        reachable = line.strip().split(' ')[2]
        item = [domain, reachable, ', '.join(direct_dns(domain)), ', '.join(clean_dns(domain, verbose=False))]
        data.append(item)
        if ind % 10 == 0:
            print("process {}/{} and cost {}s".format(ind, len(lines), int(time.time() - start_time)))
    pd.DataFrame(data=data, columns=['域名', '可达性', '直接查询ip地址', '无污染ip地址']).to_csv('domains2ips.csv', index=False)


def serve():
    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(('127.0.0.1', 53))
        print('start to receive dns request...')
        query, addr = server.recvfrom(1024)
        print('receive a query for', DNSRecord.parse(query).questions)
        response = dns_proxy(query)
        print('get clean answer is', DNSRecord.parse(response).)
        server.sendto(response, addr)
        server.close()


if __name__ == '__main__':
    # test_domain = 'go.microsoft.com'
    # print(', '.join(clean_dns(test_domain)))
    # print(', '.join(direct_dns(test_domain)))
    # test()
    serve()
