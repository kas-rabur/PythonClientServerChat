import threading
import socket


#server
host = "127.0.0.1"
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            msg = client.recv(1024).decode('ascii')
            print(msg)
            if msg.startswith("/kick"):
                if nicknames[clients.index(client)] == "admin":
                    name_to_kick = msg[6:].strip()
                    kick_user(name_to_kick)
                else:
                    client.send("Command was refused!".encode("ascii"))
            elif msg.startswith("/ban"):
                if nicknames[clients.index(client)] == "admin":
                    name_to_ban = msg[5:].strip()
                    kick_user(name_to_ban)
                    with open("bans.txt", "a") as f:
                        f.write(f"{name_to_ban}\n")
                    print(f"{name_to_ban} has been banned from the server.")
                else:
                    client.send("Command was refused!".encode("ascii"))
            else:
                broadcast(msg.encode("ascii"))
        except Exception as e:
            print(f"An error occurred: {e}")
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f"{nickname} left the chat.".encode("ascii"))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with address: {str(address)}")
        
        client.send("NICKNAME".encode("ascii"))
        nickname = client.recv(1024).decode('ascii')
        
        with open("bans.txt", "r") as f:
            bans = f.readlines()
            if f"{nickname}\n" in bans:
                client.send("BAN".encode("ascii"))
                client.close()
                continue
        
        if nickname == "admin":
            client.send("PASS".encode("ascii"))
            password = client.recv(1024).decode('ascii')
            if password != "adminpass":
                client.send("REFUSE".encode("ascii"))
                client.close()
                continue
        
        nicknames.append(nickname)
        clients.append(client)
        print(f"Nickname of client just connected is {nickname}.")
        broadcast(f"{nickname} joined the chat!".encode("ascii"))
        client.send("Connected to the server".encode("ascii"))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send("You were kicked by the admin!".encode("ascii"))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f"{name} has been kicked by an admin.".encode("ascii"))

print("Server is currently listening...")
receive()
