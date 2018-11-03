import sys
import socket
sys.path.append('/home/vchaska1/protobuf/protobuf-3.5.1/python')

import bank_pb2

def init_valid(name, ip, port, m):
    branch = m.Branch()

    if branch.name == name and branch.ip == ip  and branch.port == port:
        return True
    else:
        return False

if __name__ == "__main__":
    name = sys.argv[1]
    ip = socket.gethostbyname(socket.gethostname())
    port = sys.argv[2]

    balance  = 0

    time_interval = sys.argv[3]
    
    if interval > 1000:
        #output logs of Transfer messages
        pass

    branches = []

    # once we recieve a message we check if the init message is populated
    # if it isn't then we assume it is a transfer message
    message = bank_pb2.BranchMessage()
    
    if message.init_branch.Branch().name == '':
        # it is a transfer message
        pass
    else:
        #it is an init message
        message = message.init_branch
        if init_valid(name, ip, port, message):
            balance = message.balance
            for b in message.all_branches:
                branches.extend(b)
        else:
            print("ERROR: Init message was sent to the wrong branch.")

    


    


