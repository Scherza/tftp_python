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
parser.add_argument('-sp', type=int, required=True, help="Argument must be in range 5000-65000")
parser.add_argument('-p', type=int, required=True, help="Argument must be in range 5000-65000")

parser.add_argument('-m', type=str, required=True) 
parser.add_argument('-f', type=str, required=True,
	help='Designates file to write to or read from.')

args = parser.parse_args()

if args.sp <5000 or args.sp > 65535:
	perror("Argument passed outside of valid range for -sp. Range: 5000 - 65535")
	quit()
if args.p < 5000 or args.p > 65535:
	perror("Argument passed outside of valid range for -p. Range: 5000 - 65535")
	quit()


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