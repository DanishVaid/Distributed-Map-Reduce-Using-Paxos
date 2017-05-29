#!/bin/python

######################
# Danish Vaid, Sai Srimat
# CS171, Project 2
######################

import queue
import socket
import time
import sys


#######################################
# We left in our de-bugging print statements
#   (commented) for ease to test and see
#######################################

# Citizen
class site(object):
    def __init__(self, siteID):
        self.siteID = siteID
        self.numOfCitizens = 0
        self.localBalance = 10
        self.ipAddr = [None]                # 'siteID: IP ADDR'
        self.portAddr = [None]              # 'siteID: Port'

        # self.recSock = None
        self.outgoingChannels = [None]     # Start with None in it so the siteID's line up
        self.incomingChannels = [None]     # Start with None in it so the siteID's line up
        self.queueList = [None]           # Start with None in it so the siteID's line up
        self.snapshotCollection = {}

        self.snapshotCount = 0


    def setUp(self, setupFilePath):
        # print(self.siteID)

        setupFile = open(setupFilePath, "r")
        self.numOfCitizens = int(setupFile.readline())
        for i in range(1, self.numOfCitizens + 1):
            temp_line = setupFile.readline()
            temp_line = temp_line.split()

            # print(i, temp_line[0], temp_line[1])
            
            self.ipAddr.append(temp_line[0])
            self.portAddr.append(temp_line[1])
            self.outgoingChannels.append(None)
            self.incomingChannels.append(None)
            self.queueList.append(queue.Queue())
        
        # print(self.ipAddr)
        # print(self.portAddr)
        # print(self.ipAddr[self.siteID], int(self.portAddr[self.siteID]))

        recSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recSock.bind((self.ipAddr[self.siteID], int(self.portAddr[self.siteID])))
        recSock.listen(1)

        # time.sleep(3)
        # print("Recieving Socket", recSock)
        
        for line in setupFile.readlines():
            sendingID, receivingID = line.strip().split()
            sendingID = int(sendingID)
            receivingID = int(receivingID)            

            # print(sendingID, receivingID)

            if(sendingID == self.siteID):
                time.sleep(5)                   # To ensure the rest of the processes are good to go

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # print((self.ipAddr[sendingID], int(self.portAddr[sendingID])))
                sock.connect((self.ipAddr[receivingID], int(self.portAddr[receivingID])))
                self.outgoingChannels[receivingID] = sock
            elif(receivingID == self.siteID):
                time.sleep(5)

                stream, addr = recSock.accept()
                # print("Receiving")
                self.incomingChannels[sendingID] = stream
        
        # print(self.incomingChannels)
        # print(self.outgoingChannels)

        time.sleep(3)                               # Time break after setting up          
        # print("Finished Setting Up")

    def runCommands(self, commandFilePath):
        with open(commandFilePath) as commandFile:
            for line in commandFile:
                if "send" in line:
                    # print("Command: send")
                    line = line.split()
                    sendTo = int(line[-2])
                    amt = int(line[-1])
                    self.localBalance -= amt
                    self.outgoingChannels[sendTo].sendall(str(amt).encode())
                    self.receive()
                
                elif "sleep" in line:
                    # print("Command: sleep")
                    line = line.split()
                    self.runSleep(int(line[-1]))
                
                elif "snapshot" in line:
                    # print("Command: snapshot")
                    self.makeSnapshot()
            
            self.receive()

    def runSleep(self, sleepTime):
        ticks = int((sleepTime * 1000) / 200)
        for i in range(ticks):
            time.sleep(0.2)             # Sleep chunk
            self.receive()

    def receive(self):
        for i in range(1, len(self.incomingChannels)):
            currChannel = self.incomingChannels[i]
            if currChannel != None:
                currChannel.settimeout(1)
                try:
                    data = currChannel.recv(1024).decode()
                    if data:
                        self.queueList[i].put(data)
                        # print("Queue is empty:", self.queueList[i].empty())
                        while(not self.queueList[i].empty()):
                            currData = self.queueList[i].get()
                            if "markingData" in str(currData):
                                # print("Marking data recevied")
                                markerName = currData.split()[-1]
                                self.snapshotHandler(markerName, i)
                            else:
                                # print("Other information recevied")
                                for j in self.snapshotCollection:
                                    self.snapshotCollection[j].addChannel(i, int(currData))
                                self.localBalance += int(currData)

                except socket.timeout:
                    continue
            
    
    def sendMarkers(self, markerName=None):
        for i in range(1, len(self.outgoingChannels)):
            sock = self.outgoingChannels[i]
            if sock:
                sock.sendall(("markingData " + str(markerName)).encode())

    def makeSnapshot(self):
        self.snapshotCount += 1
        snapshotName = str(self.siteID) + "." + str(self.snapshotCount)
        newSnap = snapshot(self.numOfCitizens, self.siteID, snapshotName, self.localBalance, self.incomingChannels)
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

    # For printing the entire collection and debugging
    def printSnapshotCollection(self):
        for i in self.snapshotCollection:
            self.snapshotCollection[i].printOutput()

    def snapshotHandler(self, markerName, channelNumber):
        # Check if snapshot already exists
        if self.snapshotCollection.get(markerName):
            # Lock the channel if you have already finished this snap
            self.snapshotCollection[markerName].lock(channelNumber)
        else:
            newSnap = snapshot(self.numOfCitizens, self.siteID, markerName, self.localBalance, self.incomingChannels)
            newSnap.lock(channelNumber)
            self.snapshotCollection[markerName] = newSnap
            self.sendMarkers(markerName)
    
        if self.snapshotCollection[markerName].allFinished():
                self.snapshotCollection[markerName].printOutput()


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
        # print("Num of sites", self.sites)
        # print("Snapshot called")
        for i in range(1, self.sites + 1):
            # print(i)
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

    def allFinished(self):
        for i in range(1, len(self.locks)):
            if self.locks[i] != True:
                return False
        return True

    def printOutput(self):
        result = self.snapshotName + ": " + str(self.localBalance)
        for i in range(1, len(self.amtList)):
            if self.amtList[i] != None and i != self.channelID:
                result += " " + str(self.amtList[i])
        print(result)


# Main Function
def main():
    # print("Starting Program\n")
    arguments = sys.argv
    assert(len(arguments) == 4)

    citizen = site(int(arguments[1]))
    citizen.setUp(arguments[2])
    # print("Running Commands")
    citizen.runCommands(arguments[3])

    citizen.closeAllConnections()

if __name__ == "__main__":
    main()
