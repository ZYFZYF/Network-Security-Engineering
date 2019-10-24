import requests

if __name__ == "__main__":
    domains = open('gfwlist_domain.txt', 'r').readlines()
    result = []

    for (ind, domain) in enumerate(domains):
        try:
            res = requests.get(url="http://{}".format(domain), timeout=5)
            if res.status_code == 200:
                result.append({domain, 1})
                print('{} can access'.format(domain))
        except Exception as e:
            pass
            # print(e)
        # print(ind, domain)
        if ind % 20 == 0:
            print("process {}/{}".format(ind + 1, len(domains)))

    t = open('wwww.txt', 'w')
    t.writelines()
