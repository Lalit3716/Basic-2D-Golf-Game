import pygame
from levels import screen_width, screen_height
from utils import Button
from global_ import Global

class Screen:
	def __init__(self, screen):

		# Display Surface
		self.display_surface = screen
		
		# Title
		self.font_obj = pygame.font.Font(None, 100)
		self.title_surface = self.font_obj.render("Game Over", False, (0, 0, 0))
		self.pos = (screen_width/2, 100)
		self.title_pos = self.title_surface.get_rect(center=self.pos)

		# Restart Button
		self.restart_btn_pos = (screen_width/2, screen_height/2)
		self.restart_btn_config = {
			"size": (250, 60),
			"color": (61, 178, 255),
			"border_radius": 20,
			"text": "Restart",
			"text_size": 50,
			"text_color": (0, 0, 0),
			"outline": 1,
			"hover": (0, 255, 0)
		}

		self.restart_btn = Button(self.display_surface, self.restart_btn_pos, self.restart_btn_config)

	def on_restart_btn_clk(self):
		Global.level.restart()
		Global.state = "playing"

	def run(self):
		# Title
		self.display_surface.blit(self.title_surface, self.title_pos)

		# Buttons
		self.restart_btn.active(self.on_restart_btn_clk)