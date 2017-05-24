
class CLI(object):
	
	def __init__(self):
		self.dataQuery = Query()

		self.sockToMapper1 = None
		self.sockToMapper2 = None
		self.sockToReducer = None
		self.sockToPaxos = None

		self.connection = Connection()


	def takeCommand(self):
		print("List of data processing commands:")
		print("map\t\t\tfilename")
		print("reduce\t\tfilename1 filename2 ...")
		print("replicate\tfilename")
		print("stop")
		print("resume")
		print("")

		print("List of data query commands:")
		print("total\t\tpos1 pos2 ...")
		print("print")
		print("merge\t\tpos1 pos2 ...")

		while True:
			consoleInput = input("Command (enter 'exit' to quit):")
			consoleInput = consoleInput.split(" ")

			command = consoleInput[0]
			args = consoleInput[1:]

			if command == "quit":
				break
			elif command == "map":
				#SEND MESSAGE TO BOTH MAPPERS
			elif command == "reduce":
				#SEND MESSAGE TO REDUCER
			elif command == "replicate":	#part1
				#SEND MESSAGE TO PAXOS
			elif command == "stop":			#part1
				#SEND MESSAGE TO PAXOS
			elif command == "resume":		#part1
				#SEND MESSAGE TO PAXOS
			elif command == "total":		#part1
				dataQuery.total(args)
			elif command == "print":		#part1
				dataQuery.printFileNames()
			else command == "merge":		#part1
				dataQuery.merge(args)
			else:
				print("Not a recognizable command")


	def config(self):
		pass
		#READ FROM CONFIG FILE FOR IP/PORT OF PROCESSES IN NODE

		#INITIALIZE CONNECTIONS WITH CONNECTION OBJECT


	def makeConnections(self):
		pass
		#SHOULD HAVE OUTGOING CONNECTIONS TO MAP1, MAP2, REDUCE, AND PAXOS