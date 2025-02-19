import socket
import threading
import time

def session(conn):
    global  map
    if len(client_list) == 0:
        conn.send("1".encode("utf-8"))
        objects = conn.recv(120000).decode("utf-8")
        objects = eval(objects)
        map = objects
    else:
        conn.send("0".encode("utf-8"))
    client_list[conn] = (0,0)
    while True:
        coordinates = conn.recv(1024).decode("utf-8")
        coordinates = eval(coordinates)
        client_list[conn] = coordinates
        
def listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 986))
    s.listen()
    while True:
        conn, addr = s.accept()
        threading.Thread(target=session, args=(conn,)).start()

client_list = {}
map = []
listener()