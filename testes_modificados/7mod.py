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

print('[TEST7]')
print()

# Loga os clientes no servidor
nick1 = b'Abbi'
s1.sendall(b'NICK %s\r\n' % nick1)
assert recvline(s1) == b':server 001 %s :Welcome\r\n' % nick1
assert recvline(s1) == b':server 422 %s :MOTD File is missing\r\n' % nick1
print('[OK] 1/28')
nick2 = b'Luis'
s2.sendall(b'NICK %s\r\n' % nick2)
assert recvline(s2) == b':server 001 %s :Welcome\r\n' % nick2
assert recvline(s2) == b':server 422 %s :MOTD File is missing\r\n' % nick2
print('[OK] 2/28')
nick3 = b'Caio'
s3.sendall(b'NICK %s\r\n' % nick3)
assert recvline(s3) == b':server 001 %s :Welcome\r\n' % nick3
assert recvline(s3) == b':server 422 %s :MOTD File is missing\r\n' % nick3
print('[OK] 3/28')

# Os clientes entram em 3 canais
ch1 = b'#'+b'canal1'
ch2 = b'#'+b'canal2'
ch3 = b'#'+b'canal3'
s1.sendall(b'JOIN %s\r\n' % ch1)
assert recvcmd(s1, b'JOIN') == b':%s JOIN :%s\r\n' % (nick1, ch1)
print('[OK] 4/28')
s1.sendall(b'JOIN %s\r\n' % ch2)
assert recvcmd(s1, b'JOIN') == b':%s JOIN :%s\r\n' % (nick1, ch2)
print('[OK] 5/28')
s1.sendall(b'JOIN %s\r\n' % ch3)
assert recvcmd(s1, b'JOIN') == b':%s JOIN :%s\r\n' % (nick1, ch3)
print('[OK] 6/28')
s2.sendall(b'JOIN %s\r\n' % ch1)
assert recvcmd(s2, b'JOIN') == b':%s JOIN :%s\r\n' % (nick2, ch1)
print('[OK] 7/28')
s2.sendall(b'JOIN %s\r\n' % ch2)
assert recvcmd(s2, b'JOIN') == b':%s JOIN :%s\r\n' % (nick2, ch2)
print('[OK] 8/28')
s2.sendall(b'JOIN %s\r\n' % ch3)
assert recvcmd(s2, b'JOIN') == b':%s JOIN :%s\r\n' % (nick2, ch3)
print('[OK] 9/28')
s3.sendall(b'JOIN %s\r\n' % ch1)
assert recvcmd(s3, b'JOIN') == b':%s JOIN :%s\r\n' % (nick3, ch1)
print('[OK] 10/28')
s3.sendall(b'JOIN %s\r\n' % ch2)
assert recvcmd(s3, b'JOIN') == b':%s JOIN :%s\r\n' % (nick3, ch2)
print('[OK] 11/28')
s3.sendall(b'JOIN %s\r\n' % ch3)
assert recvcmd(s3, b'JOIN') == b':%s JOIN :%s\r\n' % (nick3, ch3)
print('[OK] 12/28')

# Os clientes saem de canais e cada um fica apenas em um
s1.sendall(b'PART %s\r\n' % ch2)
assert recvcmd(s1, b'PART') == b':%s PART %s\r\n' % (nick1, ch2)
print('[OK] 13/28')
assert recvcmd(s2, b'PART') == b':%s PART %s\r\n' % (nick1, ch2)
print('[OK] 14/28')
assert recvcmd(s3, b'PART') == b':%s PART %s\r\n' % (nick1, ch2)
print('[OK] 15/28')

s1.sendall(b'PART %s :mensagem de saida deve ser ignorada\r\n' % ch3)
assert recvcmd(s1, b'PART') == b':%s PART %s\r\n' % (nick1, ch3)
print('[OK] 16/28')
assert recvcmd(s2, b'PART') == b':%s PART %s\r\n' % (nick1, ch3)
print('[OK] 17/28')
assert recvcmd(s3, b'PART') == b':%s PART %s\r\n' % (nick1, ch3)
print('[OK] 18/28')
s2.sendall(b'PART %s\r\n' % ch1)
assert recvcmd(s1, b'PART') == b':%s PART %s\r\n' % (nick2, ch1)
print('[OK] 19/28')
assert recvcmd(s2, b'PART') == b':%s PART %s\r\n' % (nick2, ch1)
print('[OK] 20/28')
assert recvcmd(s3, b'PART') == b':%s PART %s\r\n' % (nick2, ch1)
print('[OK] 21/28')
s2.sendall(b'PART %s\r\n' % ch3)
assert recvcmd(s2, b'PART') == b':%s PART %s\r\n' % (nick2, ch3)
print('[OK] 22/28')
assert recvcmd(s3, b'PART') == b':%s PART %s\r\n' % (nick2, ch3)
print('[OK] 23/28')
s3.sendall(b'PART %s\r\n' % ch1)
assert recvcmd(s1, b'PART') == b':%s PART %s\r\n' % (nick3, ch1)
print('[OK] 24/28')
assert recvcmd(s3, b'PART') == b':%s PART %s\r\n' % (nick3, ch1)
print('[OK] 25/28')
s3.sendall(b'PART %s\r\n' % ch2)
assert recvcmd(s2, b'PART') == b':%s PART %s\r\n' % (nick3, ch2)
print('[OK] 26/28')
assert recvcmd(s3, b'PART') == b':%s PART %s\r\n' % (nick3, ch2)
print('[OK] 27/28')


# Cada cliente manda uma mensagem
msg1 = b'MENSAGEM 1'
s1.sendall(b'PRIVMSG %s :%s\r\n' % (ch1, msg1))
msg2 = b'MENSAGEM 2'
s2.sendall(b'PRIVMSG %s :%s\r\n' % (ch2, msg2))
msg3 = b'MENSAGEM 3'
s3.sendall(b'PRIVMSG %s :%s\r\n' % (ch3, msg3))

r,_,_=select.select([s1,s2,s3],[],[],0.1)
assert r == []  # ninguém deveria receber as mensagens enviadas
print('[OK] 28/28')

print()
print('FINALIZADO!')

s1.shutdown(socket.SHUT_WR)
s2.shutdown(socket.SHUT_WR)
s3.shutdown(socket.SHUT_WR)