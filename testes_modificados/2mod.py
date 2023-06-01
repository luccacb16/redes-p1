#!/usr/bin/env python3
import socket, base64, select, os
def recvline(s):
    buf = b''
    while True:
        c = s.recv(1)
        buf += c
        if c == b'' or c == b'\n':
            return buf

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 6667))

print('[TEST2]')
print()

# Verifica se o servidor lida corretamente com comando recebido em partes quebradas
#args = base64.b32encode(os.urandom(16))
args = b'PRIMEIRA MSG'
s.sendall(b'P')
s.sendall(b'ING')
s.sendall(b' %s' % args[:5])
s.sendall(args[5:] + b'\r')
s.sendall(b'\n')
assert recvline(s) == b':server PONG server :%s\r\n' % args
print('Caso 1 OK')

# Verifica se o servidor lida corretamente com mais de um comando recebido simultaneamente
#args1 = base64.b32encode(os.urandom(16))
#args2 = base64.b32encode(os.urandom(16))
args1 = b'SEGUNDA MSG'
args2 = b'TERCEIRA MSG'
s.sendall(b'PING %s\r\nPING %s\r\n' % (args1, args2))
assert recvline(s) == b':server PONG server :%s\r\n' % args1
print('Caso 2.1 OK')
assert recvline(s) == b':server PONG server :%s\r\n' % args2
print('Caso 2.2 OK')

# Verifica se o servidor lida corretamente com dados residuais em situação de múltiplos comandos
args1 = b'QUARTA MSG'
args2 = b'QUINTA MSG'
args3 = b'SEXTA MSG'

s.sendall(b'PING %s\r\nPING %s\r\nPING %s' % (args1, args2, args3[:4]))
assert recvline(s) == b':server PONG server :%s\r\n' % args1
print('Caso 3.1 OK')

assert recvline(s) == b':server PONG server :%s\r\n' % args2
print('Caso 3.2 OK')

r,_,_=select.select([s],[],[],0.1)
assert r == []  # não deve receber nada antes de completar o comando
print('Caso 3.3 OK')

s.sendall(b'%s\r' % args3[4:])
r,_,_=select.select([s],[],[],0.1)
assert r == []  # não deve receber nada antes de completar o comando
print('Caso 3.4 OK')

s.sendall(b'\n')
assert recvline(s) == b':server PONG server :%s\r\n' % args3
print('Caso 3.5 OK')

print()
print('FINALIZADO!')

s.shutdown(socket.SHUT_WR)
