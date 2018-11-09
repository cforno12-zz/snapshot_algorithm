import sys
import socket
import random
import threading
import time

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
            
    def send_transfer_msgs(self):
        for name, socket in self.branch_sockets.iteritems():
            self.balance_lock.acquire()
            send_balance = round(random.randint(self.balance*0.01, self.balance*0.05))
            # check if we have enough money
            if (self.balance - send_balance) < 0:
                print "Cannot send more money."
                self.balance_lock.release()
                continue
            self.balance -= send_balance
            self.balance_lock.release()
            transfer_message = bank_pb2.BranchMessage()
            transfer_message.transfer.money = send_balance
            transfer_message.transfer.src_branch = self.name
            transfer_message.transfer.dst_branch = name
            socket.sendall(transfer_message.SerializeToString() + '\0')
            time.sleep(self.time_interval*0.001)
            

    def parse_message(self, client_socket, client_add, msg):
        msg_type = msg.WhichOneof("branch_message")

        if msg_type == "init_branch":
            self.init_msg(msg.init_branch)
        elif msg_type == "transfer":
            self.transfer_msg(msg.transfer)
        elif msg_type == "init_snapshot":
            pass
        elif msg_type == "marker":
            pass
        elif msg_type == "retrieve_snapshot":
            pass
        elif msg_type == "return_snapshot":
            pass
        elif msg_type == None:
            print "There was an error recieving a message"

    def listen_for_message(self, client_socket, client_add):
        msg = client_socket.recv(1024)
        if msg:
            for m in msg.split('\0')
            branch_message = bank_pb2.BranchMessage()
            branch_message.ParseFromString(m)
            self.parse_message(client_socket, client_add, branch_message)


    def run(self):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(5)

        # create a sender thread here

        while True:
            try:
                print "Branch on ", self.ip, "on port", self.port
                client_socket, client_add = self.socket.accept()
                self.listen_for_message(client_socket, client_add) # start a new thread here
                self.send_tranfer_messages() # start another thread here
                
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

    


    


