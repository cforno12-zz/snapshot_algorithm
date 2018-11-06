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
   
    try:
        f = file(sys.argv[2], 'r')
    except IOError:
        print("File" + sys.argv[2] + " not found.")
        return 1

    message = bank_pb2.BranchMessage()
    init_branch = message.init_branch
    transfer = message.transfer
    init_snapshot = message.init_snapshot
    retrieve_snapshot = message.retrieve_snapshot
    return_snapshot = message.return_snapshot

    branch = populate_branch(message.init_branch.Branch())


if main():
    print("AN ERROR OCCURRED: Non-zero return value")
