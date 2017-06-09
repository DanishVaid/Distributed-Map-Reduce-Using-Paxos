#!/bin/python3

import Paxos

class PRM(object):

	def __init__(self):
		self.paxosRounds = []
		self.minMajority = 0				# Minimum number of votes for quorum

		self.ipAddrs = [None]				# Make the first element None. List of IP addresses of all other Paxos nodes
		self.ports = [None]					# Make the first element None. List of port numbers of all other Paxos nodes

		self.mySock = None					# Socket for incoming messages
		self.incomeStreams = []				# Gather all the streams to check for messages
		self.socketsToPaxos = [None]		# Make the first element None. List of sockets of all other Paxos nodes
		self.sockToClient = None


	