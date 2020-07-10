import pygame
from network import Network
from game import Game
import random
import copy
import pickle
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

pygame.font.init()

width = 1280
height = 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

class Button:
    def __init__(self, image, x, y):
        self.image = pygame.image.load("images/" + image)
        self.x = x
        self.y = y
        self.width, self.height = self.image.get_size()

    def draw(self, screen):
        screen.blit(self.image, (self.x , self.y))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False

class Region:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False

def redrawCanvas(screen, game, p, colors):
    res = 80
    x = 320
    y = 40
    canvas = pygame.Surface((640, 640))
    pygame.draw.rect(canvas, (255, 255, 255), (0, 0, 640, 640))

    for i in range(res):
        for j in range(res):
            color = colors[game.canvas[int(p)][i][j]]
            pygame.draw.rect(canvas, color, (i * 8, j * 8, 8, 8))
    screen.blit(canvas, (x, y))

def redrawReveal(screen, game, colors):
    res = 80
    x = 0
    y = 0
    canvas = pygame.Surface((1280, 640))
    pygame.draw.rect(canvas, (255, 255, 255), (0, 0, 1280, 640))
    canvas_coords = [(0,0), (320, 0), (640, 0), (960, 0), (0, 320), (320, 320), (640, 320), (960, 320)]
    for n in range(8):
        xx = canvas_coords[n][0]
        yy = canvas_coords[n][1]
        for i in range(res):
            for j in range(res):
                color = colors[game.canvas[n][i][j]]
                pygame.draw.rect(canvas, color, (i * 4 + xx, j * 4 + yy, 4, 4))
    screen.blit(canvas, (x, y))

def redrawscreendow(screen, game, p, game_start_timer):

    if not(game.connected()):
        font = pygame.font.Font("fonts/gotham_bold.otf", 36)
        font2 = pygame.font.Font("fonts/gotham_bold.otf", 12)
        text = font.render("Waiting for " + str(8 - game.players) + " more players", 1, (3, 65, 77), True)
        text2 = font2.render("(you can doodle while you wait but it will be reset once the game starts)", 1, (3, 65, 77), True)
        screen.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
        screen.blit(text2, (width/2 - text2.get_width()/2, height/2 + 40 - text.get_height()/2))
    elif game_start_timer < 60:
        font = pygame.font.Font("fonts/gotham_bold.otf", 50)
        text = font.render("Draw!", 1, (3, 65, 77))
        screen.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
        game_start_timer += 1
    else:
        pass
    return game_start_timer

cursor_crosshair = pygame.image.load("images/cursor_crosshair.png")
cursor_hand = pygame.image.load("images/cursor_hand.png")

def main(player_name):
    run = True
    clock = pygame.time.Clock()
    n = Network()
    game = Game(0)
    game_state = 0 # 0 = drawing 1 = reveal

    player = n.getP()
    player_relative = int(player) % 8
    game.name[player_relative] = player_name

    print("You are player: ", player)
    timer = 0 
    delay = 5 # Delay in frames (30 fps) to communicate with server
    game_start_timer = 0

    draw_bg = pygame.image.load("images/bg_draw.png")
    reveal_bg = pygame.image.load("images/bg_reveal.png")
    waiting_bg = pygame.image.load("images/bg_waiting.png")
    btn_done = Button("btn_done.png", 1012, 644)
    img_selector = pygame.image.load("images/selector.png")
    name_font = pygame.font.Font("fonts/gotham_bold.otf", 28)

    icon_checkmark = pygame.image.load("images/icon_checkmark.png")

    btn_play_again = Button("btn_play_again.png", 744, 644)
    btn_main_menu = Button("btn_main_menu.png", 1012, 644)

    navigator_coords = [(11, 235), (75, 235), (139, 235), (203, 235), (11, 299), (75, 299), (139, 299), (203, 299)]
    tool_coords = [(11, 375), (75, 375), (139, 375), (203, 375)]
    tool_selected = 0
    tool_radius = 1

    canvas_region = Region(320, 40, 640, 640)

    tool_regions = []
    tool_regions.append(Region(12, 376, 64, 64))
    tool_regions.append(Region(76, 376, 64, 64))
    tool_regions.append(Region(140, 376, 64, 64))
    tool_regions.append(Region(204, 376, 64, 64))

    color_coords = []
    color_coords.append((11, 451))
    color_coords.append((75, 451))
    color_coords.append((139, 451)) 
    color_coords.append((203, 451))
    color_coords.append((11, 515))
    color_coords.append((75, 515))
    color_coords.append((139, 515))
    color_coords.append((203, 515))
    color_coords.append((11, 579))
    color_coords.append((75, 579))
    color_coords.append((139, 579))
    color_coords.append((203, 579))
    color_coords.append((11, 643)) 
    color_coords.append((75, 643)) 
    color_coords.append((139, 643))
    color_coords.append((203, 643))
    color_selected = 3

    color_regions = []
    color_regions.append(Region(12, 452, 64, 64))
    color_regions.append(Region(76, 452, 64, 64))
    color_regions.append(Region(140, 452, 64, 64))
    color_regions.append(Region(204, 452, 64, 64))
    color_regions.append(Region(12, 516, 64, 64))
    color_regions.append(Region(76, 516, 64, 64))
    color_regions.append(Region(140, 516, 64, 64))
    color_regions.append(Region(204, 516, 64, 64))
    color_regions.append(Region(12, 580, 64, 64))
    color_regions.append(Region(76, 580, 64, 64))
    color_regions.append(Region(140, 580, 64, 64))
    color_regions.append(Region(204, 580, 64, 64))
    color_regions.append(Region(12, 644, 64, 64))
    color_regions.append(Region(76, 644, 64, 64))
    color_regions.append(Region(140, 644, 64, 64))
    color_regions.append(Region(204, 644, 64, 64))

    colors = []
    colors.append((255, 255, 255)) # White
    colors.append((190, 190, 190)) # Light Grey
    colors.append((128, 128, 128)) # Dark Grey
    colors.append((64, 64, 64)) # Black
    colors.append((247, 247, 47)) # Yellow
    colors.append((247, 130, 47)) # Orange
    colors.append((237, 26, 61)) # Red
    colors.append((241, 118, 166)) # Pink
    colors.append((137, 204, 70)) # Light Green
    colors.append((35, 146, 74)) # Dark Green
    colors.append((143, 90, 52)) # Brown
    colors.append((227, 177, 140)) # Skin Tone
    colors.append((69, 221, 187)) # Turqoise
    colors.append((69, 166, 215)) # Light Blue
    colors.append((30, 89, 207)) # Dark Blue
    colors.append((146, 66, 220)) # Purple

    request = 0 #player ID for server request

    mousedown = False

    rect_start = (0, 0)
    rect_end = (0, 0)

    reveal_status = 0

    undo_saves = []
    redo_save = []

    while run:
        clock.tick(60)
        timer += 1
        pos = pygame.mouse.get_pos()

        if game.connected() and game_start_timer == 1:
            game.canvas[player_relative] = game.emptyCanvas()

        if timer == delay:
            data = game.exportGameToServer(player_relative, request)
            #print('data: ', data)
            try:    
                answer = n.send(data)
            except:
                run = False
                print("Couldn't send data to server")
                break
            #print('answer: ', answer)
            game.importGameAtClient(answer, player_relative, request)
            request += 1
            if request == 8:
                request = 0
            timer = 0

        if game_state == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        tool_radius += 1
                        if tool_radius > 20:
                            tool_radius = 20
                    if event.button == 5:
                        tool_radius -= 1
                        if tool_radius < 1:
                            tool_radius = 1
                    if event.button == 1:
                        if canvas_region.click(pos):
                            undo_step = copy.deepcopy(game.canvas[int(player)])
                            undo_saves.append(undo_step)
                            if len(undo_saves) > 100:
                                undo_saves.pop(0)
                            redo_saves = []
                        mousedown = True
                        posx = pos[0]
                        posy = pos[1]
                        if posx < 320:
                            posx = 320
                        if posx > 960:
                            posx = 960
                        if posy < 40:
                            posy = 40
                        if posy > 680:
                            posy = 680
                        rect_start = (posx, posy)
                        if btn_done.click(pos):
                            game.done[player_relative] = True
                            game_state = 1
                        color_cycle = 0
                        for region in color_regions:
                            if region.click(pos):
                                color_selected = color_cycle
                            color_cycle += 1
                        tool_cycle = 0
                        for region in tool_regions:
                            if region.click(pos):
                                tool_selected = tool_cycle
                            tool_cycle += 1
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mousedown = False
                        if canvas_region.click(pos) and tool_selected == 1:
                            x1 = ((min(rect_start[0], rect_end[0]) - 320) // 8)
                            y1 = ((min(rect_start[1], rect_end[1]) - 40) // 8)
                            x2 = ((max(rect_start[0], rect_end[0]) - 321) // 8)
                            y2 = ((max(rect_start[1], rect_end[1]) - 41) // 8)
                            for i in range(80):
                                for j in range(80):
                                    if i == x1 or i == x2:
                                        if j >= y1 and j <= y2:
                                            game.canvas[int(player)][i][j] = color_selected
                                    if i > x1 and i < x2:
                                        if j == y1 or j == y2:
                                            game.canvas[int(player)][i][j] = color_selected
                        if canvas_region.click(pos) and tool_selected == 2:
                            #draw circle on canvas
                            pass
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] and keys[pygame.K_LCTRL] and keys[pygame.K_z] and len(redo_saves) > 0:
                        undo_step = copy.deepcopy(game.canvas[int(player)])
                        undo_saves.append(undo_step)
                        print("Redo")
                        game.canvas[int(player)] = redo_saves.pop()
                    elif keys[pygame.K_LCTRL] and keys[pygame.K_z] and len(undo_saves) > 0:
                        redo_step = copy.deepcopy(game.canvas[int(player)])
                        redo_saves.append(redo_step)
                        print("Undo")
                        game.canvas[int(player)] = undo_saves.pop()
                    if keys[pygame.K_LCTRL] and keys[pygame.K_y] and len(redo_saves) > 0:
                        undo_step = copy.deepcopy(game.canvas[int(player)])
                        undo_saves.append(undo_step)
                        print("Redo")
                        game.canvas[int(player)] = redo_saves.pop()

            screen.blit(draw_bg, (0, 0))

            name_text = []
            for i in range(8):
                name_text.append(name_font.render(game.name[i], True, (3, 65, 77)))
            
            for i in range(8):
                screen.blit(name_text[i], (1020, 48 + (30 * i)))
                if game.done[i] == True:
                    screen.blit(icon_checkmark, (1020 + name_text[i].get_width() + 6, 52 + (30 * i)))

            screen.blit(img_selector, navigator_coords[player_relative])
            screen.blit(img_selector, tool_coords[tool_selected])
            screen.blit(img_selector, color_coords[color_selected])
            btn_done.draw(screen)

            redrawCanvas(screen, game, player, colors)
            game_start_timer = redrawscreendow(screen, game, player, game_start_timer)

            if tool_selected == 0:
                if canvas_region.click(pos):
                    x, y = pos
                    x = ((x - 321) // 8)
                    y = (y - 41) // 8
                    offset = 0.7
                    for i in range(-tool_radius, tool_radius + 1):
                        for j in range(-tool_radius, tool_radius + 1):
                            if (max(x + i, x) - min(x + i, x)) ** 2 + (max(y + j, y) - min(y + j, y)) ** 2 < (tool_radius - offset) ** 2:
                                if x + i < 80 and x + i > -1 and y + j < 80 and y + j > -1:
                                    pygame.draw.rect(screen, colors[color_selected], ((x + i) * 8 + 320, (y + j) * 8 + 40, 8, 8))

            if mousedown:
                if tool_selected == 0:
                    if canvas_region.click(pos):
                        x, y = pos
                        x = ((x - 321) // 8)
                        y = (y - 41) // 8
                        offset = 0.7
                        for i in range(-tool_radius, tool_radius + 1):
                            for j in range(-tool_radius, tool_radius + 1):
                                if (max(x + i, x) - min(x + i, x)) ** 2 + (max(y + j, y) - min(y + j, y)) ** 2 < (tool_radius - offset) ** 2:
                                    if x + i < 80 and x + i > -1 and y + j < 80 and y + j > -1:
                                        game.canvas[int(player)][x + i][y + j] = color_selected
                    else:
                        pass
                elif tool_selected == 1:
                    if canvas_region.click(pos):
                        rect_end = pos
                        x1 = ((min(rect_start[0], rect_end[0]) - 320) // 8) * 8
                        y1 = ((min(rect_start[1], rect_end[1]) - 40) // 8) * 8
                        x2 = ((max(rect_start[0], rect_end[0]) - 313 - x1) // 8) * 8
                        y2 = ((max(rect_start[1], rect_end[1]) - 33 - y1) // 8) * 8
                        for i in range(8):
                            pygame.draw.rect(screen, colors[color_selected], (320 + x1 + i, 40 + y1 + i, x2 - 2 * i, y2 - 2 * i), 1)
                    else:
                        pass
                elif tool_selected == 2:
                    if canvas_region.click(pos):
                        #draw realtime temp circle
                        x1 = ((min(rect_start[0], rect_end[0]) - 320) // 8)
                        y1 = ((min(rect_start[1], rect_end[1]) - 40) // 8)
                        x2 = ((max(rect_start[0], rect_end[0]) - 313 - x1) // 8)
                        y2 = ((max(rect_start[1], rect_end[1]) - 33 - y1) // 8)
                    else:
                        pass
                else:
                    pass

        if game_state == 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if btn_main_menu.click(pos):
                            run = False
                        if btn_play_again.click(pos):
                            pass

            if game.bothDone():
                screen.blit(reveal_bg, (0, 0))
                redrawReveal(screen, game, colors)
                btn_play_again.draw(screen)
            else:
                screen.blit(waiting_bg, (0, 0))
                font = pygame.font.Font("fonts/gotham_bold.otf", 36)
                text = font.render("Waiting for other players to finish their drawings", 1, (3, 65, 77))
                screen.blit(text, ((width - 290)/2 - text.get_width()/2, height/2 - text.get_height()/2))
                name_text = []
                for i in range(8):
                    name_text.append(name_font.render(game.name[i], True, (3, 65, 77)))
                for i in range(8):
                    screen.blit(name_text[i], (1020, 48 + (30 * i)))
                    if game.done[i] == True:
                        screen.blit(icon_checkmark, (1020 + name_text[i].get_width() + 6, 52 + (30 * i)))
            
            btn_main_menu.draw(screen)


        fps = name_font.render(str(int(clock.get_fps())), True, (0, 0, 0))
        screen.blit(fps, (10, 10))

        #mouse cursor stuff
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
        mouse_x, mouse_y = pos
        if canvas_region.click(pos) and game_state == 0:
            if tool_selected == 1 or tool_selected == 2:
                screen.blit(cursor_crosshair, (mouse_x - 16, mouse_y - 16))
        else:
            screen.blit(cursor_hand, (mouse_x - 10, mouse_y - 2))

        pygame.display.update()


def menu_screen():
    run = True
    clock = pygame.time.Clock()
    
    label_font = pygame.font.Font("fonts/gotham_light.otf", 40)
    field_font = pygame.font.Font("fonts/gotham_bold.otf", 60)
    name_label_text = "Name:"
    name_field_text = ""
    roomcode_label_text = "Enter Room Code:"
    roomcode_field_text = ""
    cursor = "|"
    cursor_timer = 0

    menu_bg = pygame.image.load("images/bg_menu.png")

    btn_play = Button("btn_play.png", 512, 600)
    btn_join_public = Button("btn_join_public_game.png", 232, 600)
    btn_create_private = Button("btn_create_private_game.png", 512, 600)
    btn_join_private = Button("btn_join_private_game.png", 792, 600)

    current_menu = "main"
    private_game = 0

    while run:
        pos = pygame.mouse.get_pos()
        clock.tick(60)
        cursor_timer += 1
        if cursor_timer == 80:
            cursor_timer = 0
        if cursor_timer >= 40:
            cursor = ""
        else:
            cursor = "|"
        screen.fill((128, 128, 128))

        screen.blit(menu_bg, (0, 0))

        if current_menu == "main":
            name_label = label_font.render(name_label_text, True, (3, 65, 77))
            name_surface = field_font.render(name_field_text + cursor, True, (3, 65, 77))
            screen.blit(name_label, (330, 414))
            screen.blit(name_surface, (330, 468))
            btn_join_public.draw(screen)
            btn_create_private.draw(screen)
            btn_join_private.draw(screen)
        
        if current_menu == "join_private":
            roomcode_label = label_font.render(name_label_text, True, (3, 65, 77))
            roomcode_surface = field_font.render(name_field_text + cursor, True, (3, 65, 77))
            screen.blit(roomcode_label, (330, 414))
            screen.blit(roomcode_surface, (330, 468))
            btn_play.draw(screen)

        #mouse cursor stuff
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
        mouse_x, mouse_y = pos
        screen.blit(cursor_hand, (mouse_x - 10, mouse_y - 2))

        pygame.display.update()

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if current_menu == "main":
                    if btn_join_public.click(pos) and name_field_text != "":
                        run = False
                    if btn_create_private.click(pos) and name_field_text != "":
                        private_game = 1
                        run = False
                    if btn_join_private.click(pos) and name_field_text != "":
                        private_game = 2
                        current_menu = "join_private"
                if current_menu == "join_private":
                    if btn_play.click(pos) and name_field_text != "":
                        run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name_field_text != "":
                    run = False
                elif event.key == pygame.K_BACKSPACE:
                    name_field_text = name_field_text[0:-1]
                elif event.key != pygame.K_RETURN:
                    if len(name_field_text) < 16:
                        name_field_text += event.unicode
            
    main(name_field_text)

while True:
    menu_screen()