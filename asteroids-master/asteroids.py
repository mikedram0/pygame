import sys
import pygame
import time
import math
import random
import time


pygame.init()

width = 1280
height = 720
#size = width, height = 1600, 900
black = 0, 0, 0
white = 255, 255, 255

#screen = pygame.display.set_mode((width,height), pygame.FULLSCREEN)
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

sysfont = pygame.font.SysFont(None , 40)
text = sysfont.render("Health = "+str(100),True,(255,255,255))

pew=pygame.mixer.Sound("pew.wav")
lasersound=pygame.mixer.Sound("lasersound.wav")
breaksound = pygame.mixer.Sound("break.wav")
thrustsound = pygame.mixer.Sound("thrust.wav")
pygame.mixer.music.load('beat.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.pre_init(44100,-16,1, 1024)
#pygame.mixer.music.set_volume(0.03)
laser_img=pygame.image.load("laser.png")
ship1 = pygame.image.load("starship.png")
ship2 = pygame.image.load("starship2.png")

#ship1 = pygame.transform.scale(ship1,(50,50))
#ship2 = pygame.transform.scale(ship2,(70,70))


bullet_img = pygame.image.load("bullet.png")
asteroid_small = pygame.image.load("small.png")
asteroid_medium = pygame.image.load("medium.png")
asteroid_large = pygame.image.load("large.png")
ammobox1 = pygame.image.load("ammo.png")
ammobox2 = pygame.image.load("laser_ammo_image.png")
healthpack = pygame.image.load("health_pck_img.png")
#space = pygame.image.load("space.png")

astersize = {1:asteroid_small,2:asteroid_medium,3:asteroid_large}
ammoboximage = {1:ammobox1 , 2:ammobox2 , 3:healthpack }
bulletimage=  {1:bullet_img,2:laser_img}


diff=1
FPS=60
DEBUG = False
bullets=[]
asteroids_list=[]
consumables_list=[]
textlist = []

start_time = time.time()


class Player:

	def __init__(self,x,y):
		self.x = x 
		self.y = y
		self.vx = 0
		self.vy = 0
		self.ax = 0
		self.ay = 0
		self.health = 100
		self.normalammo = 20
		self.laserammo = 10
		self.image = ship1
		self.angle = 0
		self.anglev = 0
		self.rect = self.image.get_rect()
		self.thrust = False
		self.score = 0
		self.lose = False
		self.limx = 30
		self.limy = 30
		self.time = 0

	def move(self):

		if self.thrust:
			self.ax = math.sin(self.angle*3.1415/180 +3.1415) * 0.1
			self.ay = math.cos(self.angle*3.1415/180+3.1415) * 0.1
		else:
			self.ax = 0
			self.ay = 0

		self.vx += self.ax
		self.vy += self.ay

		
		if abs(self.vx) >self.limx or abs(self.vy)>self.limy:
			if self.vx > self.limx: self.vx = self.limx
			if self.vx <-self.limx: self.vx = -self.limx
			if self.vy > self.limy: self.vy = self.limy
			if self.vy <-self.limy: self.vy = -self.limy




		self.x += self.vx
		self.y += self.vy

		self.angle += self.anglev

		if self.angle >= 360:
			self.angle -= (self.angle%360)*360

		if self.x-self.rect.width/2>width:
			self.x = 0 - self.rect.width/2
		if self.x+ self.rect.width/2<0:
			self.x = width + self.rect.width/2
		if self.y - self.rect.height/2>height:
			self.y = 0 - self.rect.height/2
		if self.y + self.rect.height/2<0:
			self.y = height + self.rect.height/2


	def healthcheck(self):

		if self.health > 100 : self.health = 100
		if self.health <= 0 : 
			gamereset()

	def draw(self):
		self.newimage=pygame.transform.rotate(self.image,player1.angle)
		self.rect = self.newimage.get_rect()
		self.rect.center = (self.x,self.y)
		screen.blit(self.newimage,self.rect)
		if DEBUG: pygame.draw.rect(screen,white,self.rect,3)









class Text:

	def __init__(self):
		textlist.append(self)

	def set_text(self,text,font,color):
		self.text = font.render(text,True,color)

	def draw(self,x,y):
		screen.blit(self.text,(x,y))		




class Consumables:

	def __init__(self,x,y,ammotype):
		self.x = x
		self.y = y
		self.type = ammotype 
		self.image = ammoboximage[self.type]
		self.bbox = self.image.get_rect()

	def collisiondetect(self):
		if self.bbox.colliderect(player1.rect):
			if self.type == 1:
				player1.normalammo += 10
				consumables_list.remove(self)
			if self.type == 2:
				player1.laserammo += 5
				consumables_list.remove(self)
			if self.type == 3 and player1.health < 100: 
				player1.health += 20
				consumables_list.remove(self)


	def draw(self):
		self.bbox.center = (self.x,self.y)
		screen.blit(self.image, self.bbox)
		if DEBUG: pygame.draw.rect(screen,white,self.bbox,3)



class asteroid:
	def __init__(self,x,y,vx,vy,size):
		self.aposx=x
		self.aposy=y
		self.avx=vx
		self.avy=vy
		
		self.size = size
		self.image = astersize[self.size]

		self.bbox = self.image.get_rect()
		self.bbox.center = (self.aposx,self.aposy)

	def collisiondetect(self):
		global health
		for bullet in bullets:
			if self.bbox.colliderect(bullet.bbox):
				player1.score+=10*self.size
				asteroids_list.remove(self)
				pygame.mixer.Sound.play(breaksound)
				bullets.remove(bullet)
				if self.size > 1 and bullet.type == 1:
					velx = random.choice([-1,1])
					vely = random.choice([-1,1])
					asteroids_list.append(asteroid(self.aposx,self.aposy,velx,vely,self.size-1))
					asteroids_list.append(asteroid(self.aposx,self.aposy,-velx,-vely,self.size-1))
		if self.bbox.colliderect(player1.rect):
			player1.health -= self.size*10
			try:
				asteroids_list.remove(self)
			except:
				pass
			pygame.mixer.Sound.play(breaksound)

	def move(self):
		self.aposx=self.aposx+self.avx
		self.aposy=self.aposy+self.avy
		
		if self.aposx-self.bbox.width/2>width:
			self.aposx = 0 - self.bbox.width/2
		if self.aposx+ self.bbox.width/2<0:
			self.aposx = width + self.bbox.width/2
		if self.aposy - self.bbox.height/2>height:
			self.aposy = 0 - self.bbox.height/2
		if self.aposy + self.bbox.height/2<0:
			self.aposy = height + self.bbox.height/2
		
	def draw(self):
		self.bbox.center = (self.aposx,self.aposy)
		screen.blit(self.image, self.bbox)
		if DEBUG: pygame.draw.rect(screen,white,self.bbox,3)



class Bullet:
	def __init__(self,bposx,bposy,typee,angle):

		self.angle=player1.angle
		self.bposx=bposx
		self.bposy=bposy
		self.bvx=math.sin(player1.angle*3.1415/180 +3.1415) 
		self.bvy=math.cos(player1.angle*3.1415/180+3.1415)
		self.type = typee # Type of Bullet , 1 is a normal bullet , 2 is a laser
		self.image = bulletimage[self.type]
		self.bbox = self.image.get_rect()
		if self.type == 1: player1.normalammo -= 1
		if self.type == 2: player1.laserammo -= 1


	   

	def checkdelete(self):
		if self.bposx >width or self.bposx<0 or self.bposy > height or self.bposy < 0:
			bullets.remove(self)

	def draw(self):
		
		
		if self.type==1:
			self.bbox = self.image.get_rect()
			self.bbox.center = (self.bposx,self.bposy)
			screen.blit(self.image,self.bbox)
			if DEBUG: pygame.draw.rect(screen,white,self.bbox,3)

		if self.type==2:
			self.new_l=pygame.transform.rotate(laser_img,self.angle)
			self.bbox = self.new_l.get_rect()
			self.bbox.center = (self.bposx,self.bposy)
			screen.blit(self.new_l,self.bbox)
			if DEBUG: pygame.draw.rect(screen,white,self.bbox,3)
		
	def move(self):
		self.bposx=self.bposx+self.bvx*20
		self.bposy=self.bposy+self.bvy*20



def spawn():
	global DEBUG,diff
	player1.score=player1.score*2
	#consumables_list=[]
	for i in range(3*diff):
		asteroids_list.append(asteroid(random.randint(0,width),random.randint(0,height),random.randint(-1,1),random.randint(-1,1),random.randint(1,3)   ))

	for i in range(5):
		consumables_list.append(Consumables(random.randint(0,width),random.randint(0,height),1))#normal ammo

	for i in range(1):
		consumables_list.append(Consumables(random.randint(0,width),random.randint(0,height),2))#laser

	for i in range(3):
		consumables_list.append(Consumables(random.randint(0,width),random.randint(0,height),3))#health


helathtext = Text()
ammo1text = Text()
ammo2text = Text()
DEBUGtext = Text()
scoretext=Text()

player1=Player(width/2,height/2)


def main():

	global DEBUG,diff,consumables_list
	if asteroids_list==[]:
		diff=diff+1
		consumables_list=[]
		spawn()
	
	player1.time = time.time() - start_time
	#print(time)

	for event in pygame.event.get():
		if event.type == pygame.QUIT: 
			sys.exit()
		if event.type == pygame.KEYDOWN:
			
			if event.key==pygame.K_ESCAPE:
				sys.exit()

			if event.key==pygame.K_RETURN:
				DEBUG = not DEBUG

			if event.key==pygame.K_a:
				player1.anglev=player1.anglev+4

			if event.key==pygame.K_SPACE:
				if player1.normalammo > 0:
					bullets.append(Bullet(player1.x,player1.y,1,player1.angle))
					pygame.mixer.Sound.play(pew)
					#print("piew")

			if event.key==pygame.K_LSHIFT:
				if player1.laserammo > 0:
					bullets.append(Bullet(player1.x,player1.y,2,player1.angle))
					pygame.mixer.Sound.play(lasersound)
				#print("piew")

			if event.key==pygame.K_d:
				player1.anglev=player1.anglev-4


			if event.key == pygame.K_w:
				player1.image = ship2
				player1.thrust = True
				pygame.mixer.Sound.play(thrustsound,-1)

				
		if event.type  == pygame.KEYUP:

			if event.key == pygame.K_a:
				player1.anglev = 0

			if event.key == pygame.K_d:
				player1.anglev = 0

			if event.key == pygame.K_w:
				player1.image = ship1
				player1.thrust = False
				pygame.mixer.Sound.stop(thrustsound)




	player1.healthcheck()
	clock.tick(FPS)
	screen.fill(black)
	player1.move()
	player1.draw()

	#screen.blit(space,(0,0,width,height))

	for aster in asteroids_list:
		aster.collisiondetect()
		aster.move()
		aster.draw()

	for bullet in bullets:
		bullet.checkdelete()
		if bullets.count(bullet):
			bullet.move()
			bullet.draw()

	for consumable in consumables_list:
		consumable.collisiondetect()
		consumable.draw()

	helathtext.set_text("Health: "+str(player1.health),sysfont,white) 
	DEBUGtext.set_text("x: "+str(int(player1.x))+" y: "+str(int(player1.y))+" FPS: "+str(int(clock.get_fps()))+" vx: "+str(int(player1.vx))+" vy: "+str(int(player1.vy))+" time: "+str(int(player1.time)),sysfont,white) 
	ammo1text.set_text("Bullets: "+str(player1.normalammo),sysfont,white) 
	ammo2text.set_text("Lasers: "+str(player1.laserammo),sysfont,white) 
	scoretext.set_text("Score: "+str(player1.score)+" Level: "+str(diff),sysfont,white)

	helathtext.draw(width/100,10) 
	ammo1text.draw(width/100,40) 
	ammo2text.draw(width/100,70) 
	scoretext.draw(width/100,100)
	if DEBUG: DEBUGtext.draw(width/100,130)
	pygame.display.update()


def gamereset():
	global consumables_list,player1,diff
	diff=1
	bullets=[]
	asteroids_list=[]
	consumables_list=[]
	textlist = []
	del player1
	player1=Player(width/2,height/2)
	print(player1.score)


spawn()
while 1:
	main()

pygame.quit()
quit()