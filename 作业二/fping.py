import os


def extract(num):
    open('domains_5000.txt', 'w').writelines(open('domains.txt', 'r').readlines()[:num])


def file_ping():
    os.system('fping --file=domains_5000.txt > results.txt')


if __name__ == '__main__':
    extract(5000)
    file_ping()
