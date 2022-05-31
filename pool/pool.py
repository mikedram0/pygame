import pygame
import sys
import math
import random
import numpy as np

res = (1338,760)
width,height = res

pygame.init()
screen = pygame.display.set_mode(res)
clock = pygame.time.Clock()
FPS = 60

ball_list = []
bound_list = []
text_list = []

class Text:

	def __init__(self,pos,color,fontsize):
		text_list.append(self)
		self.pos = pos
		self.color = color
		self.fontsize = fontsize
		self.font = pygame.font.SysFont(None , self.fontsize)

	def size(self):
		return pygame.font.Font.size(self.font, "Test")
		
	def draw(self, text ):
		self.text = self.font.render(text,True,self.color,"BLACK")
		screen.blit(self.text,self.pos)

fps = Text((0,0),"WHITE",30)
#_ , fps_height = fps.size() 
cursorpos = Text((0,fps.size()[1]),"WHITE",30)

class Boundary:

	def __init__(self, startx, starty, endx, endy, orientation):
		
		self.orientation = orientation
		self.startx,self.starty = startx,starty
		self.endx,self.endy = endx,endy
		'''
		if self.startx > self.endx:
			self.startx,self.endx = self.endx,self.startx
		if self.starty > self.endy:
			self.starty,self.endy = self.endy,self.starty
		'''
		self.length = math.sqrt((endx-startx)**2 + (endy-starty)**2)
		self.normx = (endy-starty)/self.length
		self.normy = -(endx - startx)/self.length
		self.norm = np.array([self.normx,self.normy])
		self.tan = np.array([-self.normy,self.normx])
		bound_list.append(self)

	def draw(self):
		pygame.draw.line(screen,"WHITE",(self.startx,self.starty),(self.endx,self.endy ),3)
		#pygame.draw.line(screen,"WHITE",((self.startx+self.endx)/2,(self.starty+self.endy)/2),(10*self.normx+(self.startx+self.endx)/2,10*self.normy+(self.starty+self.endy)/2),2)


bound1 = Boundary(0.1562*width,0.2461*height,0.1562*width,0.7539*height,"v")
bound2 = Boundary(0.1831*width,0.1987*height,0.4798*width,0.1987*height,"h")
bound = Boundary(0.5*width,0.5*height,0.5*width+200,0.5*height+200,"d")
bound3 = Boundary(0.1562*width,0.2461*height,0.1263*width,0.1961*height,"d")
bound4 = Boundary(0.1831*width,0.1987*height,0.1517*width,0.1474*height,"d")
bound5 = Boundary(0.4798*width,0.1987*height,0.4843*width,0.1711*height,"d")
bound5 = Boundary(0.4843*width,0.1711*height,0.4843*width,0.1329*height,"v")




class Ball:

	def __init__(self,pos,shape,color):
		#self.x,self.y = pos
		#self.vx,self.vy = 0.0,0.0
		self.pos = np.array(pos,dtype = "float")
		self.vel = np.array([0.0,0.0])
		self.shape = shape
		self.color = color
		self.radius = width/80
		

	def move(self):

		drag = 1
		#self.vx *= drag
		#self.vy *= drag
		self.vel *= drag

		min_speed = 0.05

		#if self.vx**2 + self.vx**2 <= min_speed: self.vx , self.vy = 0,0
		if np.dot(self.vel,self.vel) <= min_speed: self.vel = [0,0]
	
		#self.x += self.vx
		#self.y += self.vy
		self.pos += self.vel

	def collision_check(self):
		
		
		energy_loss = 0.8

		if self.pos[0]  > width - self.radius:
			self.pos[0] = width - self.radius 
			self.vel[0] *= -energy_loss
		if self.pos[0] < self.radius:
			self.pos[0] = self.radius
			self.vel[0] *= -energy_loss
		if self.pos[1] > height - self.radius:
			self.pos[1] = height - self.radius
			self.vel[1] *= -energy_loss
		if self.pos[1] < self.radius:
			self.pos[1] = self.radius
			self.vel[1] *= -energy_loss
		
		
		
		vel_line = np.cross( np.hstack( (self.pos , np.ones(1) ) )  ,  np.hstack( (self.vel,np.zeros(1)) )   )
		#print(vel_line)

		for bound in bound_list:
			s = np.vstack([(bound.startx,bound.starty),(bound.endx,bound.endy)])        # s for stacked
			h = np.hstack((s, np.ones((2, 1)))) # h for homogeneous
			l1 = np.cross(h[0], h[1])   
			x, y, z = np.cross(l1, vel_line)
			if z != 0 :
				x, y = x/z , y/z
				#print(x,y) 
				if bound.orientation == "v":
					if (y >= bound.starty and y <= bound.endy) or (y <= bound.starty and y >= bound.endy):
						poi = np.array([x,y])
						vec = poi - self.pos
						dist = np.dot(vec,vec)
						if dist <= self.radius**2:
							self.vel[0] *= -1
					
				elif bound.orientation == "h":
					if (x >= bound.startx and x <= bound.endx) or (x >= bound.startx and x <= bound.endx):
						poi = np.array([x,y])
						vec = poi - self.pos
						dist = np.dot(vec,vec)
						if dist <= self.radius**2:
							self.vel[1] *= -1
				elif bound.orientation == "d":
					if ((x >= bound.startx and x <= bound.endx) or (x <= bound.startx and x >= bound.endx))  and ((y >= bound.starty and y <= bound.endy) or (y <= bound.starty and y >= bound.endy)):
						poi = np.array([x,y])
						vec =  self.pos - poi 
						vec_proj = (self.pos + self.vel) - poi
						dist = np.linalg.norm(vec)
						#dist_proj = np.linalg.norm(vec_proj)
						#vnorm = np.linalg.norm(self.vel)
						if  (dist <= self.radius or np.dot(vec ,vec_proj ) < 0) :
							self.pos = poi + vec*self.radius/dist
							#self.vel = np.array([0,0])
							vtan = np.dot(self.vel,bound.tan)
							vnorm = np.dot(self.vel,bound.norm)

							vnorm *= -1 

							self.vel = vtan * bound.tan + vnorm* bound.norm
				#pygame.draw.circle(screen,"WHITE",(x,y),3)

	
	def ball_collision(self):

		for circle in ball_list:
			if circle == self:
				continue
			dist = np.linalg.norm(circle.pos-self.pos)
			if dist <= self.radius + circle.radius:

				overlap = self.radius + circle.radius - dist

				#Calculating the normal vector and normalizing it

				n = (circle.pos - self.pos)/dist
				

				#Calculating the tangential vector 
				t = np.array([n[1],-1*n[0]])


				#Displacing the balls along the parallel axis in case of overlap

				self.pos -= n * overlap/2
				circle.pos += n * overlap/2

				# Here I will use the collison "coordinates" , by breaking the velocity into a tangential and parralell part


				#Calculating the tangential component of velocity , which are not affected by the collision
				vtan1 = np.dot(self.vel,t)
				vtan2 = np.dot(circle.vel,t)

				#vtan1 = self.vx*tx +self.vy*ty
				#vtan2 = circle.vx*tx + circle.vy*ty

				#Calculating the parralell velocity before the colision
				vpar1b = np.dot(self.vel,n)
				vpar2b = np.dot(circle.vel,n)
		

				#vpar1b = self.vx * nx + self.vy * ny
				#vpar2b = circle.vx * nx + circle.vy * ny


				#Calculating the parallell velocities after the collision , using the elastic collision formula

				vpar1a = vpar2b
				vpar2a = vpar1b


				#Setting the velocities

				self.vel = vtan1 * t + n * vpar1a
				#self.vx = (vtan1*tx + nx * vpar1a)
				#self.vy = (vtan1*ty + ny * vpar1a)

				circle.vel = vtan2 * t + n * vpar2a
				#circle.vx = (vtan2*tx + nx * vpar2a)
				#circle.vy = (vtan2*ty + ny * vpar2a)


	def draw(self):
		
		self.ball = pygame.draw.circle(screen,self.color,(self.pos[0],self.pos[1]),self.radius,width = shapes_to_width[self.shape] )
		

class Pool_cue():

	def __init__(self,color):
		self.color = color
		self.playing = True

	def draw(self):
		if self.playing:
		
			mouse_pos = np.array(pygame.mouse.get_pos())

			vec = mouse_pos - game.white.pos

			length = np.linalg.norm(vec)
			
			vec /= length
			
			pygame.draw.line(screen,self.color,(game.white.pos[0]+vec[0]*2*r,game.white.pos[1]+vec[1]*2*r),(game.white.pos[0]+vec[0]*150,game.white.pos[1]+vec[1]*150),3)

			minimum = 1000
			for ball in ball_list:
				if ball is game.white: continue

				u = ball.pos - game.white.pos
				r2 = np.dot(u,u)
				dist = np.dot(u,vec)

				d2 = r2 - dist**2
		
				if d2 <= r**2 and dist < 0:
					dist = abs(dist)
					if dist < minimum: minimum = dist
			
			pygame.draw.line(screen,"WHITE",(game.white.pos[0]-vec[0]*2*r,game.white.pos[1]-vec[1]*2*r),(game.white.pos[0]-vec[0]*minimum , game.white.pos[1]-vec[1]*minimum ),3)

			



	def click(self,mouse,mousehit):
		if self.playing:
			mouse_pos = np.asarray(mouse)
			mousehit_pos = np.asarray(mousehit)
			vec = mouse_pos - game.white.pos
			#vecx = (mousex - game.white.x)
			#vecy = (mousey - game.white.y)

			length = np.linalg.norm(vec)
			
			vec /= length

			accel = 0.5*abs(100-100*mousehit_pos[1]/height)

			game.white.vel = -vec*accel
			

r = width/80
r3 = math.sqrt(3)
colors = {1:"YELLOW",2:"BLUE",3:"PINK",4:"PURPLE",5:"ORANGE",6:"GREEN",7:"RED",9:"YELLOW",10:"BLUE",11:"PINK",12:"PURPLE",13:"ORANGE",14:"GREEN",15:"RED"}
pos = {1:(0,0),2:(r3*r,-r),3:(2*r3*r,-2*r),4:(3*r3*r,-3*r),5:(4*r3*r,4*r),6:(4*r3*r,-2*r),7:(3*r3*r,r),9:(r3*r,r),10:(2*r3*r,2*r),11:(3*r3*r,3*r),12:(4*r3*r,-4*r),13:(4*r3*r,2*r),14:(3*r3*r,-r),15:(4*r3*r,0)}                             
shapes_to_width = {"solid":0,"white":0,"black":0,"striped":5}
class Game:

	def __init__(self):
		self.white = Ball((width*0.3,height*0.5),shape = "white", color = "WHITE")
		self.black = Ball((width*0.6+2*r3*r,height*0.5),shape = "black", color = "BLACK")
		ball_list.append(self.white)
		ball_list.append(self.black)
		'''		
		for i in range(1,16):
			if i == 8 : continue
			if i <= 7 : shape = "solid" 
			elif i >= 9 : shape = "striped"
			ball_list.append(Ball( (0.6*width+pos[i][0],0.5*height+pos[i][1]),shape,colors[i]))
		'''

game = Game()

cue = Pool_cue("Blue")

def event_handeler():
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT: 
			sys.exit()
		if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
			game.white.pos = np.asarray(pygame.mouse.get_pos(),dtype = "float")
			game.white.vel = np.array([0.0,0.0], dtype ="float")
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			cue.playing = False
			global mouse 
			mouse = pygame.mouse.get_pos()
		if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
			mousehit = pygame.mouse.get_pos()
			cue.playing = True
			cue.click(mouse,mousehit)

bg = pygame.image.load("pool_table.png").convert()
bg = pygame.transform.scale(bg, (int(width*0.8), int(height*0.8)))
#bg = pygame.transform.laplacian(bg)
rect = bg.get_rect()
rect.center = (width/2,height/2)



while 1:
	
	event_handeler()

	clock.tick(60)
	screen.fill((0,0,0))
	screen.blit(bg, rect)
	

	mouse = pygame.mouse.get_pos()
	fps.draw("FPS: "+str(int(clock.get_fps())))
	cursorpos.draw(f"x:{mouse[0]*100/width:.2f} y:{mouse[1]*100/height:.2f}")


	
	for bound in bound_list:
		bound.draw()

	

	for ball in ball_list:
		ball.collision_check()
		ball.ball_collision()
		ball.move()
		ball.draw()
		
		cue.draw()

	pygame.display.update()










	 