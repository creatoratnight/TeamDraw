import socket
from _thread import start_new_thread
from game import Game
import pickle

server = "localhost" # Empty for python-server
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen() # Amount of connections allowed (empty for unlimited)
print("Server started, waiting for connections")

connected = set()
games = {}
idCount = 0

def threaded_client(conn, p, gameId):
    global idCount
    conn.send(str.encode(str(p))) # Send player ID once at connection
    while True:
        try:
            #print("trying to receieve data")
            data = pickle.loads(conn.recv(4096*4)) # Receive data from the client
            print("received data from client: ", data)
            if gameId in games:
                game = games[gameId]
                if not data:
                    break
                else:
                    #print("importing data into game object")
                    game.importGameAtServer(data, p)
                    #print(game.p1Name)
                    #print("data imported. exporting data for client")
                    answer = game.exportGameToClient(data[4])
                    print(answer)
                    conn.sendall(pickle.dumps(answer))
            else:
                pass
                    
        except:
            break

    print("Lost connection with player: ", p)
    
    games[gameId].players -= 1
    if games[gameId].players == 0:
        del games[gameId]
        print("Deleting game", gameId)

    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    idCount += 1
    if len(games) == 0:
        gameId = 0
        games[gameId] = Game(gameId)
    latest_game_id = len(games) - 1
    if games[latest_game_id].players < 8 and games[latest_game_id].ready == False:
        gameId = latest_game_id
    elif games[latest_game_id] == 8 or games[latest_game_id].ready == True:
        gameId = latest_game_id + 1
        print("Creating a new game: ", gameId)
        games[gameId] = Game(gameId)

    start_new_thread(threaded_client, (conn, games[gameId].players, gameId))
    games[gameId].players += 1

    if games[gameId].players == 8:
        games[gameId].ready = True