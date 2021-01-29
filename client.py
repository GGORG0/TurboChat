# d888888P                   dP                 a88888b. dP                  dP    a88888b. dP oo                     dP   
#    88                      88                d8'   `88 88                  88   d8'   `88 88                        88   
#    88    dP    dP 88d888b. 88d888b. .d8888b. 88        88d888b. .d8888b. d8888P 88        88 dP .d8888b. 88d888b. d8888P 
#    88    88    88 88'  `88 88'  `88 88'  `88 88        88'  `88 88'  `88   88   88        88 88 88ooood8 88'  `88   88   
#    88    88.  .88 88       88.  .88 88.  .88 Y8.   .88 88    88 88.  .88   88   Y8.   .88 88 88 88.  ... 88    88   88   
#    dP    `88888P' dP       88Y8888' `88888P'  Y88888P' dP    dP `88888P8   dP    Y88888P' dP dP `88888P' dP    dP   dP   
# 
#  TurboChat Client 1.0.0
# 
#  A TCP Chat protocol client, preferred to be used in TurBOX.


import datetime
import socket
import threading
import time

FIGLET = """
d888888P                   dP                 a88888b. dP                  dP   
   88                      88                d8'   `88 88                  88   
   88    dP    dP 88d888b. 88d888b. .d8888b. 88        88d888b. .d8888b. d8888P 
   88    88    88 88'  `88 88'  `88 88'  `88 88        88'  `88 88'  `88   88   
   88    88.  .88 88       88.  .88 88.  .88 Y8.   .88 88    88 88.  .88   88   
   dP    `88888P' dP       88Y8888' `88888P'  Y88888P' dP    dP `88888P8   dP   

TurboChat Client 1.0.0

A TCP Chat protocol client, preferred to be used in TurBOX."""

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(FIGLET)

address = input(
    "Not connected. Please enter the server's address >>> ")
if ":" in address:
    ip, port = address.split(":")
else:
    ip = address
    port = 9357


def getLocalIP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


if ip == "localhost" or ip == "127.0.0.1":
    ip = getLocalIP()

client.connect((ip, int(port)))

myNick = ""


def send(type, message):
    client.send(f"{type.upper()}:{message}".encode("ascii"))


def sender():
    while True:
        text = input("")
        if text != "" and text != " ":
            execCmd(text)


def receive():
    global myNick
    brokenCounter = 0
    while True:
        try:
            command = client.recv(1024).decode("ascii")
            cmdList = command.split(":")
            cmdList2 = cmdList.copy()
            cmdList2.pop(0)
            args = ":".join(cmdList2)
            timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if cmdList[0] == "NICK":
                nick = input(f"[{timestamp}]: {args} >>> ")
                send("SETNICK", nick)
                myNick = nick
            elif cmdList[0] == "STOP" or cmdList[0] == "YOU" or cmdList[0] == "CONNECTED" or \
                    cmdList[0] == "LEAVES" or \
                    cmdList[0] == "KICKED":
                print(f"[{timestamp}]: {args}")
            elif cmdList[0] == "JOIN":
                if not args.startswith(myNick):
                    print(f"[{timestamp}]: {args}")
            elif cmdList[0] == "MSG":
                if not args.startswith(myNick + ":"):
                    print(f"[{timestamp}]: {args}")
            elif cmdList[0] == "KICKED" or cmdList[0] == "CANLEAVE":
                print(f"[{timestamp}]: {args}")
                client.close()
                client.shutdown(socket.SHUT_RDWR)
                exit()
                break
            elif cmdList[0] == "UNKNOWN":
                print(f"[{timestamp}]: Unknown command")
            elif cmdList[0] == "":
                print(f"[{timestamp}]: ERROR: Received an empty command, maybe the server is down?")
            else:
                print(
                    f"[{timestamp}]: ERROR: Received an invalid command ( ({cmdList[0]}) {args}), maybe an outdated client?")
        except:
            timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if not brokenCounter >= 5:
                print(f"[{timestamp}]: ERROR: Broken connection, maybe the server is down?")
                brokenCounter += 1
                time.sleep(1)
            else:
                print(f"[{timestamp}]: The connection is broken for too long. Shutting down.")
                exit()
                break


def execCmd(command):
    cmdList = command.split(" ")
    cmdList2 = cmdList.copy()
    cmdList2.pop(0)
    args = " ".join(cmdList2)
    if cmdList[0].startswith("/"):
        send(cmdList[0].upper()[1::], args)
    else:
        send("SAY", command)


receive_thread = threading.Thread(target=receive)
send_thread = threading.Thread(target=sender)
try:
    receive_thread.start()
    while myNick == "":
        pass
    send_thread.start()
except KeyboardInterrupt:
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{timestamp}]: Shutting down.")
    client.close()
    client.shutdown(socket.SHUT_RDWR)
