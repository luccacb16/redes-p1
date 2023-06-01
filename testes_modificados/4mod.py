#!/usr/bin/env python3
import socket, base64, select, os, re
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

print('[TEST4]')
print()

# Verifica se o servidor aceita um nick contendo apenas caracteres permitidos
nick = b'Luis'
s1.sendall(b'NICK %s\r\n' % nick)
assert recvline(s1) == b':server 001 %s :Welcome\r\n' % nick
print('Caso 1.1 OK!')
assert recvline(s1) == b':server 422 %s :MOTD File is missing\r\n' % nick
print('Caso 1.2 OK!')

# Verifica se impede de usar o mesmo nick do outro cliente
s2.sendall(b'NICK %s\r\n' % nick)
assert recvline(s2) == b':server 433 * %s :Nickname is already in use\r\n' % nick
print('Caso 2 OK!')

# Verifica se permite usar um outro nick
nick2 = b'Abbiati'
s2.sendall(b'NICK %s\r\n' % nick2)
assert recvline(s2) == b':server 001 %s :Welcome\r\n' % nick2
print('Caso 3.1 OK!')
assert recvline(s2) == b':server 422 %s :MOTD File is missing\r\n' % nick2
print('Caso 3.2 OK!')

# Verifica se impede de trocar pra um nick que já esteja em uso
s1.sendall(b'NICK %s\r\n' % nick2)
assert recvline(s1) == b':server 433 %s %s :Nickname is already in use\r\n' % (nick, nick2)
print('Caso 4 OK!')

# Tem que dar como duplicado mesmo se estiver em maiúsculas
s2.sendall(b'NICK %s\r\n' % nick.upper())
assert recvline(s2) == b':server 433 %s %s :Nickname is already in use\r\n' % (nick2, nick.upper())
print('Caso 5 OK!')

# Deve ser permitido trocar por um nick que não esteja em uso
newnick = b'Heitor'
s1.sendall(b'NICK %s\r\n' % newnick)
# e o servidor informa o sucesso de outra forma após o registro
assert recvline(s1) == b':%s NICK %s\r\n' % (nick, newnick)
print('Caso 6 OK!')

r,_,_=select.select([s1,s2],[],[],0.1)
assert r == []  # não é pra receber mais nada além do que foi verificado
print('Caso 7 OK!')

print()
print('FINALIZADO!')

s1.shutdown(socket.SHUT_WR)
s2.shutdown(socket.SHUT_WR)
