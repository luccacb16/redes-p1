#!/usr/bin/env python3
import socket, base64, select, os, re, sys
def recvline(s):
    buf = b''
    while True:
        c = s.recv(1)
        buf += c
        if c == b'' or c == b'\n':
            return buf

def recvcmd(s, cmd):
    while True:
        line = recvline(s)
        arr = line.split()
        if len(arr) >= 2 and arr[0].startswith(b':') and arr[1] == cmd:
            return line

def randletters(n):
    res = b''
    while len(res) < n: 
        res += re.sub(br'[^a-z]', b'', os.urandom(512))
    return res[:n]

s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.connect(('localhost', 6667))
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.connect(('localhost', 6667))
s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s3.connect(('localhost', 6667))

print('[TEST8]')
print()

# Loga os clientes no servidor
nick1 = b'Abbi'
s1.sendall(b'NICK %s\r\n' % nick1)
assert recvline(s1) == b':server 001 %s :Welcome\r\n' % nick1
assert recvline(s1) == b':server 422 %s :MOTD File is missing\r\n' % nick1
print('[OK] 1/12')
nick2 = b'Caio'
s2.sendall(b'NICK %s\r\n' % nick2)
assert recvline(s2) == b':server 001 %s :Welcome\r\n' % nick2
assert recvline(s2) == b':server 422 %s :MOTD File is missing\r\n' % nick2
print('[OK] 2/12')
nick3 = b'Luis'
s3.sendall(b'NICK %s\r\n' % nick3)
assert recvline(s3) == b':server 001 %s :Welcome\r\n' % nick3
assert recvline(s3) == b':server 422 %s :MOTD File is missing\r\n' % nick3
print('[OK] 3/12')

# Os clientes entram todos no mesmo canal
ch1 = b'#'+b'C1'
s1.sendall(b'JOIN %s\r\n' % ch1)
assert recvcmd(s1, b'JOIN') == b':%s JOIN :%s\r\n' % (nick1, ch1)
print('[OK] 4/12')
s2.sendall(b'JOIN %s\r\n' % ch1)
assert recvcmd(s2, b'JOIN') == b':%s JOIN :%s\r\n' % (nick2, ch1)
print('[OK] 5/12')
s3.sendall(b'JOIN %s\r\n' % ch1)
assert recvcmd(s3, b'JOIN') == b':%s JOIN :%s\r\n' % (nick3, ch1)
print('[OK] 6/12')

# Quando os clientes saem, os outros devem ser notificados
s2.shutdown(socket.SHUT_WR)
assert recvcmd(s1, b'QUIT').startswith(b':%s QUIT' % nick2)
print('[OK] 7/12')
assert recvcmd(s3, b'QUIT').startswith(b':%s QUIT' % nick2)
print('[OK] 8/12')
s3.shutdown(socket.SHUT_WR)
assert recvcmd(s1, b'QUIT').startswith(b':%s QUIT' % nick3)
print('[OK] 9/12')

# O primeiro cliente deve conseguir reutilizar os nicks liberados pela saída dos outros
s1.sendall(b'NICK %s\r\n' % nick2)
assert recvline(s1) == b':%s NICK %s\r\n' % (nick1, nick2)
print('[OK] 10/12')
s1.sendall(b'NICK %s\r\n' % nick3)
assert recvline(s1) == b':%s NICK %s\r\n' % (nick2, nick3)
print('[OK] 11/12')

r,_,_=select.select([s1],[],[],0.1)
assert r == []  # não deve receber nada além do que foi verificado até o momento
print('[OK] 12/12')

print()
print('FINALIZADO!')

s1.shutdown(socket.SHUT_WR)
