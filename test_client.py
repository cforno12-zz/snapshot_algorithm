import socket
import sys
sys.path.append('/home/vchaska1/protobuf/protobuf-3.5.1/python')

import bank_pb2

if __name__ == "__main__":
    message  = bank_pb2.BranchMessage()



    for i in range(0,4):
        branch = message.init_branch.Branch()
        n = "Cris"
        n += str(i)
        branch.name = n
        branch.ip = socket.gethostbyname(socket.gethostname())
        branch.port = 9090 + i
        message.init_branch.balance = 1000
    
        message.init_branch.all_branches.extend([branch])
    

    print message
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    port = 9080

    s.connect((socket.gethostbyname(socket.gethostname()), port))

    s.sendall(message.SerializeToString())

    s.close()
    
