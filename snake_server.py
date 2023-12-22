import numpy as np
import socket
from _thread import *
import pickle
from snake import SnakeGame
import uuid
import time
import rsa

# server = "10.11.250.207"
server = "localhost"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clients = []
publicKey, privateKey = rsa.newkeys(1024)

counter = 0 
rows = 20 

class Client:
    socket = None
    uuid = None
    color = None
    key = None

    def __init__(self, connectionSocket):
        self.socket = connectionSocket
        self.uuid = str(uuid.uuid4())
        self.key = rsa.PublicKey.load_pkcs1(self.socket.recv(4096), "PEM")
        self.socket.send(publicKey.save_pkcs1("PEM"))
        game.add_player(self.uuid, color=self.color)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
s.settimeout(0.5)
print("Waiting for a connection, Server Started")


game = SnakeGame(rows)
game_state = "" 
last_move_timestamp = time.time()
interval = 0.2
moves_queue = set()



def game_thread() : 
    global game, moves_queue, game_state 
    while True :
        last_move_timestamp = time.time()
        game.move(moves_queue)
        moves_queue = set()
        game_state = game.get_state()
        while time.time() - last_move_timestamp < interval : 
            time.sleep(0.1) 



rgb_colors = {
    "red" : (255, 0, 0),
    "green" : (0, 255, 0),
    "blue" : (0, 0, 255),
    "yellow" : (255, 255, 0),
    "orange" : (255, 165, 0),
} 
rgb_colors_list = list(rgb_colors.values())



def main() : 
    global counter, game, privateKey

    

    start_new_thread(game_thread, ())
    s.settimeout(0.1)
    
    while True :
        input = False

        try:
            conn, addr = s.accept()
            print("Connected to:", addr)
            clients.append(Client(conn))
        except socket.timeout:
            pass

        for client in clients:
            #data = client.socket.recv(500).decode()
            data = client.socket.recv(1024)
            #client.socket.send(game_state.encode())
            
            move = None 
            if not data :
                print("no data received from client")
                game.remove_player(client.uuid)
                client.socket.close()
                clients.remove(client)
                break

            try:
                data = rsa.decrypt(data, privateKey)
                #data = rsa.decrypt(data, client.key)
                data = data.decode()
            except:
                continue 



            if data == "get" : 
                #print("received get")
                pass 
            elif data == "quit" :
                print("received quit")
                game.remove_player(client.uuid)
                clients.remove(client)
                break
            elif data == "reset" : 
                game.reset_player(client.uuid)

            elif data in ["up", "down", "left", "right"] : 
                move = data
                moves_queue.add((client.uuid, move))
            
            elif data in ['z', 'x', 'c']:
                print("letter pressed")
                input = True
                for cl in clients:
                    if cl == client:
                        continue
                    cl.socket.send(rsa.encrypt(data.encode(), cl.key))
            #else :
                #print("Invalid data received from client:", data)
            else:
                found_letter = False
                for char in data:
                    if char in ['z', 'x', 'c']:
                        print("letter pressed")
                        found_letter = True
                        input = True
                        for cl in clients:
                            if cl == client:
                                continue
                            cl.socket.send(rsa.encrypt(data.encode(), cl.key))
                        break  # Exit loop after finding a letter

                if not found_letter:
                    print("Invalid data received from client:", data)
            if not input:
                client.socket.send(game_state.encode())
                
       # conn.close()

if __name__ == "__main__" : 
    main()