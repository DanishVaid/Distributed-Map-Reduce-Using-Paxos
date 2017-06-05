

def total(positions):
	f = open("tempLogFile.txt", 'r')
	lines = f.readlines()
	f.close()

	relevantDicts = []
	for position in positions:
		relevantDicts.append(lines[position - 1])

	# Parse relevantDicts and add up the word/frequencies
	keys = []
	values = []
	for dictionary in relevantDicts:
		dictionary = dictionary.split("=")[1]

		entries = dictionary.split(",")
		for entry in entries:
			key = entry.split(":")[0]
			value = int(entry.split(":")[1])

			if key in keys:
				index = keys.index(key)
				values[index] += value

			else:
				keys.append(key)
				values.append(value)

	for i in range(len(keys)):
		print(str(keys[i]) + " " + str(values[i]))


def printFileNames():
	f = open("tempLogFile.txt", 'r')
	lines = f.readlines()
	f.close()

	for line in lines:
		print(line.split("=")[0])


def merge(pos1, pos2):
	f = open("tempLogFile.txt", 'r')
	lines = f.readlines()
	f.close()

	relevantDicts = []
	relevantDicts.append(lines[pos1 - 1])
	relevantDicts.append(lines[pos2 - 1])

	keys = []
	values = []
	
	for dictionary in relevantDicts:
		dictionary = dictionary.split("=")[1]

		entries = dictionary.split(",")
		for entry in entries:
			key = entry.split(":")[0]
			value = int(entry.split(":")[1])

			if key in keys:
				index = keys.index(key)
				values[index] += value

			else:
				keys.append(key)
				values.append(value)

	for i in range(len(keys)):
		print(str(keys[i]) + " " + str(values[i]))



