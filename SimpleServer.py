#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

sock = socket.socket()
sock.bind(('', 45454))
sock.listen(1)
while True:
    conn, addr = sock.accept()
    print('Successfully connected:', addr)
    points = ''
    while True:
        data = conn.recv(1024).decode('utf-8')
        print(data)
        if data[:3] == 'SND':
            print('Got Data')
            points = data[3:]
            with open('data.txt', 'w') as f:
                f.write(points)
            conn.send('OK'.encode('utf-8'))
        if data[:3] == 'RCV':
            if points:
                conn.send(points.encode('utf-8'))
            else:
                with open('data.txt', 'r') as f:
                    conn.send(f.read().encode('utf-8'))
        if data[:3] == 'DSC':
            break
    print('Successfully disconnected')
    conn.close()
