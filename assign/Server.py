from socket import *
import time
import threading
import sys,os
Port = sys.argv[1] # change this port number if required
duration = sys.argv[2]
timeout = sys.argv[3]
block_duration = int(duration)
serverPort = int(Port)
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(5)
blockname = {}
server_start_time = time.time()
client_login_time = {}
online_client = {}
offline = {}
total_users = {}
block_list = {}
## read the whole files and generate a dictionary that key is username, value is the password
file1 = open("credentials.txt")
while(1):
    
    line1 =file1.readline()
    line1 = line1.strip()
    if not line1:
        break
    username1 = line1.split(" ")
    total_users[username1[0]] = username1[1]
## when client login, broadcast to all of other clients that such client has loged in
def presence_client(username):
    global online_client
    client_list = []
    sentence = str(username) + " has logged in."
    client_list = online_client.values()
    if (len(client_list)==0):
        return
    for socket in client_list:
        socket.send(str.encode(sentence))
## when client logout, broadcast all others
def presence_client_out(username):
    global online_client
    client_list = []
    sentence = str(username) + " has logged out."
    client_list = online_client.values()
    if (len(client_list)==0):
        return
    for socket in client_list:
        socket.send(str.encode(sentence))
## when client input whoelse command, it will return all keys in online_client{}
def whoelse(username,connectionSocket):
    global online_client
    online_client_list = []
    whoelse_list = online_client.keys()
    for item in whoelse_list:
        online_client_list.append(item)
    online_client_list.remove(username)
    data = ' '.join(online_client_list)
    data = "Other clients:"+data
    connectionSocket.send(str.encode(str(data)))    
## this command will return all clients online current and the client that has already been logged
## out but the logout time is smaller that the current time minus the value that given
def whoelsesince(commandline,connectionSocket,username):
    global server_start_time,client_login_time,online_client
    user_list = []
    first = commandline.index("(")+1
    last = commandline.index(")")
    command_time = commandline[first:last]
    users = client_login_time.keys()
    users1 = online_client.keys()
    for user in users:
        if (float(time.time())-float(client_login_time[user])<float(command_time)):
            if user != username: 
               user_list.append(user)
    for user1 in users1:
        if user1 not in users and user1 != username: 
           user_list.append(user1)
    data = ' '.join(user_list)
    data = 'From '+ str(command_time) + 'users are ' + str(data)
    connectionSocket.send(str.encode(data))
## examine the keys in the online_client, and send message to every key except itself and the client
## that has been in block_list of that client.
def broadcast(username,commandline,connectionSocket):
    global online_client,block_list
    conf = 0
    first = commandline.index("(")+1
    last = commandline.index(")")
    message = commandline[first:len(commandline)-1]
    who_online = online_client.keys()
    if username in block_list.keys():        
        for client in who_online:
            if client is not username and client not in block_list[username]:
                if client in block_list.keys():
                    if username not in block_list[client]:
                        socket = online_client[client]
                        socket.send(str.encode(str(username)+":"+" "+str(message)))
                else:
                    socket = online_client[client]
                    socket.send(str.encode(str(username)+":"+" "+str(message)))
            
    elif username not in block_list.keys():
        for client in who_online:
            if client is not username:
                if client in block_list.keys():
                    if username not in block_list[client]:
                        socket = online_client[client]
                        socket.send(str.encode(str(username)+":"+" "+str(message)))
                else: 
                   socket = online_client[client]
                   socket.send(str.encode(str(username)+":"+" "+str(message)))
            

    for values in block_list.values():
        
        if username in values:
            conf = 1
    if username in block_list.keys():
        if len(block_list[username])>0:
            conf = 1
    if conf == 1:
        connectionSocket.send(str.encode("Your message could not be delivered to some recipients."))
            
## when one client want to send message to other, if that client are not in the blacklist and
## it is online, then get that socket from the online_list, if it is offline, save the information as the
## value in the offline dictionary, and the username as the key.
def message3(commandline,connectionSocket,username):
    global online_client,total_users
    first = commandline.index("(")+1
    last = commandline.index(")")
    second = commandline.find("(",last)+1
    user = commandline[first:last]
    message = commandline[second:len(commandline)-1]
##    if username in block_list.keys(): 
##      if user in block_list[username]:
##          connectionSocket.send(str.encode(str(user)+" has been blocked by you"))
    if user in block_list.keys():        
       if (username in block_list[user]):
           connectionSocket.send(str.encode("Your message could not be delivered as the recipient has blocked you."))
       else:
           if user in online_client.keys():
               socket = online_client[user]
               socket.send(str.encode(str(username)+":"+" "+str(message)))
           else:
               if user in total_users.keys() and user != username:
                   if user not in offline.keys():
                       offline[user]=[]
                       offline[user].append(username+":"+message)
                   else:
                       offline[user].append(username+":"+message)
               else:
                   connectionSocket.send(str.encode("Error. Invalid user"))
    else:        
        if user in online_client.keys():
            socket = online_client[user]
            socket.send(str.encode(str(username)+":"+" "+str(message)))
        else:
            if user in total_users.keys() and user != username:
                if user not in offline.keys():
                    offline[user]=[]
                    offline[user].append(username+":"+message+"\n")
                else:
                    offline[user].append(username+":"+message+"\n")
            else:
                connectionSocket.send(str.encode("Error. Invalid user"))
    
## using a dictionary named block_list, username as the key, and the client that it wants to
## block as the value 
def block(commandline,username,connectionSocket):
    global block_list
    first = commandline.index("(")+1
    user2 = commandline[first:len(commandline)-1]
    if user2 != username and user2 in total_users.keys():
        
       if username not in block_list.keys():
           
           block_list[username] = []
           block_list[username].append(user2)
       else:
           block_list[username].append(user2)
       connectionSocket.send(str.encode(str(user2)+" is blocked"))
    elif user2 == username:
        connectionSocket.send(str.encode("Error. Cannot block self"))
    else:
        connectionSocket.send(str.encode("Invalid operate."))
## when client want to unblock any client in the block_list, just delete such key
def unblock(commandline,username,connectionSocket):
    global block_list
    first = commandline.index("(")+1
    user3 = commandline[first:len(commandline)-1]
    if user3 != username and user3 in total_users.keys():
        
       if username in block_list.keys():
           
           if user3 in block_list[username]:              
               new_list = block_list[username]
               new_list.remove(user3)
               block_list[username] = new_list
               connectionSocket.send(str.encode(str(user3)+" is unblocked"))
           else:
               connectionSocket.send(str.encode("Error. "+str(user3)+" was not blocked"))
       else:
           connectionSocket.send(str.encode("No user has been blocked by "+str(username)))
       
    else:
        connectionSocket.send(str.encode("Invalid operate.")) 
## after receive logout command from the client, then send back logout delete username in the online_list
def logout(username,connectionSocket):
    global online_client
    client_login_time[username] = time.time()
    del online_client[username]
    presence_client_out(username)
    connectionSocket.send(str.encode("logout"))
    


def client(connectionSocket,addr):
   global blockname,online_client,total_users,timeout 
   times = 0
   times1 = 0
   jumpout = 0
   clientlist = []
   while(1):
       if jumpout == 1:
               break
       ## get the username and the password
       account = connectionSocket.recv(1024)
       accountname = account.decode('utf-8')
       accountname = accountname.split(",")
       username = accountname[0]
       password = accountname[1]
       jump = 0
       ## if input wrong password or username over three times, then block it 60s
       if (username in blockname):
           if ((time.time() - blockname[username])<block_duration):
               connectionSocket.send(str.encode("You are being blocked"))
               break
       if (addr[0] in blockname):
           
           if ((time.time() - blockname[addr[0]])<block_duration):
               connectionSocket.send(str.encode("You are being blocked"))
               break
       
       while 1:
           
           if username in total_users.keys():
               times = times + 1 
               if (times == 3):
                   blockname[username] = time.time()
                   unconfirm = "You are blocked"
                   connectionSocket.send(str.encode(unconfirm))
                   jump = 1
                   break
               if (password == total_users[username]):
                   x = 2
                   confirm = "Welcome"
                   connectionSocket.send(str.encode(confirm+" "+timeout+" "))
                   presence_client(username)
                   online_client[username] = connectionSocket
                   
                   if username in offline.keys():                      
                       for message in offline[username]:
                           
                           connectionSocket.send(str.encode(str(message+" ")))
                       del offline[username]
                   while(1):
                       ## judge the command and give different service
                       command = connectionSocket.recv(1024)
                       commandline = command.decode('utf-8')
                       com = commandline.split("(")
                       if(commandline == "whoelse"):
                           whoelse(username,connectionSocket)
                       elif(com[0] == "whoelsesince"):
                           whoelsesince(commandline,connectionSocket,username)
                       elif(com[0] == "broadcast"):
                           broadcast(username,commandline,connectionSocket)
                       elif(com[0] == "message"):
                           message3(commandline,connectionSocket,username)
                       elif(com[0] == "block"):
                           block(commandline,username,connectionSocket)
                       elif(com[0] == "unblock"):
                           unblock(commandline,username,connectionSocket)
                       elif(com[0] == "logout"):
                           logout(username,connectionSocket)
                           jumpout = 1
                           break
                       else:
                           connectionSocket.send(str.encode("Error. Invalid command"))
                   break
                   
               else:
                   unconfirm = "Wrong password"
                   connectionSocket.send(str.encode(unconfirm))
                   break
                              
           if username not in total_users.keys():
               unconfirm = "Try again"
               times1 = times1 + 1               
               if(times1 == 3):
                   blockname[addr[0]] = time.time()                   
                   unconfirm = "You are blocked1"
                   jump = 1
                   connectionSocket.send(str.encode(unconfirm))
                   break
               connectionSocket.send(str.encode(unconfirm))
               break
       if(jump == 1):
           break
       


print ("Welcome to my instant messaging application.The server is listening on port number "+Port)
while 1:
    ## open new thread for every client
    connectionSocket, addr = serverSocket.accept()
    t1 = threading.Thread(target = client,args=(connectionSocket,addr))
    t1.start()
