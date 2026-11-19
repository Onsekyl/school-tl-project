import socket
import os

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('172.20.241.9', 20000))
s.sendall(b'2\n')

chunks = []
while True:
    data = s.recv(1024)
    if len(data) == 0:
        break
    chunks.append(data.decode('utf-8'))

with open (os.path.join(os.getcwd(), f"received-data.txt"), "w", newline="", encoding="utf-8") as f:
    f.writelines(chunks)

s.close()
