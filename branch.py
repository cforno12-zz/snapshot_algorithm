import sys
import socket
sys.path.append('/home/vchaska1/protobuf/protobuf-3.5.1/python')

import bank_pb2


def populate_branch(branch):
    branch.name = sys.argv[1]
    branch.ip = socket.gethostbyname(socket.gethostname())
    branch.port = sys.argv[2]

    return branch
    

if __name__ == "__main__":

    message = bank_pb2.BranchMessage()
    init_branch = message.init_branch
    transfer = message.transfer
    init_snapshot = message.init_snapshot
    retrieve_snapshot = message.retrieve_snapshot
    return_snapshot = message.return_snapshot

    branch = populate_branch(message.init_branch.Branch())

    init_branch.all_branches.extend([branch])
    

    if interval > 1000:
        #output logs of Transfer messages
        pass

    


