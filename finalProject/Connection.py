import socket
from time import sleep

def openConnection(acceptSock):
	stream, clientAddress = acceptSock.accept()
	return stream


def closeSocket(sock):
	sock.close()


def createConnectSocket(IP, port):
	port = int(port)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		address = (IP, port)
		sock.connect(address)

	except socket.error as sockError:
		print(sockError, IP, port)
		sleep(1)
		createConnectSocket(IP, port)

	return sock
	

def createAcceptSocket(IP, port):
	port = int(port)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		address = (IP, port)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(address)
		sock.listen(10)

	except socket.error as sockError:
		print(sockError, IP, port)
		sleep(1)
		createAcceptSocket(IP, port)

	return sock