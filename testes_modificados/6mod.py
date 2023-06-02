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

print('[TEST6]')
print()

# Loga os clientes no servidor
nick1 = b'Abbiamigo'
s1.sendall(b'NICK %s\r\n' % nick1)
assert recvline(s1) == b':server 001 %s :Welcome\r\n' % nick1
assert recvline(s1) == b':server 422 %s :MOTD File is missing\r\n' % nick1
print('[OK] 1/14')
nick2 = b'Obatake'
s2.sendall(b'NICK %s\r\n' % nick2)
assert recvline(s2) == b':server 001 %s :Welcome\r\n' % nick2
assert recvline(s2) == b':server 422 %s :MOTD File is missing\r\n' % nick2
print('[OK] 2/14')
nick3 = b'Luibas'
s3.sendall(b'NICK %s\r\n' % nick3)
assert recvline(s3) == b':server 001 %s :Welcome\r\n' % nick3
assert recvline(s3) == b':server 422 %s :MOTD File is missing\r\n' % nick3
print('[OK] 3/14')

# cliente1 e cliente2 entram em 2 canais, cliente3 entra em apenas um
ch1 = b'#'+b'canalUM'
ch2 = b'#'+b'canalDOIS'
s1.sendall(b'JOIN %s\r\n' % ch1)
assert recvcmd(s1, b'JOIN') == b':%s JOIN :%s\r\n' % (nick1, ch1)
print('[OK] 4/14')
s1.sendall(b'JOIN %s\r\n' % ch2)
assert recvcmd(s1, b'JOIN') == b':%s JOIN :%s\r\n' % (nick1, ch2)
print('[OK] 5/14')
s2.sendall(b'JOIN %s\r\n' % ch1)
assert recvcmd(s2, b'JOIN') == b':%s JOIN :%s\r\n' % (nick2, ch1)
print('[OK] 6/14')
s2.sendall(b'JOIN %s\r\n' % ch2)
assert recvcmd(s2, b'JOIN') == b':%s JOIN :%s\r\n' % (nick2, ch2)
print('[OK] 7/14')
s3.sendall(b'JOIN %s\r\n' % ch1)
assert recvcmd(s3, b'JOIN') == b':%s JOIN :%s\r\n' % (nick3, ch1)
print('[OK] 8/14')

# Cada cliente manda uma mensagem

msg1 = b'MENSAGEM 1'
s1.sendall(b'PRIVMSG %s :%s\r\n' % (ch1, msg1))
assert recvcmd(s2, b'PRIVMSG') == b':%s PRIVMSG %s :%s\r\n' % (nick1, ch1, msg1)
print('[OK] 9/14')
assert recvcmd(s3, b'PRIVMSG') == b':%s PRIVMSG %s :%s\r\n' % (nick1, ch1, msg1)
print('[OK] 10/14')

msg2 = b'MENSAGEM 2'
s2.sendall(b'PRIVMSG %s :%s\r\n' % (ch2, msg2))
assert recvcmd(s1, b'PRIVMSG') == b':%s PRIVMSG %s :%s\r\n' % (nick2, ch2, msg2)
print('[OK] 11/14')

msg3 = b'MENSAGEM 3'
s3.sendall(b'PRIVMSG %s :%s\r\n' % (ch1.upper(), msg3))
assert recvcmd(s1, b'PRIVMSG') in {
        b':%s PRIVMSG %s :%s\r\n' % (nick3, ch1, msg3),
        b':%s PRIVMSG %s :%s\r\n' % (nick3, ch1.upper(), msg3)
    }
print('[OK] 12/14')
assert recvcmd(s2, b'PRIVMSG') in {
        b':%s PRIVMSG %s :%s\r\n' % (nick3, ch1, msg3),
        b':%s PRIVMSG %s :%s\r\n' % (nick3, ch1.upper(), msg3)
    }
print('[OK] 13/14')

r,_,_=select.select([s1,s2,s3],[],[],0.1)
assert r == []  # não é pra receber mais nada depois do que foi verificado
print('[OK] 14/14')

print()
print('FINALIZADO!')

s1.shutdown(socket.SHUT_WR)
s2.shutdown(socket.SHUT_WR)
s3.shutdown(socket.SHUT_WR)
