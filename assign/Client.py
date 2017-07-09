import sys,os
import time
import threading

from socket import *
serverName = sys.argv[1]
Port = sys.argv[2]
signal = 0
serverPort = int(Port) #change this port number if required
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
logofftime = time.time()
inactive_time = 1000
def loging():
    global logofftime,inactive_time
    username = raw_input('Input your username:')
    password = raw_input('Input your password:')
    while(1):
        account = username+','+password
        clientSocket.sendall(str.encode(account))
        logofftime = time.time()
        modifiedSentence = clientSocket.recv(1024)
        first_sentence = modifiedSentence.decode('utf-8')
        first_sentence = str(first_sentence)
        if (modifiedSentence.decode('utf-8') == "Try again"):
            print('From Server:', modifiedSentence.decode('utf-8'))
            username = raw_input('Username:')
            password = raw_input('Password:')
            continue
        if (first_sentence.split()[0]=="Welcome"): 
            print('Welcome to the greatest messaging application ever!')
            inactive_time = int(first_sentence.split()[1])
            if len(first_sentence.split())>2:
                
##                for v in range(2,len(first_sentence.split("u"))):
##                    if first_sentence.split()[v] != "u":
##                       print(first_sentence.split()[v], end=='')
                
                st = first_sentence.split()
                str2 = str(st[2:])
                
                print(" ".join(st[2:]))
                
                
                
            t3 = threading.Thread(target = receive)
            t3.start()
            inputcommand()
            clientSocket.close()
            break
            
        if (modifiedSentence.decode('utf-8') == "You are blocked"):
            print('Invalid Password. Your account has been blocked. Please try again later.')
            clientSocket.close()
            break
        if (modifiedSentence.decode('utf-8') == "You are blocked1"):
            print('Invalid Username.Your IP address has been blocked')
            clientSocket.close()
            break
        if (modifiedSentence.decode('utf-8') == "You are being blocked"):           
            print('Your account is blocked due to multiple login failure. Please try again later.')
            clientSocket.close()
            break
        if (modifiedSentence.decode('utf-8') == "Wrong password"):           
            print('Invalid Password. Please try again')
            password=raw_input('Password:')

## examine if the client has been inactivity for a certain period           
def timeout():
    global logofftime,inactive_time,clientSocket
    while(1):
       current_time = time.time()
       if (current_time - logofftime > inactive_time):
           clientSocket.sendall(str.encode("logout"))
           break
## get the input            
def inputcommand():
    global signal,logofftime
    while(1): 
       command = raw_input()
       clientSocket.sendall(str.encode(command))
       logofftime = time.time()
       if signal == 1:
           break
       
## get the receive from the server   
def receive():
    global signal
    while(1):
        sentence = clientSocket.recv(1024)
        
        if sentence.decode('utf-8') == "logout":
            print("You are logout")
            signal = 1
            break
        print(sentence.decode('utf-8'))
        
        
    
t1 = threading.Thread(target = loging)
t2 = threading.Thread(target = timeout)
t1.start()
t2.start()


    

