# d888888P                   dP                 a88888b. dP                  dP   .d88888b
#    88                      88                d8'   `88 88                  88   88.    "'
#    88    dP    dP 88d888b. 88d888b. .d8888b. 88        88d888b. .d8888b. d8888P `Y88888b. .d8888b. 88d888b. dP   .dP .d8888b. 88d888b.
#    88    88    88 88'  `88 88'  `88 88'  `88 88        88'  `88 88'  `88   88         `8b 88ooood8 88'  `88 88   d8' 88ooood8 88'  `88
#    88    88.  .88 88       88.  .88 88.  .88 Y8.   .88 88    88 88.  .88   88   d8'   .8P 88.  ... 88       88 .88'  88.  ... 88
#    dP    `88888P' dP       88Y8888' `88888P'  Y88888P' dP    dP `88888P8   dP    Y88888P  `88888P' dP       8888P'   `88888P' dP
# 
#  TurboChat Server 1.0.0
# 
#  A TCP Chat protocol server, preferred to be used in TurBOX.


import datetime
import socket
import threading
import time


# from random import randint


def getLocalIP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


# host = socket.gethostbyname(socket.gethostname())
host = getLocalIP()
port = 9357
# port = randint(1000, 9999)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clients = {}

serverRunning = False


class Client:
    def __init__(self, socketClient, nickname):
        self.socketClient = socketClient
        self.nickname = nickname
        self.running = True


def broadcastToAll(type, message):
    for client in clients.values():
        client.socketClient.send(f"{type.upper()}:{message}".encode("utf-8"))


def send(client, type, message):
    client.socketClient.send(f"{type.upper()}:{message}".encode("utf-8"))


def sendToRawClient(client, type, message):
    client.send(f"{type.upper()}:{message}".encode("utf-8"))


def handle(client):
    while serverRunning and clients[client.nickname].running:
        try:
            command = client.socketClient.recv(1024).decode("utf-8")
            cmdList = command.split(":")
            cmdList2 = cmdList.copy()
            cmdList2.pop(0)
            args = ":".join(cmdList2)
            if cmdList[0] == "MSGIN" or cmdList[0] == "SAY":
                Log(True, "MSG", f"{client.nickname}: {args}")
            # elif cmdList[0] == "SETNICK":
            # Log(False, "SETNICK", f"{client.nickname} ")
            elif cmdList[0] == "LEAVE" or cmdList[0] == "EXIT" or cmdList[0] == "QUIT":
                send(client, "CANLEAVE", "You can now disconnect.")
                Log(True, "LEAVES", f"{client.nickname} has left the chat.")
                client.socketClient.close()
                client.socketClient.shutdown(socket.SHUT_RDWR)
                del clients[client.nickname]
                break
            elif cmdList[0] == "ME":
                send(client, "YOU", f"Your nickname is {client.nickname}")
            else:
                send(client, "UNKNOWN", "Unknown command.")
        except:
            nick = client.nickname

            del clients[nick]
            Log(True, "LEAVES", f"{nick} has left the chat.")
            break


def receive():
    while True:
        client, address = server.accept()
        Log(False, "CONNECT", f"{str(address)}  has connected. Asking for nickname.")
        args = ""
        goodNick = False
        while not goodNick:
            sendToRawClient(client, "NICK", "Please enter a nickname.")
            command = client.recv(1024).decode("utf-8")
            cmdList = command.split(":")
            cmdList2 = cmdList.copy()
            cmdList2.pop(0)
            args = ":".join(cmdList2)
            if cmdList[0] == "SETNICK" and len(args) >= 3 and args not in clients:
                goodNick = True

        user = Client(client, args)

        clients[args] = user

        send(user, "CONNECTED", f"Successfully connected to the server as {args}")
        time.sleep(1)
        Log(True, "JOIN", f"{args} has joined.")

        thread = threading.Thread(target=handle, args=(user,))

        thread.start()


def Log(broadcast, type, message):
    with open("server.log", "a") as file:
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        text = f"[{timestamp}]: ({type}) {message}\n"
        file.write(text)
        print(text)
        if broadcast:
            broadcastToAll(type, message)


def main():
    global serverRunning
    server.bind((host, port))
    server.listen()
    Log(False, "STARTINFO", f"Listening on {host}:{port}")
    Log(False, "START", "Server started.")
    serverRunning = True
    receive()
    # receive_thread = threading.Thread(target=receive)
    # receive_thread.start()


def cmdLine():
    text = input("")
    if text != "" and text != " ":
        execCmd(text)


def execCmd(command):
    cmdList = command.split(" ")
    cmdList2 = cmdList.copy()
    cmdList2.pop(0)
    args = " ".join(cmdList2)
    cmd = cmdList[0].upper()
    if cmdList[0].startswith("/"):
        cmd = cmdList[0][1::].upper()
    if cmd == "KICK":
        if clients[args]:
            clients[args].running = False
            send(clients[args], "KICK", "You have been kicked by the server console")
            clients[args].socketClient.close()
            clients[args].socketClient.shutdown(socket.SHUT_RDWR)
            del clients[args]
    elif cmd == "STOP":
        Log(True, "STOP", "Stopping server.")
        serverRunning = False
        for client in clients.values():
            try:
                send(client, "KICKED", "You have been kicked because the server is shutting down.")
                client.socketClient.close()
                client.socketClient.shutdown(socket.SHUT_RDWR)
                Log(True, "LEAVES", f"Kicked {client.nickname}, because the server is shutting down.")
            except:
                Log(False, "ERROR", f"An error occurred while kicking {client.nickname}")
        server.close()
        server.shutdown(socket.SHUT_RDWR)
        exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:

        if server:
            Log(True, "STOP", "Stopping server.")
            serverRunning = False
            for client in clients.values():
                try:
                    send(client, "KICKED", "You have been kicked because the server is shutting down.")
                    client.socketClient.close()
                    client.socketClient.shutdown(socket.SHUT_RDWR)
                    Log(True, "LEAVES", f"Kicked {client.nickname}, because the server is shutting down.")
                except:
                    Log(False, "ERROR", f"An error occurred while kicking {client.nickname}")
            server.close()
            server.shutdown(socket.SHUT_RDWR)
        else:
            Log(False, "STOP", "Stopping server.")
        exit()
