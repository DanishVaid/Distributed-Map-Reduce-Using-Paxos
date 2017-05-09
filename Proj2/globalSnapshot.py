#!/bin/python
import queue
import socket
import time
import sys


# Citizen
class site(object):
    def __init__(self, siteID):
        self.siteID = siteID
        self.localBalance = 10
        self.addrDict = {}                # 'siteID: IP ADDR' & 'IP ADDR' : 'PORT'

        self.recSock = None
        self.outgoingChannels = [None]     # Start with None in it so the siteID's line up
        self.incomingChannels = [None]     # Start with None in it so the siteID's line up
        self.queueList = [None]           # Start with None in it so the siteID's line up
        self.snapshotCollection = {}

        self.snapshotCount = 0


    def setUp(self, setupFilePath):
        setupFile = open(setupFilePath, "r")
        numProcess = int(setupFile.readline())
        for i in range(1, numProcess + 1):
            temp_line = setupFile.readline()
            temp_line = temp_line.split()
            self.addrDict[i] = temp_line[0]
            self.addrDict[temp_line[0]] = temp_line[1]
            self.outgoingChannels.append(None)
            self.incomingChannels.append(None)
            self.queueList.append(queue.Queue())
        
        self.recSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recSock.bind((self.addrDict[self.siteID], int(self.addrDict[self.addrDict[self.siteID]])))
        self.recSock.setblocking(0)
        self.recSock.listen(1)
        
        for line in setupFile.readlines():
            sendID, recID = line.strip().split()
            sendID = int(sendID)
            recID = int(recID)            
            sendPort = self.addrDict[self.addrDict[sendID]]
            recPort = self.addrDict[self.addrDict[recID]]

            if(sendID == self.siteID):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.addrDict[sendID], int(self.addrDict[self.addrDict[sendID]])))
                self.outgoingChannels[recID] = sock
            elif(recID == self.siteID):
                stream, addr = (self.recSock).accept()
                self.incomingChannels[sendID] = stream

    def runCommands(self, commandFilePath):
        with open(commandFilePath) as commandFile:
            for line in commandFile:
                if "send" in line:
                    line = line.split()
                    sendTo = line[-2]
                    amt = line[-1]
                    self.localBalance -= amt
                    self.outgoingChannels[sendTo].sendall(str(amt))
                    self.receive()
                
                elif "sleep" in line:
                    line = line.split()
                    self.runSleep(int(line[-1]))
                
                elif "snapshot" in line:
                    self.makeSnapshot()

    def runSleep(self, sleepTime):
        ticks = (sleepTime * 1000) / 200
        for i in range(ticks):
            time.sleep(0.2)             # Sleep chunk
            self.receive()

    def receive(self):
        for i in range(1, len(self.incomingChannels)):
            currChannel = self.incomingChannels[i]
            if currChannel != None:
                currChannel.settimeout(15)
                try:
                    data = currChannel.recv(1024)
                    if data:
                        self.queueList[i].put(data)
                        
                        while(not self.queueList[i].empty()):
                            currData = self.queueList[i].get()
                            if "markingData" in str(currData):
                                markerName = currData.split()[-1]
                                self.snapshotHandler(markerName, i)
                            else:
                                for j in self.snapshotCollection:
                                    self.snapshotCollection[j].addChannel(i, int(currData))
                                self.localBalance += int(currData)

                except socket.timeout:
                    continue
    
    def sendMarkers(self, markerName=None):
        for i in range(1, len(self.outgoingChannels)):
            sock = self.outgoingChannels[i]
            if sock:
                sock.sendall("markingData " + str(markerName))

    def makeSnapshot(self):
        self.snapshotCount += 1
        snapshotName = str(self.siteID) + "." + str(self.snapshotCount)
        newSnap = snapshot(len(self.outgoingChannels), self.siteID, snapshotName, self.localBalance, self.incomingChannels)
        self.snapshotCollection[snapshotName] = newSnap
        self.sendMarkers(snapshotName)
        self.receive()

    def closeAllConnections(self):
        for i in range(1, len(self.incomingChannels)):
            j = self.outgoingChannels[i]
            k = self.incomingChannels[i]
            if j:
                j.close()
            if k:
                k.close()

    def printSnapshotCollection(self):
        for i in self.snapshotCollection:
            self.snapshotCollection[i].printOutput()

    def snapshotHandler(self, markerName, channelNumber):
        # Check if snapshot already exists
        if self.snapshotCollection.get(markerName):
            # Lock the channel if you have already seen this snap
            self.snapshotCollection[markerName].lock(channelNumber)
        else:
            newSnap = snapshot(len(self.outgoingChannels), self.siteID, markerName, self.localBalance, self.incomingChannels);
            newSnap.lock(channelNumber)
            self.snapshotCollection[markerName] = newSnap
            self.sendMarkers(markerName)


class snapshot(object):
    def __init__(self, sites, channelID, snapshotName, localBalance, incomingChannels):
        self.sites = int(sites)
        self.channelID = int(channelID)
        self.snapshotName = str(snapshotName)
        self.localBalance = int(localBalance)
        self.incomingChannels = incomingChannels

        self.locks = [None]
        self.amtList = [None]

        # Set Locks and amtlist
        for i in range(1, self.sites + 1):
            if i == self.channelID or incomingChannels[i] == None:
                self.locks.append(True)
                self.amtList.append(None)
            else:
                self.locks.append(False)
                self.amtList.append(0)

    def addChannel(self, channel, amt):
        if not self.locks[channel]:
            self.amtList[channel] += amt

    def lock(self, channel):
        self.locks[channel] = True

    def printOutput(self):
        result = self.snapshotName + ": " + str(self.localBalance)
        for i in range(1, len(self.amtList)):
            if self.amtList[i] and i != self.channelID:
                result += " " + str(self.amtList[i])
        print(result)


# Main Function
def main():
    print("Starting Program\n")
    arguments = sys.argv
    
    assert(len(arguments) == 4)

    citizen = site(int(arguments[1]))
    citizen.setUp(arguments[2])
    citizen.runCommands(arguments[3])
    citizen.printSnapshotCollection()
    citizen.closeAllConnections()

if __name__ == "__main__":
    main()