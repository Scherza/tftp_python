
import socket

from support import perror, notify

CHUNK_SIZE = 512 # Bytes

def tftp_send(filename, sa, sp, cp):
	
	try:
		file = tftp_file_wrapper_send(filename)
	except FileNotFoundError as e:
		perror("There is no file found with the specified filename in current directory.")
		return

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.settimeout(1.00)
	server_address = (sa, sp)
	sock.bind((sa, cp))

	sock.sendto( build_request_wrq(filename), server_address )
	ackgram, addr =  sock.recvfrom(512)
	ack = get_ack(ackgram)
	notify("Received ack " + str(ack) + " from " + addr)
	trycount = 0

	while True:
		# read from file at <block> ... if block matches cached, reuse, if block is cached+1, read new.
		try:
			data = file.read(ack)
		except EOFError as e:
			break
		# send bit
		else:
			datagram = get_datagram(ack, data)
			sock.sendto( datagram, server_address )
		# await ack
		try:
			ackgram, addr = sock.recvfrom(512)
		except TimeoutError as e:
			perror("Server Timed out.")
			break
		else:
			ack = get_ack(ackgram)


	file.close()
	sock.close()

		
class tftp_file_wrapper_send:
	def __init__(self, filename):
		self.file = open(filename, 'r')
		self.offset = 0
		self.cache = ""
	def read(self, ack):
		try:# if cached item requested, return item. if next requested, return next. Else fail.
			if ack == self.offset - 1:
				return self.cache
			elif ack == self.offset:
				self.cache = self.file.read(CHUNK_SIZE)
				offset = ack
				return self.cache
			else:
				perror("An attempt was made to read file data out-of-order.")
				raise Exception
		except EOFError as e:
			raise e #This is the completion condition. 
		except Exception as e:
			perror("An unknown exception has occurred while trying to read file data.")
			raise e
	def close(self):
		self.file.close()

def build_request_wrq(filename):
	opcode = b'\x00\x02' #opcode 1 for 'gimme file'
	filename_ascii = filename.encode()
	mode = b'netascii' #for ascii data transfer, or, rather, transfer via bytes.
	return opcode + filename_ascii + b'\x00' + mode + b'\x00'

def get_ack(ackgram):
	opcode = int.from_bytes( ackgram [0:2], byteorder ='big')
	if opcode == 4:
		ack = int.from_bytes( ackgram[2:4], byteorder='big' )
		return ack 
	else:
		perror("An errant packet was sent in place of an ack. Exception raised.")
		raise TypeError

def get_datagram(ack, data):
	opcode = b'\x00\x03'
	acknowledgement = ack.to_bytes(2, byteorder='big')
	datum = data.encode('ascii')
	return opcode + acknowledgement + datum