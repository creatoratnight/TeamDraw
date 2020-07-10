class Game:
    def __init__(self, id):
        self.id = id
        self.name = ["", "", "", "", "", "", "", ""]
        self.canvas = [[], [], [], [], [], [], [], []]
        self.active = [False, False, False, False, False, False, False, False]
        self.done = [False, False, False, False, False, False, False, False]
        self.ready = False
        self.players = 0
        self.res = 80

        for i in range(8):
            self.canvas[i] = self.emptyCanvas()

    def emptyCanvas(self):
        grid = []
        for n in range(self.res):
            grid.append([0] * self.res)
        return grid

    def exportGameToClient(self, request):
        request = int(request)
        export = []
        export.append(self.id)
        export.append(self.name[request])
        export.append(self.canvas[request])
        export.append(self.active[request])
        export.append(self.done[request])
        export.append(self.ready)
        export.append(self.players)
        
        return export

    def importGameAtClient(self, data, player, request):
        request = int(request)
        print("import: ", request)
        player = int(player)
        try:
            if request != player:
                self.id = data[0]
                self.name[request] = data[1]
                self.canvas[request] = data[2]
                self.active[request] = data[3]
                self.done[request] = data[4]
                self.ready = data[5]
                self.players = data[6]
        except:
            pass

    def exportGameToServer(self, player, request):
        request = int(request)
        print("export: ", request)
        player = int(player)
        export = []
        export.append(self.name[player])
        export.append(self.canvas[player])
        export.append(self.active[player])
        export.append(self.done[player])
        export.append(request)
        return export

    def importGameAtServer(self, data, player):
        player = int(player)
        self.name[player] = data[0]
        self.canvas[player] = data[1]
        self.active[player] = data[2]
        self.done[player] = data[3]

    def connected(self):
        return self.ready

    def bothActive(self):
        active = True
        for i in range(8):
            if self.active[i] == False:
                active = False
        return active
    
    def bothDone(self):
        done = True
        for i in range(8):
            if self.done[i] == False:
                done = False
        return done

    def resetActive(self):
        for i in range(8):
            self.active[i] = False