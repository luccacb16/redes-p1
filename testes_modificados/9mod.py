#!/usr/bin/env python3
import socket, base64, select, os, re, sys
def recvline(s):
    buf = b''
    while True:
        c = s.recv(1)
        buf += c
        if c == b'' or c == b'\n':
            return buf

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

print('[TEST9]')
print()

# Loga os clientes no servidor
nick1 = b'Abbiati'
s1.sendall(b'NICK %s\r\n' % nick1)
assert recvline(s1) == b':server 001 %s :Welcome\r\n' % nick1
assert recvline(s1) == b':server 422 %s :MOTD File is missing\r\n' % nick1
print('[OK] 1/16')
nick2 = b'Caio'
s2.sendall(b'NICK %s\r\n' % nick2)
assert recvline(s2) == b':server 001 %s :Welcome\r\n' % nick2
assert recvline(s2) == b':server 422 %s :MOTD File is missing\r\n' % nick2
print('[OK] 2/16')
nick3 = b'Luis'
s3.sendall(b'NICK %s\r\n' % nick3)
assert recvline(s3) == b':server 001 %s :Welcome\r\n' % nick3
assert recvline(s3) == b':server 422 %s :MOTD File is missing\r\n' % nick3
print('[OK] 3/16')

ch1 = b'#'+b'C1'
s1.sendall(b'JOIN %s\r\n' % ch1)
assert recvline(s1) == b':%s JOIN :%s\r\n' % (nick1, ch1)
print('[OK] 4/16')
assert recvline(s1).strip() == b':server 353 %s = %s :%s' % (nick1, ch1, nick1)
print('[OK] 5/16')
assert recvline(s1) == b':server 366 %s %s :End of /NAMES list.\r\n' % (nick1, ch1)
print('[OK] 6/16')

# Quando o cliente2 entrar, o nome do cliente1 também tem que estar na lista
s2.sendall(b'JOIN %s\r\n' % ch1)
assert recvline(s1) == b':%s JOIN :%s\r\n' % (nick2, ch1)
print('[OK] 7/16')
assert recvline(s2) == b':%s JOIN :%s\r\n' % (nick2, ch1)
print('[OK] 8/16')
assert recvline(s2).strip() == b':server 353 %s = %s :%s' % (nick2, ch1, b' '.join(sorted([nick1, nick2])))
print('[OK] 9/16')
assert recvline(s2) == b':server 366 %s %s :End of /NAMES list.\r\n' % (nick2, ch1)
print('[OK] 10/16')

# Quando o cliente3 entrar, os nomes do cliente1 e do cliente2 também têm que estar na lista
s3.sendall(b'JOIN %s\r\n' % ch1)
assert recvline(s1) == b':%s JOIN :%s\r\n' % (nick3, ch1)
print('[OK] 11/16')
assert recvline(s2) == b':%s JOIN :%s\r\n' % (nick3, ch1)
print('[OK] 12/16')
assert recvline(s3) == b':%s JOIN :%s\r\n' % (nick3, ch1)
print('[OK] 13/16')
assert recvline(s3).strip() == b':server 353 %s = %s :%s' % (nick3, ch1, b' '.join(sorted([nick1, nick2, nick3])))
print('[OK] 14/16')
assert recvline(s3) == b':server 366 %s %s :End of /NAMES list.\r\n' % (nick3, ch1)
print('[OK] 15/16')

r,_,_=select.select([s1,s2,s3],[],[],0.1)
assert r == []  # não deve receber nada além do que foi verificado até o momento
print('[OK] 16/16')

print()
print('FINALIZADO!')

s1.shutdown(socket.SHUT_WR)
s2.shutdown(socket.SHUT_WR)
s3.shutdown(socket.SHUT_WR)
