import socket
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost" #172.105.89.134 for python-server
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr) #Start connecting to server
            answer = self.client.recv(4096*4).decode()
            return answer #get player ID from server on connection
        except:
            pass

    def send(self, data):
        try:
            #print("trying to send data: ", data)
            self.client.sendall(pickle.dumps(data)) # Send data to server
            #print("data sent")
            answer = self.client.recv(4096*4)
            return pickle.loads(answer) # Receive data back from server
        except socket.error as e:
            print(e)