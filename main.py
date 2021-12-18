import math,os
import pygame,sys,math,copy,json,random,os
import numpy as np

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
WHITE   =  (255, 255, 255)
ORANGE  =  (255, 127, 0  )
YELLOW  =  (255, 255, 0  )
BLACK   =  (0,   0,   0  )
BLUE    =  (0,   0,   255)
RED     =  (255, 0,   0  )
SKYBLUE =  (135, 206, 235)
SLIVER  =  (192, 192, 192)
GRASS_GREEN = (106,133,24)

SPEED_INC = 3
SPEED_LIM = 15

XY = 0
XZ = 1
YZ = 2

class PVector:
    def __init__(self,x,y) -> None:
        self.x = x
        self.y = y
    
    def __add__(self,other):
        x,y = self.x + other.x , self.y + other.y
        return PVector(x,y)

    def __sub__(self,other):
        x,y = self.x - other.x , self.y - other.y
        return PVector(x,y)
    
    def __repr__(self) -> str:
        return str((self.x,self.y))
    
    def convert(self):
        theta = math.atan2(self.y,self.x) * 180 / math.pi
        value = math.sqrt(self.x**2 + self.y**2)
        return Vector(theta,value)

class Vector:
    def __init__(self,theta,value) -> None:
        self.theta = theta
        self.value = value
    
    def __add__(self,other):
        S = self.convert()
        O = other.convert()
        return (S+O).convert()
    
    def __sub__(self,other):
        S = self.convert()
        O = other.convert()
        return (S-O).convert()
    
    def __repr__(self) -> str:
        return str((self.theta,self.value))
    
    def convert(self):
        x = math.cos(math.radians(self.theta)) * self.value
        y = math.sin(math.radians(self.theta)) * self.value
        return PVector(x,y)

class Drone:
    def __init__(self,x,y,z,degree) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.degree = degree
        self.backMode = False
        self.speed = Vector(self.degree, 0)
        self.moveHistory = [Vector(0, 0),0]
    
    def draw(self,screen,D = XY):
        if D == XY:
            degreeSign = 40 * self.z / 500
            pygame.draw.line(screen,ORANGE,[self.x + SCREEN_WIDTH/2,self.y + SCREEN_HEIGHT/2],[self.x + SCREEN_WIDTH/2 + math.cos(math.radians(self.degree)) * degreeSign,self.y + SCREEN_HEIGHT/2 + math.sin(math.radians(self.degree)) * degreeSign],2)
            size = 20 * self.z / 500
            pygame.draw.rect(screen,BLUE,pygame.Rect(self.x + SCREEN_WIDTH/2 - size/2,self.y + SCREEN_HEIGHT/2 - size/2,size,size))
            pygame.draw.rect(screen,ORANGE,pygame.Rect(self.x + SCREEN_WIDTH/2 - size/4,self.y + SCREEN_HEIGHT/2- size/4,size/2,size/2))
        elif D == XZ:
            size = 40 * (250 + self.y) / 500
            pygame.draw.rect(screen,BLUE,pygame.Rect(self.x + SCREEN_WIDTH/2 - size/2, 500 - self.z - size/4, size, size/2))
        elif D == YZ:
            size = 40 * (250 + self.x) / 500
            pygame.draw.rect(screen,BLUE,pygame.Rect(self.y + SCREEN_WIDTH/2 - size/2, 500 - self.z - size/4, size, size/2))


    def keyboard(self):
        global mode
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_SPACE]:
            self.backMode = True
            self.goBack()
        if pressed_keys[pygame.K_UP]:
            self.speed += Vector(self.degree, 3)
            self.moveHistory[0] += Vector(self.degree, 3)
        elif pressed_keys[pygame.K_DOWN]:
            self.speed -= Vector(self.degree, 3)
            self.moveHistory[0] -= Vector(self.degree, 3)
        self.x += self.speed.convert().x
        self.y += self.speed.convert().y
        self.speed = Vector(self.degree, 0)

        if pressed_keys[pygame.K_LEFT]:
            self.degree -= 5
        elif pressed_keys[pygame.K_RIGHT]:
            self.degree += 5
        if pressed_keys[pygame.K_z] and self.z >= 5:
            self.z -= 5
            self.moveHistory[1] -= 5
        elif pressed_keys[pygame.K_x] and self.z <= 500 - 5:
            self.z += 5
            self.moveHistory[1] += 5
        if pressed_keys[pygame.K_1] :
            mode = XY
        elif pressed_keys[pygame.K_2] :
            mode = XZ
        elif pressed_keys[pygame.K_3] :
            mode = YZ
        self.z = max(0,self.z)
        self.z = min(500,self.z)    
    def goBack(self):
        pV = self.moveHistory[0].convert()
        r = math.sqrt(pV.x ** 2 + pV.y ** 2 + self.moveHistory[1] **2)
        degree = math.atan2(self.moveHistory[1], pV.y)
        print(degree)
        step = r/SPEED_INC
        if step >= 1:
            move = copy.copy(self.moveHistory[0])
            move.value = SPEED_INC
            if self.moveHistory[0].value >= SPEED_INC:
                pV = move.convert()
                self.x -= pV.x
                self.y -= pV.y
                self.moveHistory[0] -= Vector(self.moveHistory[0].theta, SPEED_INC)
            else:
                move = Vector(self.moveHistory[0].theta,- self.moveHistory[0].value)
                pV = move.convert()
                self.x += pV.x
                self.y += pV.y
                self.moveHistory[0] = Vector(self.moveHistory[0].theta, 0)
            if abs(self.moveHistory[1]) >= 5 * math.sin(degree):
                self.moveHistory[1] -= 5 * math.sin(degree)
                self.z -= 5 * math.sin(degree)
            else:
                self.z -= self.moveHistory[1]
                self.moveHistory[1] = 0
        else:
            move = Vector(self.moveHistory[0].theta,self.moveHistory[0].value)
            pV = move.convert()
            self.x -= pV.x
            self.y -= pV.y
            self.backMode = False
            self.moveHistory[0] = Vector(self.degree,0)
            self.z += self.moveHistory[1]
            self.moveHistory[1] = 0

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("심화수학 드론 띄우기")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    drone = Drone(0,0,200,0)
    mode = XY

    clock = pygame.time.Clock()
    while True:
        clock.tick(120)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(SKYBLUE)
        #pygame.draw.circle(screen,YELLOW,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2),7)
        #print(drone.degree,drone.speed)
        drone.draw(screen,mode)
        pV = drone.moveHistory[0].convert()
        print("오차 : ",(pV.x - drone.x,pV.y - drone.y, drone.moveHistory[1] - drone.z + 200))
        if drone.backMode:
            drone.goBack()
            print(drone.x, drone.y, drone.z)
        else:
            drone.keyboard()
        #print((drone.x,drone.y,drone.z),(loc,drone.moveHistory[1]))
        if mode == XY:
            loc = drone.moveHistory[0].convert()
            pygame.draw.line(screen,RED,[SCREEN_WIDTH/2 + drone.x, SCREEN_HEIGHT/2 + drone.y],[SCREEN_WIDTH/2 + drone.x - loc.x,SCREEN_HEIGHT/2 + drone.y - loc.y])
        elif mode == XZ:
            loc = drone.moveHistory[0].convert()
            #degree = math.atan2(drone.moveHistory[1], loc)
            loc2 = drone.moveHistory[1]
            pygame.draw.line(screen,RED,[SCREEN_WIDTH/2 + drone.x, SCREEN_HEIGHT - drone.z],[SCREEN_WIDTH/2 + drone.x - loc.x, SCREEN_HEIGHT - drone.z + loc2])
        elif mode == YZ:
            loc = drone.moveHistory[0].convert()
            #degree = math.atan2(drone.moveHistory[1], loc)
            loc2 = drone.moveHistory[1]
            pygame.draw.line(screen,RED,[SCREEN_WIDTH/2 + drone.y, SCREEN_HEIGHT - drone.z],[SCREEN_WIDTH/2 + drone.y - loc.y, SCREEN_HEIGHT - drone.z + loc2])
        pygame.display.update()
