
class Node(object):	#PROBABLY DON'T NEED THIS CLASS
	
	def __init__(self):
		self.mappers = [Mapper(), Mapper()]
		self.reducer = Reducer()
		self.client = CLI()
		self.paxos = Paxos()






	################ connections ################

	def openLinks():
		#Global variables
		global acceptSock
		global incomeStream
		#Global variables

		#should accept incoming connections
		acceptSock = createAcceptSocket(IP[ownID - 1], port[ownID - 1])

		sleep(5)

		for i in range(len(siteIDFrom)):	#open links that correspond to its site as TCP sockets
			if siteIDFrom[i] == ownID:
				connectSock.append(createConnectSocket(IP[siteIDTo[i] - 1], port[siteIDTo[i] - 1]))
			else:	#not a link for me
				connectSock.append(None)	#to structure list where index is siteID

		for i in range(len(siteIDTo)):		
			if siteIDTo[i] == ownID:		#check all incoming channels
				stream, client_address = acceptSock.accept()
				incomeStream.append(stream)	#store individual streams to recv from


	def closeLinks():
		for sock in connectSock:
			if sock != None:
				sock.close()
		
		acceptSock.close()


	def createConnectSocket(IP, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			address = (IP, port)
			sock.connect(address)

		except socket_error as sockError:
			print(sockError, IP, port)
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
			print(sockError, IP, port)
			sleep(1)
			createAcceptSocket(IP, port)

		return sock


	###########################################################################



	