# coded by davidson, cole on 2019-09-30

import argparse
import tftp_send
import tftp_receive
import threading

# Building variables, parsing arguments.
from support import perror

parser = argparse.ArgumentParser()
parser.add_argument('-a', type=str, required=True, 
	help='IPv4 address for the server.')
parser.add_argument('-sp', type=int, choices=range(5000, 0xFFFF) ,required=True)
parser.add_argument('-p', type=int, choices=range(5000, 0xFFFF), required=True)

parser.add_argument('-m', type=str, required=True) 
parser.add_argument('-f', type=str, required=True,
	help='Designates file to write to or read from.')

args = parser.parse_args()

server_ip = args.a
server_port = args.sp
client_port = args.p
filename = args.f
mode = args.m



# I'd make a main method, but this is python. Here begins main.
if mode == 'w':
	tftp_send.tftp_send( filename, server_ip, server_port, client_port )
elif mode == 'r':
	tftp_receive.tftp_receive( filename, server_ip, server_port, client_port )
else:
	perror("Mode must be either r (read) or w (write)")