
class CLI(object):
	
	def __init__(self):
		


	def takeCommand(self):
		print "List of data processing commands:"
		print "map\t\t\tfilename"
		print "reduce\t\tfilename1 filename2 ..."
		print "replicate\tfilename"
		print "stop"
		print "resume"
		print ""

		print "List of data query commands:"
		print "total\t\tpos1 pos2 ..."
		print "print"
		print "merge\t\tpos1 pos2 ..."

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
			elif command == "replicate":
				#SEND MESSAGE TO PAXOS
			elif command == "stop":
				#SEND MESSAGE TO PAXOS
			elif command == "resume":
				#SEND MESSAGE TO PAXOS
			elif command == "total":
				operator.total(args)
			elif command == "print":
				operator.printFileNames()
			else command == "merge":
				operator.merge(args)
			else:
				print "Not a recognizable command"


