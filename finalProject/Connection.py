
class Connection(object):

	def __init__(self):
		pass
		#POSSIBLY HAVE NOTHING

	def openConnection(acceptSock):
		stream, clientAddress = acceptSock.accept()
		return stream


	def closeSocket(sock):
		sock.close()


	def createConnectSocket(IP, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			address = (IP, port)
			sock.connect(address)

		except socket_error as sockError:
			print sockError, IP, port
			sleep(1)
			createConnectSocket(IP, port)

		return sock


	def createAcceptSocket(IP, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			address = (IP, port)
			sock.bind(address)
			sock.listen(10)

		except socket_error as sockError:
			print sockError, IP, port
			sleep(1)
			createAcceptSocket(IP, port)

		return sock
