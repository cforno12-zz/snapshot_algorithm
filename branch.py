import sys
import socket
import random
import threading

sys.path.append('/home/vchaska1/protobuf/protobuf-3.5.1/python')
import bank_pb2

class Branch:

    def __init__(self, name, port, time, sock):
        self.name = name
        self.port = port
        self.ip = socket.gethostbyname(socket.gethostname())
        self.time_interval = time
        self.balance = 0
        self.balance_lock = threading.Lock()
        self.branches = []
        self.socket = sock # server socket
        self.branch_sockets = {} # client sockets of all the other branches

    def init_connections(self):
        for b in self.branches:
            branch_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            branch_socket.connect((b.ip, b.port))
            self.branch_sockets[b.name] = branch_socket



    def init_msg(self, msg):
        self.balance = msg.balance
        self.branches = msg.all_branches
        self.init_connections()

    def recieve_transfer_msg(self, msg):
        if msg.dst_branch == self.name:
            self.balance_lock.acquire()
            self.balance += msg.money
            self.balance_lock.release()
        else:
            print("Recieved wrong transfer message")
    def send_transfer_msg(self):
        for name, socket in self.branch_sockets.items():
            # check if we have enough money
            self.balance_lock.acquire()
            send_balance = round(random.randint(self.balance*0.01, self.balance*0.05))
            if (self.balance - send_balance) < 0:
               print "" 
            
            

    def parse_message(self, client_socket, client_add, msg):
        msg_type = msg.WhichOneof("branch_message")

        if msg_type == "init_branch":
            self.init_msg(msg.init_branch)
        elif msg_type == "transfer":
            self.transfer_msg(msg.transfer)
        #TODO: put in other cases for other messages


    def listen_for_message(self, client_socket, client_add):
        
        msg = client_socket.recv(1024)
        if msg:
            branch_message = bank_pb2.BranchMessage()
            branch_message.ParseFromString(msg)
            self.parse_message(client_socket, client_add, branch_message)


    def run(self):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(5)

        # create a sender thread here

        while True:
            try:
                print "Branch on ", self.ip, "on port", self.port
                client_socket, client_add = self.socket.accept()
                self.listen_for_message(client_socket, client_add)
                print("New stuff") 
                print(self.name)
                print(self.port)
                print(self.ip)
                print(self.time_interval)
                print(self.balance)
                print(self.branches)
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

    # selecting random time interval
    time_interval = random.randint(0,time_interval+1)
    

    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    current_branch = Branch(name, port, time_interval, mysocket)
    current_branch.run()

    


    


