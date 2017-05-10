/*
 * Danish Vaid - 7971484 - danishvaid@umail.ucsb.edu
 * Sai Srimat - 7785504 - srimat@umail.ucsb.edu
 */

 ----- 1) GROUP & WORKLOAD DISTRIBUTION ----
 * Members: Danish Vaid, Sai Srimat
 * Workload Distribution:
    - Site Class (All but receive function): Danish Vaid
    - Snapshot Class: Sai Srimat
    - Receive Function in Citizen Class: Both Members
    - Debugging and Main: Both Memebers

----- 2) DESIGN EXPLANATION ----
* Site Class: The site class is meant to represent a citizen as
        described by our assignment. We made the site class have
        a site ID, the number of total sites (citizen), local balance,
        2 lists to act as the IP and Port address books, 2 lists to
        act the outgoing and incoming channels, and 1 last list to 
        of queues to maintain the FIFO order. There are 2 more variables,
        a dictionary that holds all of the snapshots, according to their
        name(<siteID>.<snapshotNumber>), and a int variable that contains
        the count for how many snapshots the current process has made.

        After creating the site object, you simple run the setup funtion
        with the setup file, and then execute run commands with the commands
        file.

* Snapshot Class: The snapshot class is a object that stores a snapshot
        information along with a few extra variables we defined, namely a 
        list for locks and a list for the amounts in each channel. The locks
        make it so that after the info is read from a channel, that specific
        channel's "log" can be locked so that more info coming from it or
        caused by a different snapshot does not interfere with each other.
        It also serves a dual purpose to telling us when all the information
        for the snapshot has arrived and the snapshot should be printed
    
* The rest of the code is fairly self-explanatory and each function does what
    it's name describes. We left in our de-bugging print statements for easy 
    testing.


----- 3) EXECUTION ----
* This project requires Python 3 to execute

    ./asg2 <site_id> <setup_file> <command_file>