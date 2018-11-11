import sys
import socket
import random
import threading
import thread
import time
import collections

sys.path.append('/home/vchaska1/protobuf/protobuf-3.5.1/python')
import bank_pb2

class Snapshot:
    def __init__(self, snap_id, balance):
        self.snap_id = snap_id
        self.balance = balance
        self.channels = {} # key: name of source; value: money transfered
        # key: name of source; bool tells us if the channel is active or not
        # all set as false by default, set to true when we recieve a marker message from the source a second time
        self.active_channels = {}
        self.retrieved = False

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
        self.branch_sockets = {} # key: name of other branch; value: client socket of that branch
        self.log_bool = False
        self.snapshots = {} #key: snap_id; value: snap_obj

    def init_connections(self):
        for b in self.branches:
            name = str(b.name)
            ip = str(b.ip)
            port = int(b.port)
            if not name == self.name: # we don't want to connect to ourselves
                print "making client socket for " + name + " on port " + ip + "port: " + str(port)
                branch_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                branch_socket.connect((ip, port))
                self.branch_sockets[name] = branch_socket
        if self.branch_sockets:
            thread.start_new_thread(self.send_transfer_msgs())
                

    def init_msg(self, msg):
        self.balance = msg.balance
        self.branches = msg.all_branches
        self.init_connections()

    def recieve_transfer_msg(self, msg):
        print("Trying to receive")
        print(msg)
        if msg.dst_branch == self.name:
            for ss_id, ss_obj in self.snapshots:
                if ss_obj.retrieved == False and ss_obj.active_channels[msg.src_branch] == False:
                    print "we are setting the channel's state"
                    ss_obj.channels[msg.src_branch] += msg.money
            self.balance_lock.acquire()
            self.balance += msg.money
            self.balance_lock.release()
        else:
            print("Recieved wrong transfer message")
            
    def send_transfer_msgs(self):
        while True:
            for name, socket in self.branch_sockets.iteritems():
                self.balance_lock.acquire()
                send_balance = int(round(random.randint(int(self.balance*0.01), int(self.balance*0.05))))
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
                if self.log_bool:
                    print "Transferring $" + str(send_balance) + " from " + self.name + " to " + name
                    print self.name + "'s new balance: " + str(self.balance)
                print "Sending to " + name
                socket.sendall(transfer_message.SerializeToString() + '\0')
                time.sleep(2)

        thread.exit()
    
    def init_snapshot(self, msg):
        snapshot_id = msg.snapshot_id

        marker_msg = bank_pb2.BranchMessage()
        marker_msg.marker.snapshot_id = snapshot_id
        self.balance_lock.aquire()
        snap_obj = Snapshot(snapshot_id, self.balance)
        self.balance_lock.release()
        self.send_marker_msgs(marker_msg, snap_obj)

    def send_marker_msgs(self, marker_msg, snap_obj):
        #sending marker messages to all other branches
        for name, socket in self.branch_sockets.iteritems():
            snap_obj.channels[name] = 0 # no money has been transferred yet
            snap_obj.active_channels[name] = False
            marker_msg.marker.src_branch = self.name
            marker_msg.marker.dst_branch = name
            socket.sendall(marker_msg.SerializeToString + '\0')
        self.snapshots[snapshot_id] = snap_obj

    def recieve_marker_msg(self, msg):
        snap_id = msg.snapshot_id
        if not snap_id in self.snapshots:
            # this is the first time the branch has seen this snapshot
            self.init_snapshot(msg)
        else:
            self.snapshots[snap_id].active_channels[msg.src_branch] = True
            
    def parse_message(self, client_socket, client_add, msg):
        if not msg:
            print "Error: null message"
            return
        msg_type = msg.WhichOneof("branch_message")

        if msg_type == "init_branch":
            print("initializing branch")
            self.init_msg(msg.init_branch)
            print("Returned from init msg")
        elif msg_type == "transfer":
            self.recieve_transfer_msg(msg.transfer)
        elif msg_type == "init_snapshot":
            self.init_snapshot_msg(msg.init_snapshot)
        elif msg_type == "marker":
            self.recieve_marker_msg(msg.marker)
        elif msg_type == "retrieve_snapshot":
            self.retrieve_snapshot_msg(msg.retrieve_snapshot)
        elif msg_type == "return_snapshot":
            self.return_snapshot_msg(msg.return_snapshot)
        else:
            print "Unrecognized message type: " + str(msg_type)

    def listen_for_message(self, client_socket, client_add):
        print "listening for a message"
        msg = client_socket.recv(1024)
        if msg:
            for m in msg.split('\0')[:-1]:
                branch_message = bank_pb2.BranchMessage()
                branch_message.ParseFromString(m)
                print "parsing message: " + m
                self.parse_message(client_socket, client_add, branch_message)

    def run(self):
        # checking if we should log

        if self.time_interval >= 1000:
            self.log_bool = True
            
        self.time_interval = random.randint(0,self.time_interval+1) # choosing a random time for sleeping
        self.socket.bind((self.ip, self.port))
        self.socket.listen(5)
        print "Branch on ", self.ip, "on port", self.port
        while True:
            print("Just reset loop in run function")
            try:
                client_socket, client_add = self.socket.accept()
                print("Just received a message from", client_add)
                thread.start_new_thread(self.listen_for_message, (client_socket, client_add))
                #self.send_transfer_msgs() # start another thread here
            except KeyboardInterrupt:
                self.socket.close()
                print("Closing socket...")
                sys.exit(0)
        print "We are exiting our branch"

if __name__ == "__main__":

    if(len(sys.argv) != 4):
        print("Usage: python branch.py <branch_name> <port> <time_interval>")
        sys.exit(1)

    name = sys.argv[1]
    ip = socket.gethostbyname(socket.gethostname())
    port = int(sys.argv[2])
    time_interval = int(sys.argv[3])

    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    current_branch = Branch(name, port, time_interval, mysocket)
    current_branch.run()
