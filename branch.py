import sys
import socket
sys.path.append('/home/vchaska1/protobuf/protobuf-3.5.1/python')

import bank_pb2

class Branch:

    def __init__(self, name, port, time, sock):
        self.name = name
        self.port = port
        self.ip = socket.gethostbyname(socket.gethostname())
        self.own_branch = bank_pb2.BranchMessage()
        self.time_interval = time
        self.balance = 0
        self.branches = []
        self.socket = sock


    def handle_message(self, client_socket, client_add):
        while True:
            msg = client_socket.recv(1024)
            if not msg:
                break
            
            self.own_branch.ParseFromString(msg)
            print self.own_branch
            sys.exit(0)
                

        

    def run(self):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(5)

        while True:
            try:
                print "Branch on ", self.ip, "on port", self.port
                client_socket, client_add = self.socket.accept()
                self.handle_message(client_socket, client_add)
                
            except KeyboardInterrupt:
                self.socket.close()
                print("Closing socket...")
                sys.exit(0)

                
def init_valid(name, ip, port, m):
    branch = m.Branch()

    if branch.name == name and branch.ip == ip  and branch.port == port:
        return True
    else:
        return False

if __name__ == "__main__":

    if(len(sys.argv) != 4):
        print("Usage: python branch.py <branch_name> <port> <time_interval>")
        sys.exit(1)

    name = sys.argv[1]
    ip = socket.gethostbyname(socket.gethostname())
    port = int(sys.argv[2])
    time_interval = sys.argv[3]
    

    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    current_branch = Branch(name, port, time_interval, mysocket)
    current_branch.run()



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

    


    


