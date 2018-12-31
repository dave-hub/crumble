import pygame, sys, random, math, time
from pygame.locals import *


pygame.init()
pygame.mixer.init()
size = 900, 600
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
batList = []
batspawncount = random.randint(60, 300)
skelly = 0
sound = True

spookyfont = pygame.font.SysFont("Comic Sans MS", 24)
spookytext = spookyfont.render("2spooky4me", False, (255,255,255))

textfont = pygame.font.SysFont("Lucida Console", 16)
msgfont = pygame.font.SysFont("Lucida Console", 48)

sfx_bathit = pygame.mixer.Sound("audio/bat_hit.wav")
sfx_batterydrain = pygame.mixer.Sound("audio/battery_drain.wav")
sfx_crystalexplode = pygame.mixer.Sound("audio/crystal_explosion.wav")
sfx_crystalwarp = pygame.mixer.Sound("audio/crystal_warp.wav")
sfx_gunshot = pygame.mixer.Sound("audio/gunshot.wav")
sfx_skeleton = pygame.mixer.Sound("audio/skeleton.wav")
sfx_skeletonappear = pygame.mixer.Sound("audio/skeleton_appear.wav")
sfx_skeletonhit = pygame.mixer.Sound("audio/skeleton_hit.wav")
sfx_chest = pygame.mixer.Sound("audio/chest.wav")
music = pygame.mixer.Sound("audio/mus/crumble.wav")

music.play(loops=-1)


# cave object where everything that happens to the map takes place
class cave:
    def __init__(self):
        # generate the grid
        self.generate(1, 9)

    def generate(self, resx, resy):
        # create the grid (or reset it from previous grid) NOTE: Grid is not in similar dimensions to actual
        self.grid = [[cave.tile(1, 0, 0), 0, 0, 0, 0, 0, 0, 0, 0, cave.tile(3, 0, 9)],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [cave.tile(2, 14, 0), 0, 0, 0, 0, 0, 0, 0, 0, cave.tile(4, 14, 9)]]
        self.floorList = []
        self.rockList = []

        # chance of exit
        if random.randint(1, 4) == 3:
            side = random.randint(1, 4)
        else:
            side = 0
        self.side = side

        # generate top wall tiles
        for x in range(1, 14):
            self.grid[x][0] = cave.tile(5, x, 0)
        if side == 1:
            x = random.randint(1, 14)
            self.grid[x][0] = cave.tile(13, x, 0)
            self.exitx, self.exity = x, 0

        # generate bottom wall tiles
        for x in range(1, 14):
            self.grid[x][9] = cave.tile(6, x, 9)
        if side == 2:
            x = random.randint(1, 14)
            self.grid[x][9] = cave.tile(14, x, 9)
            self.exitx, self.exity = x, 9

        # generate left wall tiles
        for y in range(1, 9):
            self.grid[0][y] = cave.tile(7, 0, y)
        if side == 3:
            y = random.randint(1, 9)
            self.grid[0][y] = cave.tile(15, 0, y)
            self.exitx, self.exity =  0, y

        # generate right wall tiles
        for y in range(1, 9):
            self.grid[14][y] = cave.tile(8, 14, y)
        if side == 4:
            y = random.randint(1, 9)
            self.grid[14][y] = cave.tile(16, 14, y)
            self.exitx, self.exity = 14, y

        if not side == 0:
            print self.exitx, self.exity

        # generate a random amount of rocks in the grid
        rockCount = random.randint(10, 30)
        for i in range(0, rockCount):
            x = random.randint(1, 13)
            y = random.randint(1, 8)
            if x != 1 and y != 8:
                if self.grid[x][y] == 0:
                    self.grid[x][y] = cave.tile(10, x, y)

        # generate the rest of the blocks as the floor tiles
        for x in range(0, 14):
            for y in range(0, 9):
                if self.grid[x][y] == 0:
                    self.grid[x][y] = cave.tile(9, x, y)
                    self.floorList.append(self.grid[x][y])

        # set skeleton tiles
        skeletons = random.randint(2, 4)
        self.skeletonList = []
        for i in range(0, skeletons):
            self.skeletonList.append(random.choice(self.floorList))

        # set chest tile
        x = random.randint(1, 13)
        y = random.randint(1, 8)
        while x == resx and y == resy:
            x = random.randint(1, 13)
            y = random.randint(1, 8)
        self.grid[x][y] = cave.tile(12, x, y)
        self.chestx, self.chesty = x, y
        # set crystal tile
        x = random.randint(1, 13)
        y = random.randint(1, 8)
        while x == resx and y == resy or x == self.chestx or y == self.chesty:
            x = random.randint(1, 13)
            y = random.randint(1, 8)
        self.grid[x][y] = cave.tile(11, x, y)
        self.crystalx, self.crystaly = x, y

    def draw(self):
        for x in range(0, 15):
            for y in range(0, 10):
                self.grid[x][y].draw()
        self.grid[self.crystalx][self.crystaly].draw()

    # tile class where the tiles data is stored
    class tile:
        def __init__(self, type, gridx, gridy):
            self.type = type
            if type == 1:
                self.image = pygame.image.load("tiles/tlcorner.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 2:
                self.image = pygame.image.load("tiles/trcorner.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 3:
                self.image = pygame.image.load("tiles/blcorner.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 4:
                self.image = pygame.image.load("tiles/brcorner.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 5:
                self.image = pygame.image.load("tiles/topwall.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 6:
                self.image = pygame.image.load("tiles/bottomwall.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 7:
                self.image = pygame.image.load("tiles/leftwall.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 8:
                self.image = pygame.image.load("tiles/rightwall.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 9:
                self.image = pygame.image.load("tiles/floor.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 10:
                self.image = pygame.image.load("tiles/rock"+str(random.randint(1, 3))+".png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 11:
                self.image = pygame.image.load("tiles/crystal.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 12:
                self.image = pygame.image.load("tiles/chest.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 13:
                self.image = pygame.image.load("tiles/exitt.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 14:
                self.image = pygame.image.load("tiles/exitb.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 15:
                self.image = pygame.image.load("tiles/exitl.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60
            elif type == 16:
                self.image = pygame.image.load("tiles/exitr.png")
                self.rect = self.image.get_rect()
                self.rect.top, self.rect.left = gridy * 60, gridx * 60

        def draw(self):
            screen.blit(self.image, self.rect)


# player object where the player data and control happens
class player:
    def __init__(self):
        # holstered player images, 1 - up, 2 - down, 3 - left, 4 - right
        self.holstList = [pygame.image.load("players/playerup.png"), pygame.image.load("players/playerdown.png"),
                          pygame.image.load("players/playerleft.png"), pygame.image.load("players/playerright.png")]
        self.drawnList = [pygame.image.load("players/gunup.png"), pygame.image.load("players/gundown.png"),
                          pygame.image.load("players/gunleft.png"), pygame.image.load("players/gunright.png")]
        self.holstImg = self.holstList[0]
        self.drawnImg = self.drawnList[0]
        self.rect = self.holstImg.get_rect()
        self.rect.left, self.rect.top = 80, 490
        # movement variables
        self.mw = False
        self.ms = False
        self.ma = False
        self.md = False
        self.dr = 0
        self.playerspeed = 1
        # player stats
        self.health = 10
        self.healthgui = player.healthbar()
        self.batterylife = 6
        self.batterycounter = 3600
        self.batterygui = player.batterybar()
        self.bullets = random.randint(1, 3)
        self.bulletsfired = []
        self.ammocount = textfont.render("Ammo - "+str(self.bullets), False, (255, 255, 255))
        # torch vingettes
        self.vingetteList = []
        for i in range(0, 7):
            self.vingetteList.append(pygame.image.load("vingette/"+str(i)+".png"))
        self.vingetteImg =  self.vingetteList[self.batterylife]
        self.vingette = self.vingetteImg.get_rect()
        self.showFOW = True


    def collisioncheck(self):
        global skelly
        nocollidelist = [9, 12, 13, 14, 15, 16]
        for x in range(0, 15):
            for y in range(0, 10):
                if not gamemap.grid[x][y].type in nocollidelist:
                    if self.rect.colliderect(gamemap.grid[x][y].rect):
                        if self.mw:
                            self.rect.top += self.playerspeed
                        if self.ms:
                            self.rect.top -= self.playerspeed
                        if self.ma:
                            self.rect.left += self.playerspeed
                        if self.md:
                            self.rect.left -= self.playerspeed
                else:
                    if gamemap.grid[x][y] in gamemap.skeletonList and self.rect.colliderect(gamemap.grid[x][y].rect):
                        skelly = skeleton(gamemap.grid[x][y])
                        if sound:
                            sfx_skeletonappear.play()
                        gamemap.skeletonList.remove(gamemap.grid[x][y])
                    if x == gamemap.chestx and y == gamemap.chesty and self.rect.colliderect(gamemap.grid[x][y].rect):
                        if sound:
                            sfx_chest.play()
                        self.health += random.randint(1, 4)
                        if self.health > 10:
                            self.health = 10
                        self.bullets += random.randint(1, 5)
                        self.ammocount = textfont.render("Ammo - "+str(self.bullets), False, (255, 255, 255))
                        self.batterycounter += random.randint(120, 600)
                        if self.batterycounter > 3600:
                            self.batterycounter = 3600
                        gamemap.chestx, gamemap.chesty = -1, -1
                        gamemap.grid[x][y] = cave.tile(9, x, y)
                        gamemap.floorList.append(gamemap.grid[x][y])
                    if gamemap.side != 0:
                        if self.rect.colliderect(gamemap.grid[gamemap.exitx][gamemap.exity].rect):
                            time.sleep(1)
                            end("won")

        if self.health == 0:
            time.sleep(1)
            end("lost")


    # function to operate player movement
    def move(self):
        if self.mw:
            self.dr = 0
            self.rect.top -= self.playerspeed
        if self.ms:
            self.dr = 1
            self.rect.top += self.playerspeed
        if self.ma:
            self.dr = 2
            self.rect.left -= self.playerspeed
        if self.md:
            self.dr = 3
            self.rect.left += self.playerspeed

    def draw(self):
        # different image render scripts
        if len(self.bulletsfired) == 0:
            self.holstImg = self.holstList[self.dr]
            screen.blit(self.holstImg, self.rect)
        else:
            self.drawnImg = self.drawnList[self.dr]
            screen.blit(self.drawnImg, self.rect)
        for i in range(0, len(self.bulletsfired)):
            self.bulletsfired[i].draw()
        # rendering torch vingette
        if self.showFOW:
            self.vingetteImg = self.vingetteList[self.batterylife]
            self.vingette.top = self.rect.top-(559/2) - 600
            self.vingette.left = self.rect.left-(879/2) - 900
            screen.blit(self.vingetteImg, self.vingette)
        self.healthgui.draw()
        self.batterygui.draw()
        screen.blit(self.ammocount, (810, 575))

    def shoot(self, mousex, mousey):
        if not self.bullets == 0:
            if sound:
                sfx_gunshot.play()
            self.bullets -= 1
            self.ammocount = textfont.render("Ammo - "+str(self.bullets), False, (255, 255, 255))
            cy = self.rect.top + 20
            cx = self.rect.left + 10
            # if in top right quadrant
            if mousex > cx and mousey < cy:
                # if right
                if mousex - cx >= cy - mousey:
                    dr = 3
                    self.dr = 3
                # if up
                elif mousex - cx <= cy - mousey:
                    dr = 1
                    self.dr = 0
            # if in bottom right quadrant
            elif mousex > cx and mousey > cy:
                # if right
                if mousex - cx >= mousey - cy:
                    dr = 3
                    self.dr = 3
                # if down
                elif mousex - cx <= mousey - cy:
                    dr = 2
                    self.dr = 1
            # if top left quadrant
            elif mousex < cx and mousey < cy:
                # if left
                if cx - mousex >= cy - mousey:
                    dr = 4
                    self.dr = 2
                # if up
                elif cx - mousex <= cy - mousey:
                    dr = 1
                    self.dr = 0
            # if bottom left quadrant
            elif mousex < cx and mousey > cy:
                # if left
                if cx - mousex >= mousey - cy:
                    dr = 4
                    self.dr = 2
                # if down
                elif cx - mousex <= mousey - cy:
                    dr = 2
                    self.dr = 1
            else:
                print "dr error"
                dr = 4
            self.bulletsfired.append(player.bullet(dr, self.rect.top, self.rect.left))


    class healthbar:
        def __init__(self):
            self.image = pygame.image.load("players/heart.png")
            self.rects = []
            for i in range(0, 10):
                self.rects.append(self.image.get_rect())
            for i in range(0, len(self.rects)):
                self.rects[i].top, self.rects[i].left = 10, 10 + (26 * i)

        def draw(self):
            for i in range(0, p1.health):
                screen.blit(self.image, self.rects[i])

    class batterybar:
        def __init__(self):
            self.image = pygame.image.load("players/battery.png")
            self.rects = []
            for i in range(0, 5):
                self.rects.append(self.image.get_rect())
            for i in range(0, len(self.rects)):
                self.rects[i].top, self.rects[i].left = 7, 869 - (26 * i)

        def draw(self):
            for i in range(0, p1.batterylife - 1):
                screen.blit(self.image, self.rects[i])

    class bullet:
        def __init__(self, direction, top, left):
            self.image = pygame.image.load("players/bullet"+str(direction)+".png")
            self.rect = self.image.get_rect()
            self.rect.top = top + 19
            self.rect.left = left + 9
            if direction == 1:
                self.topvect = -8
                self.leftvect = 0
            elif direction == 2:
                self.topvect = 8
                self.leftvect = 0
            elif direction == 3:
                self.leftvect = 8
                self.topvect = 0
            elif direction == 4:
                self.leftvect = -8
                self.topvect = 0
            self.running = True

        def update(self):
            if self.running:
                self.rect.top += self.topvect
                self.rect.left += self.leftvect
                if self.rect.top < 0 or self.rect.top > 600:
                    self.running = False
                elif self.rect.left < 0 or self.rect.left > 900:
                    self.running = False
                if skelly != 0:
                    if skelly.alive and self.rect.colliderect(skelly.rect):
                        if sound:
                            sfx_skeletonhit.play()
                        skelly.alive = False
                        self.running = False
                if self.rect.colliderect(gamemap.grid[gamemap.crystalx][gamemap.crystaly].rect):
                    self.running = False
                    transform()


        def draw(self):
            screen.blit(self.image, self.rect)


# bat mob class
class bat:
    def __init__(self):
        self.image = pygame.image.load("mob/bat.png")
        self.rect = self.image.get_rect()
        self.top = random.randint(60, 440)
        self.rect.top = self.top
        self.dr = random.randint(0, 1)
        self.alive = True
        # dr 0 is going left, dr 1 is going right
        if self.dr == 0:
            self.rect.left = 900
            self.vect = -random.randint(2, 5)
        else:
            self.rect.left = -22
            self.vect = -random.randint(2, 5)

    def update(self):
        if self.alive:
            if self.rect.colliderect(p1.rect):
                self.alive = False
                if sound:
                    sfx_bathit.play()
                p1.health -= random.randint(1, 3)
                while p1.health < 0:
                    p1.health += 1
            if math.floor(self.rect.left/50) % 2 == 0:
                self.rect.top = self.top + 5
            else:
                self.rect.top = self.top - 5
            self.rect.left += self.vect

    def draw(self):
        screen.blit(self.image, self.rect)


# skeleton mob class
class skeleton:
    def __init__(self, tile):
        self.image = pygame.image.load("mob/skeleton.png")
        self.rect = self.image.get_rect()
        self.rect.top, self.rect.left = tile.rect.top + 4, tile.rect.left + 19
        self.tile = tile
        self.alive = True
        self.spookychance = random.randint(0, 20)
        hitChance = random.randint(1, 5)
        if hitChance == 1:
            self.attacktime = 0
        else:
            self.attacktime = random.randint(5, 30)
        self.timedelay = 60
        self.attacked = False

    def update(self):
        if self.attacktime == 0:
            if self.attacked == False:
                if sound:
                    sfx_skeleton.play()
                p1.health -= random.randint(2, 5)
                while p1.health < 0:
                    p1.health += 1
                self.attacked = True
            if self.timedelay == 0:
                self.alive = False
            else:
                self.timedelay -= 1

        else:
            self.attacktime -= 1

    def draw(self):
        screen.blit(self.image, self.rect)
        if self.spookychance == 1:
            screen.blit(spookytext, (250, 250))


# crystal map transformation
def transform():
    p1.rect.top = gamemap.grid[gamemap.crystalx][gamemap.crystaly].rect.top + 10
    p1.rect.left = gamemap.grid[gamemap.crystalx][gamemap.crystaly].rect.left + 20
    gamemap.generate(gamemap.crystalx, gamemap.crystaly)

    msg1 = msgfont.render("Oh no...", False, (255, 255, 255))
    msg2 = msgfont.render("The cave is shaking...", False, (255, 255, 255))

    if sound:
        sfx_crystalexplode.play()

    # init variable resets
    p1.health += random.randint(1, 5)
    if p1.health > 10:
        p1.health = 10
    p1.batterylife = 6
    p1.batterycounter += random.randint(0, 300)
    if p1.batterycounter > 3600:
        p1.batterycounter = 3600
    p1.bullets += random.randint(1, 3)
    p1.bulletsfired = []
    p1.ammocount = textfont.render("Ammo - "+str(p1.bullets), False, (255, 255, 255))

    t = 360
    while t > 0:
        if t == 300:
            if sound:
                sfx_crystalwarp.play()
        screen.fill((0, 0, 0))
        if 180 < t < 300:
            screen.blit(msg1, (142, 132))
        if 0 < t < 180:
            screen.blit(msg2, (26, 450))
        pygame.display.update()
        clock.tick(60)

        t -= 1


# introduction procedure
def intro():
    global gamemap, p1
    gamemap = cave()
    p1 = player()

    msg1 = msgfont.render("You are trapped", False, (255, 255, 255))
    msg2 = msgfont.render("With limited supplies", False, (255, 255, 255))
    msg3 = msgfont.render("You must escape...", False, (255, 255, 255))

    t = 420
    while t > 0:
        screen.fill((0, 0, 0))
        if 420 > t > 300:
            screen.blit(msg1, (80, 60))
        if 300 > t > 180:
            screen.blit(msg2, (40, 221))
        if 180 > t > 60:
            screen.blit(msg3, (90, 447))
        pygame.display.update()
        clock.tick(60)

        t -= 1


# info procedure
def info():
    bgimg = pygame.image.load("title/howto.png")
    bg = bgimg.get_rect()

    backbutton = pygame.Rect(6, 20, 72, 70)

    while True:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    if backbutton.collidepoint(x, y):
                        MENU()
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(bgimg, bg)
        pygame.display.update()
        clock.tick(60)


# win message
def end(outcome):
    if outcome == "lost":
        msg = msgfont.render("You have failed...", False, (255, 255, 255))
    else:
        msg = msgfont.render("You escaped! Good Job.", False, (255, 255, 255))

    screen.fill((0, 0, 0))
    screen.blit(msg, (45, 246))
    pygame.display.update()
    time.sleep(2)
    sys.exit()


# game function, where main game process takes place
def GAME():
    global batspawncount

    while True:

        # event handling
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_w:
                    p1.mw = True
                elif event.key == K_s:
                    p1.ms = True
                elif event.key == K_a:
                    p1.ma = True
                elif event.key == K_d:
                    p1.md = True
            if event.type == KEYUP:
                if event.key == K_w:
                    p1.mw = False
                if event.key == K_s:
                    p1.ms = False
                if event.key == K_a:
                    p1.ma = False
                if event.key == K_d:
                    p1.md = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    if p1.bullets > 0:
                        p1.shoot(x, y)
            if event.type == pygame.QUIT:
                sys.exit()

        # game processes

        # player movement
        p1.move()
        p1.collisioncheck()
        # battery sound
        soundtrigger = [0, 600, 1200, 1800, 2400, 3000]
        if p1.batterycounter in soundtrigger:
            if sound:
                sfx_batterydrain.play()
        # player battery
        if p1.batterylife != 0:
            if p1.batterycounter == 0:
                p1.batterylife = 0
            elif 600 > p1.batterycounter > 0:
                p1.batterylife = 1
            elif 1200 > p1.batterycounter > 600:
                p1.batterylife = 2
            elif 1800 > p1.batterycounter > 1200:
                p1.batterylife = 3
            elif 2400 > p1.batterycounter > 1800:
                p1.batterylife = 4
            elif 3000 > p1.batterycounter > 2400:
                p1.batterylife = 5
            elif 3600 > p1.batterycounter > 3000:
                p1.batterylife = 6
            p1.batterycounter -= 1
        # player shooting
        for i in range(0, len(p1.bulletsfired)):
            p1.bulletsfired[i].update()
        # delete inactive bullets
        for i in range(0, len(p1.bulletsfired)):
            if p1.bulletsfired[i].running == False:
                p1.bulletsfired.remove(p1.bulletsfired[i])
                break

        # skeleton
        if skelly != 0:
            if skelly.alive:
                skelly.update()

        # check bat spawn
        if batspawncount == 0:
            batList.append(bat())
            batspawncount = random.randint(60, 300)
        else:
            batspawncount -= 1
        # move bats
        for i in range(0, len(batList)):
            batList[i].update()
        # delete bats
        for i in range(0, len(batList)):
            if batList[i].alive == False:
                batList.remove(batList[i])
                break

        # rendering
        gamemap.draw()
        if skelly != 0:
            if skelly.alive:
                skelly.draw()
        for i in range(0, len(batList)):
            batList[i].draw()
        p1.draw()
        pygame.display.update()
        clock.tick(60)


# menu procedure
def MENU():
    global sound
    bgimg = pygame.image.load("title/menu.png")
    bg = bgimg.get_rect()

    audiobuttonimgs = [pygame.image.load("title/audiooff.png"), pygame.image.load("title/audioon.png")]
    audio = 1
    audiobutton = audiobuttonimgs[audio].get_rect()
    audiobutton.left = 800


    playbutton = pygame.Rect(353, 353, 209, 72)
    infobutton = pygame.Rect(27, 499, 70, 75)

    while True:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    if playbutton.collidepoint(x, y):
                        intro()
                        GAME()
                    if infobutton.collidepoint(x, y):
                        info()
                    if audiobutton.collidepoint(x, y):
                        if audio == 1:
                            audio = 0
                            sound = False
                            pygame.mixer.pause()
                        else:
                            audio = 1
                            sound = True
                            pygame.mixer.unpause()
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(bgimg, bg)
        screen.blit(audiobuttonimgs[audio], audiobutton)
        pygame.display.update()
        clock.tick(60)

# create the cave instance and player instance
MENU()