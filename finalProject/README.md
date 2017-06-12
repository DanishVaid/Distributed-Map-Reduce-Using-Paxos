Final Project for 171
-- Danish Vaid, Jake Can
-- UCSB, Spring 2017


[ === Milestone 1 === ]
    Implemented CLI completed for milestone 1.

    Implemented Paxos algorithm completely to reach a consensus for milestone 1. Only 
    tested with an integer instead of a log entry. Successfully reaches consensus on 
    the value. Still maintains debugging statements so we can quickly implement log 
    entries instead of just integers (should be a quick fix).

    To Run (our setup files work with 3 paxos and 3 clients:
        Paxos - python3 Paxos.py [site_ID] pax_config.txt
        Client - python3 CLI.py [site_ID] client_config.txt

        *Each run as their own process


[ === Milestone 2 === ]
    We implemeted all that the lab asked for and that we believe will be tested.

    To run we wrote scripts, run the scripts as such (each in its own terminal):
        Paxos - ./prm_runner [site_ID]
        Client - ./client_runner

    The client_runner script takes the responsiblity of creating the Mapper
    and Reducer processes and running them in the back ground.