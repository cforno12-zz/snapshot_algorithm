import sys
import socket
sys.path.append('/home/vchaska1/protobuf/protobuf-3.5.1/python')

import bank_pb2

class Branch:

    def __init__(self, name, port, time, sock):
        self.name = name
        self.port = port
        self.ip = socket.gethostbyname(socket.gethostname())
        self.time_interval = time
        self.balance = 0
        self.branches = []
        self.socket = sock

    def init_msg(self, msg):
        self.balance = msg.balance
        self.branches = msg.branches

    def transfer_msg(self, msg):
        if msg.dst_branch == self.name:
            self.balance += msg.money
        else:
            print("Recieved wrong transfer message")

    def parse_message(self, client_socket, client_add, msg):
        msg_type = msg.WhichOneOf("branch_message")

        if msg_type == "init_branch":
            self.init_msg(client_socket, client_add, msg.init_branch)
        elif msg_type == "transfer":
            self.transfer_msg(client_socket, client_add, msg)
        #TODO: put in other cases for 


    def listen_for_message(self, client_socket, client_add):
        while True:
            msg = client_socket.recv(1024)
            if not msg:
                break
            
            msg = bank_pb2.BranchMessage().ParseFromString(msg)
            self.parse_message(client_socket, client_add, msg)


    def run(self):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(5)

        while True:
            try:
                print "Branch on ", self.ip, "on port", self.port
                client_socket, client_add = self.socket.accept()
                self.listen_for_message(client_socket, client_add)
                
            except KeyboardInterrupt:
                self.socket.close()
                print("Closing socket...")
                sys.exit(0)

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

    


    


