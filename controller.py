import sys
import socket
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

   
    each_balance = total_money//len(target_branches)
    for branch_tuple in target_branches:
        name, ip, port = branch_tuple

        message = bank_pb2.BranchMessage()
        branch = message.init_branch.Branch()
        branch.name = name
        branch.ip = ip
        branch.port = port
        message.init_branch.balance = each_balance

        message.init_branch.all_branches.extend([branch])

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((socket.gethostbyname(ip), port))
        print(message.SerializeToString())
        message
        s.sendall(message.SerializeToString())
        s.close()

    message = bank_pb2.BranchMessage()
    init_branch = message.init_branch
    transfer = message.transfer
    init_snapshot = message.init_snapshot
    retrieve_snapshot = message.retrieve_snapshot
    return_snapshot = message.return_snapshot

    #branch = populate_branch(message.init_branch.Branch())


if main():
    print("AN ERROR OCCURRED: Non-zero return value")
