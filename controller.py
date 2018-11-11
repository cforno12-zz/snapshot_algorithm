import sys
import socket
from random import randint
from time import sleep

sys.path.append('/home/vchaska1/protobuf/protobuf-3.5.1/python')

import bank_pb2

def print_usage_string():
    print("./controller <total balance> <branch file>")

def main():
    if len(sys.argv) != 3:
        print("Incorrect arguments. See usage string:")
        print_usage_string()
        return 1
    
    total_money = None
    try:
        total_money = int(sys.argv[1])
    except ValueError:
        print("Argument 2 should be an integer.")
        print_usage_string()
        return 1

    f = None
    try:
        f = file(sys.argv[2], 'r')
    except IOError:
        print("File " + sys.argv[2] + " not found.")
        print_usage_string()
        return 1

    target_branches = []
    try:
        for line in f.readlines():
            l = line.split()
            assert(len(l) == 3)
            target_branches.append((l[0], l[1], int(l[2])))
    except:
        print("Values in " + sys.argv[2] + " should look like this:")
        print("<branchname> <ip address> <port number>")
        return 1

    # Sort in alphabetical order by name
    target_branches.sort(key=lambda tup:tup[0])

    # Each one gets the same amount of money
    each_balance = total_money//len(target_branches)

    # New init branch message
    # Idea: send the same message to each branch since
    # each gets the same amount of money
    message = bank_pb2.BranchMessage()
    message.init_branch.balance = each_balance

    # Put each branch in a message and put it in the array
    print target_branches
    for branch_tuple in target_branches:
        name, ip, port = branch_tuple

        branch = message.init_branch.Branch()
        branch.name = name
        branch.ip = ip
        branch.port = port
        message.init_branch.all_branches.extend([branch])

    print message
   
    # Send each message
    for name,ip,port in target_branches:
        print str(ip) + " " + str(port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((socket.gethostbyname(ip), port))
        s.sendall(message.SerializeToString()+'\0')
        s.close()

    # Snapshots!
    global_snapshot_id = 0
    while True:
        # Sleep between snapshots
        sleep_time = randint(5, 10)
        #sleep(sleep_time)

        global_snapshot_id += 1
        # Initiate a new snapshot to a random branch.
        # branch_to_initiate is the name of the branch
        branch_to_initiate = target_branches[randint(0, len(target_branches)-1)]
        print("snapshot_id: " + str(global_snapshot_id))

        # Build the message and send it
        snapshot_message = bank_pb2.BranchMessage()
        snapshot_message.init_snapshot.snapshot_id = global_snapshot_id
        
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_socket.connect((socket.gethostbyname(branch_to_initiate[1]),branch_to_initiate[2]))
        new_socket.sendall(snapshot_message.SerializeToString() + '\0')
        new_socket.close() 
        sleep(3)

        # Retrieve the snapshots
        ret = bank_pb2.BranchMessage()
        ret.retrieve_snapshot.snapshot_id = global_snapshot_id 
        for name,ip,port in target_branches:
            ret_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ret_socket.connect((socket.gethostbyname(ip), port))
            ret_socket.sendall(ret.SerializeToString() + '\0')
           
            rec = ret_socket.recv(1024)
            
            snapshot_message = bank_pb2.BranchMessage()
            snapshot_message.ParseFromString(rec.split('\0')[0])
            print_msg = name + ": "
            print_msg += str(snapshot_message.return_snapshot.local_snapshot.balance)
            print_msg += ", "
            sub = 0
            for i,tup in enumerate(target_branches):
                other_name = tup[0]
                if name != other_name:
                    print_msg += other_name + "->" + name + ": "
                    if snapshot_message.return_snapshot.local_snapshot.channel_state:
                        print_msg += str(snapshot_message.return_snapshot.local_snapshot.channel_state[i-sub])
                    else:
                        print_msg += '0'
                    print_msg += ", "
                else:
                    sub = 1

            print(print_msg[:-2])
            ret_socket.close()
        
        break 
    #message = bank_pb2.BranchMessage()
    #init_branch = message.init_branch
    #transfer = message.transfer
    #init_snapshot = message.init_snapshot
    #retrieve_snapshot = message.retrieve_snapshot
    #return_snapshot = message.return_snapshot

    #branch = populate_branch(message.init_branch.Branch())

if main():
    print("AN ERROR OCCURRED: Non-zero return value")
