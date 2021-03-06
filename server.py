import os
import socket
import threading
import json
import database_handler as dh
import argparse

parser = argparse.ArgumentParser(description='COEN366 Project Client')
parser.add_argument('--server_udpport', type=int, required=True)
# Check ipconfig (using 'what is my ip' is fine for ENCS lab PCs as they have public IPs)
parser.add_argument('--server_host', type=str, required=True)

args = parser.parse_args()

HOST = args.server_host
PORT = args.server_udpport

#PORT = 5051
#HOST = '172.30.105.221'
UDPServerSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPServerSocket.bind((HOST, PORT))

#TASK 1
def registration(message, address):
    
    #response = dh.register_client(message['name'], message['IP'], message['UDP_socket'], message['TCP_socket'])
    # We use the actual address the client used to send the datagram as the DB address, not the address in the message
    response = dh.register_client(message['name'], address[0], message['UDP_socket'], message['TCP_socket'])

    reply={}

    if response[0] == "REGISTERED":
        reply['service']=response[0]
        reply['request_#']=message['request_#']
    else:
        reply['service']=response[0]
        reply['request_#']=message['request_#']
        reply['reason']=response[1]
    
    msg=json.dumps(reply)
    
    UDPServerSocket.sendto(msg.encode(), address)


def derigistration(message):
    dh.deregister(message['name'])
   

def update_contact(message, address):
    
    response = dh.update_client(message['name'], address[0], message['UDP_socket'], message['TCP_socket'])

    reply={}

    if response[0] == "UPDATE-CONFIRMED":
        reply['service']=response[0]
        reply['request_#']=message['request_#']
        reply['name']=message['name']
        reply['IP']=address[0]
        reply['UDP_socket']=message['UDP_socket']
        reply['TCP_socket']=message['TCP_socket']
    else:
        reply['service']=response[0]
        reply['request_#']=message['request_#']
        reply['name']=message['name']
        reply['reason']=response[1]
    
    msg=json.dumps(reply)
    
    UDPServerSocket.sendto(msg.encode(), address)

#TASK 2
def publishing(message, address):

    response = dh.publish_files(message['name'], message['list of files'])

    reply={}

    if response[0] == "PUBLISHED":
        reply['service']=response[0]
        reply['request_#']=message['request_#']
    else:
        reply['service']=response[0]
        reply['request_#']=message['request_#']
        reply['reason']=response[1]
    
    msg=json.dumps(reply)
    
    UDPServerSocket.sendto(msg.encode(), address)
    

def file_removal(message, address):
    
    response = dh.remove_files(message['name'], message['list of files'])

    reply={}

    if response[0] == "REMOVED":
        reply['service']=response[0]
        reply['request_#']=message['request_#']
    else:
        reply['service']=response[0]
        reply['request_#']=message['request_#']
        reply['reason']=response[1]
    
    msg=json.dumps(reply)
    
    UDPServerSocket.sendto(msg.encode(), address) 

#TASK 3
def retrieve_all(message, address):
    
    response = dh.retrieve_all()

    reply={}

    if response[0] == "RETRIEVE":
        reply['service']=response[0]
        reply['request_#']=message['request_#']
        reply['list']=response[1]
    else:
        reply['service']=response[0]
        reply['request_#']=message['request_#']
        reply['reason']=response[1]
    
    msg=json.dumps(reply)
    
    UDPServerSocket.sendto(msg.encode(), address) 

def retrieve_infot(message, address):
   
    response = dh.retrieve_infot(message['name'])

    reply={}
   
    if response[0] == "RETRIEVE-INFOT":
       reply['service'] = response[0]
       reply['request_#']=message['request_#']
       reply['name']=response[1]
       reply['IP']=response[2]
       reply['TCP_socket']=response[3]
       reply['list']=response[4]
    else:
        reply['service']=response[0]
        reply['request_#']=message['request_#']
        reply['reason']=response[1]
    
    msg=json.dumps(reply)
    
    UDPServerSocket.sendto(msg.encode(), address) 

def search_file(message, address):

    response = dh.search_file(message['File-name'])

    reply={}

    if response[0] == "SEARCH-FILE":
       reply['service'] = response[0]
       reply['request_#']=message['request_#']
       reply['list']=response[1]
    else:
        reply['service']=response[0]
        reply['request_#']=message['request_#']
        reply['reason']=response[1]
    
    msg=json.dumps(reply)
    
    UDPServerSocket.sendto(msg.encode(), address) 


def handle_client(message, address, port):

    print("[NEW CONNECTION] " + str(address) + ':' + str(port) + " connected.")
    print("Received message: " + message)

    message_json=json.loads(message[2:-1])
    service_type=message_json['service']

    #end = address.find(",")
    #CLIENT_HOST=address[2:end-1]
    #CLIENT_PORT=address[end+1:-1]
    CLIENT_HOST = address
    CLIENT_PORT = port
    addr = (CLIENT_HOST, int(CLIENT_PORT)) 

    if service_type == "REGISTER":
        registration(message_json, addr)
    elif service_type == "DE-REGISTER":
        derigistration(message_json)
    elif service_type == "PUBLISH":
        publishing(message_json, addr)
    elif service_type == "REMOVE":
        file_removal(message_json, addr)
    elif service_type == "RETRIEVE-ALL":
        retrieve_all(message_json, addr)
    elif service_type == "RETRIEVE-INFOT":
        retrieve_infot(message_json, addr)
    elif service_type == "SEARCH-FILE":
        search_file(message_json, addr)
    elif service_type == "UPDATE-CONTACT":
        update_contact(message_json, addr)

    # msg="Message Received"
    # bytes_msg=msg.encode()
    # UDPServerSocket.sendto(bytes_msg, (CLIENT_HOST, int(CLIENT_PORT)))



def start():
    #UDPServerSocket.listen()
    while True:
        message_address_bytes_pair = UDPServerSocket.recvfrom(1024)
        message = format(message_address_bytes_pair[0])
        address = message_address_bytes_pair[1][0]
        port = message_address_bytes_pair[1][1]
        thread = threading.Thread(target=handle_client, args=(message, address, port))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}" )


print("Server is starting...")
start()
