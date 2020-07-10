class Canvas():
    def __init__(self, id, res):
        self.id = id
        self.res = res
        self.pixels = self.pixel_grid()

    def pixel_grid(self):
        pixels = []
        for n in range(self.res):
            pixels.append([0] * self.res)
        return pixels

    def drawRect(self, x1, y1, x2, y2, fill):
        if fill:
            for i in range(x1, x2):
                for j in range(y1, y2):
                    self.pixels[j][i] = 1
        else:
            for i in range(x1, x2):
                self.pixels[y1][i] = 1
                self.pixels[y2-1][i] = 1
            for i in range(y1+1, y2-1):
                self.pixels[i][x1] = 1
                self.pixels[i][x2-1] = 1 

    def sendCanvas(self):
        return self.pixels

    def recvCanvas(self, pixelData):
        self.pixels = pixelData

    def __str__(self):
        printer = ''
        for n in range(self.res):
            print_row = ''
            for m in range(self.res):
                print_row += str(self.pixels[n][m]) + ' '
            printer += print_row + '\n'
        return printer

