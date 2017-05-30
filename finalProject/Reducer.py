
class Reducer():
	
	def __init__(self, ID, fileNames):
		self.ID = ID
		self.fileNames = fileNames

		self.conjoinedDict = {}
		self.outputFileName = "filler" + ".txt"

		self.socketFromCLI = None

		self.connection = Connection()


	def reduce(self):
		for fileName in fileNames:
			f = open(fileName, 'r')

			for line in f:
				line = line.split(" ")
				word = line[0]
				count = line[1]

				self.conjoinedDict[word] = conjoinedDict.get(word, count) + count 	#CHECK SYNTAX
																				#CHECK INSTRUCTIONS
																				#"IF A WORD IS NOT IN THE DICTIONARY, IT IS INSERTED
																				#WITH A COUNT OF 1 IN ITS FIRST OCCURENCE"
																				#HOW COULD THERE BE A FIRST OCCURENCE?


	def writeToFile(self):
		f = open(outputFileName, 'w')

		for key, value in conjoinedDict.items():
			f.write(str(key) + " " + str(value) + "\n")

		f.close()


	def makeConnections(self):
		pass
		#SHOULD ONLY HAVE ONE CONNECTION FROM CLI