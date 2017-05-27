
class Log():	# MAY NOT NEED THIS CLASS

	def __init__(self):
		self.fileNames = [None]		# List of files names, indexes start at 1
		self.dictionaries = [None]	# List of dictionaries, indexes start at 1

		self.logFile = "tempLogFile.txt"


	def append(self, fileName, assocDict):
		self.fileNames.append(fileName)
		self.dictionaries.append(assocDict)

		with open(self.logFile, "w") as f:
			f.seek(0)
			f.truncate()
			f.write(self.toString())


	def getSize(self):
		return len(self.fileNames)
	

	def toString(self):					# FileName1=Key:Val,Key:Val, . . .\n
		finalString = ""				# FileName2=Key:Val,Key:Val, . . . \n ...

		for i in range(1, len(self.fileNames)):
			finalString += str(self.fileNames[i])
			finalString += "="
			formatBool = True
			for key in self.dictionaries[i]:
				if formatBool:
					formatBool = False
				else:
					finalString += ","
				temp = str(key) + ":" + str(self.dictionaries[i][key])
				finalString += temp
			finalString += "\n"

		return finalString

	
	def indexToString(self, index):
		if index == 0 or index >= len(self.fileNames):
			print("--- ERROR: Can not print index", index, "for log object")
			return

		finalString = str(self.fileNames[index])
		finalString += "="
		formatBool = True
		for key in self.dictionaries[index]:
			if formatBool:
				formatBool = False
			else:
				finalString += ","
			temp = str(key) + ":" + str(self.dictionaries[index][key])
			finalString += temp
		finalString += "\n"

		return finalString



# Static Method - Makes a log object from string
def buildLogFromString(inputString):
		lines = inputString.split("\n")

		finalObj = Log()

		for i in range(len(lines) - 1):
			currBreak = lines[i].split("=")
			filename = currBreak[0]
			pairs = currBreak[1].split(",")
			assocDict = {}
			for i in pairs:
				parts = i.split(":")
				assocDict[parts[0]] = parts[1]

			finalObj.append(filename, assocDict)

		return finalObj



# ### TESTING AREA ###
# def testing():
# 	tempObj = Log()
# 	tempObj.append("file1",{"key1": "value1", "key2": "value2", "randkey":"randval"})
# 	tempObj.append("file2",{"key3": "value3", "key4": "value4", "randkey":"randval"})
# 	inStringFormat = tempObj.toString()
# 	print("To String Output:")
# 	print(inStringFormat)
# 	print("Now Rebuilding and printing")
# 	tempObj = buildLogFromString(inStringFormat)
# 	print(tempObj.toString())
# 	print("Now Printing index 1: ")
# 	print(tempObj.indexToString(1))
# 	print("\nAnd indivisual parts just to be sure: ")
# 	print("    ", tempObj.fileNames)
# 	print("    ", tempObj.dictionaries)
# # Run testing
# testing()

# ### END OF TESTING AREA ###
