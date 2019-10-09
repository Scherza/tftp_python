import io
import socket

from support import perror

CHUNK_SIZE = 512
HEADER_SIZE = 4
##### Function which takes in the parameters, then sends a request for a file #####
#####	Then receives the file, and exits when the file is fully received.	  #####
def tftp_receive(filename, server_addr, sp, cp):
	
	file = tftp_file_wrapper_receive(filename)

	sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # UDP socket
	sock.settimeout(1.00) # set timeout for socket -- 
	server_address = (server_addr, sp) # target server address.
	sock.bind((server_addr, cp)) #filters for packets received from server into client port.
	## Send Request ##
	sock.sendto(build_request_rrq(filename), server_address )
	trycount = 0
	## Receive Data ## #todo: check for error packets sent.
	while True:
		datagram, addr, opcode, block_num, data = None 

		try:
			datagram, addr = sock.recvfrom(CHUNK_SIZE + HEADER_SIZE + 16) 
			opcode, block_num, data = unpack_data_packet(datagram)
		except socket.timeout as e:
			if trycount > 2:
				perror("System Timeout has occurred; server may have terminated early.")
			else:
				trycount = trycount + 1
		except TypeError as e:
			perror("Something happened, and the server sent an errant packet. Exiting application.")
			return

		try:
			file.writeto(block_num, data)
		except Exception as e:
			perror("Error while writing to file.")
		
		sock.sendto(get_ack(file.block_num), server_address)

		if len(data) < 512:
			file.close()
			sock.close()
			return

##### Class to abstract file access. #######
class tftp_file_wrapper_receive:
	def __init__(self, filename):
		self.file = open(filename, 'xb') #todo: try/catch
		self.offset = 0
		self.block_num = 0
	def writeto(self, block_ack, data):
		# appends to file if expected block number. Else excepts.
		if self.block_num == block_ack:
			self.offset += self.file.write(data)
			return self.block_num
		else:
			#out-of-order packet. Alternatively, file out-of-range.
			raise Exception("Packet received out-of-order, or out-of-range.")
	def close(self):
		self.file.close()

def build_request_rrq(filename):
	opcode = b'\x00\x01' #opcode 1 for 'gimme file'
	filename_ascii = filename.encode()
	mode = b'netascii' #for ascii data transfer, or, rather, transfer via bytes.
	return opcode + filename + b'\x00' + mode + b'\x00'			

def unpack_data_packet( datagram ):
	opcode = int.from_bytes(datagram[0:2], byteorder='big')
	if opcode == 3:
		block_num = int.from_bytes(datagram[2:4], byteorder='big')
		data = datagram[4:]
		return opcode, block_num, data
	else:
		raise TypeError
		# I don't know what to do with errors now, so we'll just raise a type objection.
		# todo: err... objections for receiving requests and acks. I'll leave it.


def get_ack(ack):
	opcode = b'\x00\x04'
	acknowledgement = ack.to_bytes(2, byteorder='big')
	return opcode + acknowledgement