import pygame, math, random
from global_ import Global
from levels import levels, tile_size, screen_height, screen_width
from UI import victory_scene, pause_scene, game_over_scene

# Initialize
pygame.init()

class Game:
	def __init__(self):
		
		# Load Level
		starting_level = 1
		self.level = Level(levels[starting_level])
		Global.level = self.level
		Global.cur_level = starting_level
		
		# All Scenes
		self.victory_scene = victory_scene.Screen(screen)
		self.pause_scene = pause_scene.Screen(screen)
		self.game_over_scene = game_over_scene.Screen(screen)

	def run(self):
		state = Global.state
		self.level = Global.level
		if state == "playing":
			self.level.run()
		elif state == "victory":
			self.victory_scene.run()
		elif state == "pause":
			self.pause_scene.run()
		elif state == "game_over":
			self.game_over_scene.run()

class Level:
	def __init__(self, level):
		
		# Setup
		self.level = level
		self.level_data = level["level_data"]
		self.won = False
		self.strokes_remains = level["strokes"]

		# Background
		self.background = pygame.sprite.Group()

		# Ball and hole
		self.ball = pygame.sprite.GroupSingle()
		self.hole = pygame.sprite.GroupSingle()

		# Obstacles
		self.obstacles = pygame.sprite.Group()
		
		# Create_level
		self.create_level()

	def change_level(self, level):
		self.__init__(levels[level])

	def create_level(self):
		for key, data in self.level_data.items():
			for row_index, row in enumerate(data):
				for col_index, cell in enumerate(row):
					x = col_index * tile_size
					y = row_index * tile_size
					if key == "background":
						self.background.add(Tile((x, y), cell))
					if key == "obstacle":
						if cell != "-1":
							self.obstacles.add(Obstacle((x, y)))
					if key == "ball_hole":
						if cell == "0":
							self.ball_start_pos_x = x
							self.ball_start_pos_y = y
							self.ball.add(Ball((x, y), self.strokes_remains))
						elif cell == "2":
							self.hole.add(Hole((x, y)))

	def collisions(self):
		ball = self.ball.sprite
		for sprite in self.obstacles.sprites():
			if sprite.rect.colliderect(ball.rect):
				if abs(ball.rect.right - sprite.rect.left) <= 40 and ball.vel.x > 0:
					ball.vel.x *= -1
					if not ball.shooting:
						swing_sound.play()
				if abs(ball.rect.left - sprite.rect.right) <= 40 and ball.vel.x < 0:
					ball.vel.x *= -1
					if not ball.shooting:
						swing_sound.play()
				if abs(ball.rect.bottom - sprite.rect.top) <= 40 and ball.vel.y > 0:
					ball.vel.y *= -1
					if not ball.shooting:
						swing_sound.play()
				if abs(ball.rect.top - sprite.rect.bottom) <= 40 and ball.vel.y < 0:
					ball.vel.y *= -1
					if not ball.shooting:
						swing_sound.play()

	def move_to_hole_center(self):
		self.ball.sprite.vel = pygame.math.Vector2(0, 0)
		self.ball.sprite.rect.center = self.hole.sprite.rect.center

	def shrink_ball(self, factor):
		ball = self.ball.sprite
		scale = ball.image.get_size() - pygame.math.Vector2(factor, factor)
		scale = (int(scale.x), int(scale.y))
		if scale[0] > 0 and scale[1] > 0:
			ball.image = pygame.transform.smoothscale(ball.image, scale)
			ball.rect = ball.image.get_rect(center=ball.rect.center)
		else:
			self.background.draw(screen)
			Global.state = "victory"

	def check_win(self):
		if pygame.sprite.collide_circle(self.ball.sprite, self.hole.sprite):
			self.move_to_hole_center()
			if self.won == False:
				self.won = True
				hole_sound.play()

	def check_loose(self):
		if self.strokes_remains <= 0 and not self.won:
			self.background.draw(screen)
			Global.state = "game_over"

	def restart(self):
		self.strokes_remains = self.level["strokes"]
		self.ball.sprite.kill()
		self.ball.add(Ball((self.ball_start_pos_x, self.ball_start_pos_y), self.strokes_remains))
		self.won = False

	def input(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]:
			self.background.draw(screen)
			Global.state = "pause"

	def show_strokes(self):
		text = f"Strokes left - {self.strokes_remains}"
		show_text(screen, text, (20, 20), 50, "black")

	def run(self):
		
		# Background
		self.background.draw(screen)

		# Obstcales
		self.obstacles.update()
		self.obstacles.draw(screen)

		# Hole
		self.hole.draw(screen)

		# Ball
		self.ball.update()
		self.ball.draw(screen)

		# Collisions
		self.collisions()

		# Strokes
		self.strokes_remains = self.ball.sprite.strokes_remains
		self.show_strokes()

		# Win and loose
		self.check_win()
		if self.won:
			self.shrink_ball(0.1)
		self.check_loose()	

		# Get_States
		self.input()

class Ball(pygame.sprite.Sprite):
	def __init__(self, pos, strokes_remains):
		super().__init__()
		
		# Basic Setup
		self.display_surface = pygame.display.get_surface()
		self.image = pygame.image.load("../assets/ball.png").convert_alpha()
		offset = pygame.math.Vector2(tile_size/2, tile_size/2)
		self.rect = self.image.get_rect(center=pos+offset)
		self.radius = 20 	  # For Collision Detection with Hole
		
		# Necessary Variables
		self.shooting = False # Gets Set to True if mouse is dragging from ball position only
		self.fired = False # Gets Set to True when user releases mouse button
		self.strokes_remains = strokes_remains
		self.vel = pygame.math.Vector2(0, 0)  # Initial Velocity Of Ball since ball will not move initially
		self.move_to = pygame.math.Vector2(self.rect.center)  # This is the vector towards which we have to move, initially we don't have to move

		# Arrow And Power Rect
		self.arrow = pygame.image.load("../assets/arrow.png")
		self.power_rect_offset = pygame.math.Vector2(45, 0)
		self.power_rect = pygame.Rect(self.rect.center+self.power_rect_offset, (20, 100))

	def aim(self):

		# Direction
		self.ball_position = pygame.math.Vector2(self.rect.center)           	# Current ball position
		self.current_mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos()) 	# Current mouse position
		self.move_to = self.ball_position - self.current_mouse_pos			 	# set move_to to the difference of both 
		
		# Velocity
		self.vel = self.move_to.normalize() * (ball_speed * self.move_to.magnitude()/40)
		if self.vel.magnitude() > max_speed:
			self.vel.scale_to_length(max_speed)
		
		# Arrow 
		self.angle = (180/math.pi) * math.atan2(-self.move_to.x, -self.move_to.y)  # Calculate angle in degrees
		self.rotated_arrow = pygame.transform.rotozoom(self.arrow, self.angle, 1)
		self.rotated_arrow_rect = self.rotated_arrow.get_rect(center=self.rect.center)
		self.draw_arrow()

		# Power Rect
		power_rect_fill_size = 20, self.get_power_rect_height(self.vel.magnitude())
		self.power_rect_fill = pygame.Rect(self.power_rect.bottomleft, power_rect_fill_size)
		self.power_rect_color = self.get_power_rect_color(self.power_rect_fill.size[1])
		self.draw_power_rect()

	def draw_arrow(self):
		self.display_surface.blit(self.rotated_arrow, self.rotated_arrow_rect)
	
	def get_power_rect_height(self, vel_magnitude):
		ratio = 100/max_speed
		return -ratio * vel_magnitude
	
	def get_power_rect_color(self, rect_height):
		if abs(rect_height) <= 50:
			return "green"
		elif abs(rect_height) > 50 and abs(rect_height) <= 80:
			return "orange"
		else:
			return "red"	

	def draw_power_rect(self):
		# Actual Power Level
		pygame.draw.rect(self.display_surface, self.power_rect_color, self.power_rect_fill, border_radius=5)

		# Border
		pygame.draw.rect(self.display_surface, (0, 0, 0), self.power_rect, width=2, border_radius=5)

	def shoot(self):
		self.rect.center += self.vel # move the ball with given velocity

	def apply_friction(self):
		if self.vel.length() != 0:
			self.vel.scale_to_length(self.vel.length() - friction)  # Scale the length of velcity vector to decrease each time to eventually stop it.
		if self.vel.length() <= 0.4:					   		# If velocity decrease too much like 0.5 then we will set fired = False
			self.vel = pygame.math.Vector2(0, 0)
			self.fired = False
			self.strokes_remains -= 1

	def boundary(self):
		if self.rect.left < 0:
			self.rect.left = 0
			self.vel.x *= -1
			swing_sound.play()
		elif self.rect.right > screen_width:
			self.rect.right = screen_width
			self.vel.x *= -1
			swing_sound.play()
		if self.rect.top < 0:
			self.rect.top = 0
			self.vel.y *= -1
			swing_sound.play()
		elif self.rect.bottom > screen_height:
			self.rect.bottom = screen_height
			self.vel.y *= -1
			swing_sound.play()	

	def get_mouse_input(self):
		left_click = pygame.mouse.get_pressed()[0]
		cur_mouse_pos = pygame.mouse.get_pos()
		if left_click:
			if self.rect.collidepoint(cur_mouse_pos):
				self.shooting = True
			elif not self.shooting:
				self.shooting = False
		else:
			if self.shooting:
				self.fired = True
				self.shooting = False
				charge_sound.play()

	def update(self):
		self.arrow_rect = self.arrow.get_rect(midbottom=(self.rect.center))
		self.power_rect.center = self.rect.center + self.power_rect_offset
		self.get_mouse_input()
		
		if self.shooting: 	# If shooting then aim towards the location to move
			self.aim()  	# This method will find the location and set move_to vector as well as velocity.
		
		if self.fired:   			# If ball is fired then move the ball towards move_to vector 
			self.shoot() 			# This method will move the ball with velocity set in aim() method
			self.apply_friction()	# Apply Friction to eventually stop the ball. 

		self.boundary()	 # This method will check for boundaries.		

class Obstacle(pygame.sprite.Sprite):
	def __init__(self, pos):
		super().__init__()
		self.image = pygame.Surface((64, 64)).convert_alpha()
		self.color = random.choice(["brown", "green", "green"])
		self.image.fill(self.color)
		self.rect = self.image.get_rect(topleft=pos)

	def update(self):
		pygame.draw.rect(pygame.display.get_surface(), (0, 0, 0), self.rect, width=10)

class Hole(pygame.sprite.Sprite):
	def __init__(self, pos):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.image = pygame.image.load("../assets/hole.png").convert_alpha()
		offset = pygame.math.Vector2(tile_size/2, tile_size/2)
		self.rect = self.image.get_rect(center=pos+offset)
		self.radius = 20

class Tile(pygame.sprite.Sprite):
	def __init__(self, pos, type):
		super().__init__()
		if type == "2":
			self.image = light_tile
		elif type == "3":
			self.image = dark_tile

		self.rect = self.image.get_rect(topleft=pos)

def show_text(surface, text, pos, size, color, anti_alias=False, font=None):
	font_obj = pygame.font.Font(font, size)
	font_surface = font_obj.render(text, anti_alias, color)
	font_pos = font_surface.get_rect(topleft=pos)
	surface.blit(font_surface, font_pos)

# Screen + Clock
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# Tiles
light_tile = pygame.image.load("../assets/tile1.png").convert()
dark_tile = pygame.image.load("../assets/tile2.png").convert()

# Sounds
swing_sound = pygame.mixer.Sound("../assets/sound/res_sfx_swing.mp3")
hole_sound = pygame.mixer.Sound("../assets/sound/res_sfx_hole.mp3")
charge_sound = pygame.mixer.Sound("../assets/sound/res_sfx_charge.mp3")

# Game Variables
ball_speed = 2
max_speed = 40
friction = 0.5

#Game
game = Game()

# Main Loop
while True:
	
	# Event Loop
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()

	# level
	game.run()
	
	pygame.display.update()
	clock.tick(60)