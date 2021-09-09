import pygame
from levels import screen_width, screen_height
from utils import Button
from global_ import Global
from .game_over_scene import Screen

class Screen(Screen):
	def __init__(self, screen):
		super().__init__(screen)

		# Title
		self.title_surface = self.font_obj.render("You Won", False, (0, 0, 0))
		self.title_pos = self.title_surface.get_rect(center=(screen_width/2, 100))

		# Replay_btn
		self.restart_btn_config = {**self.restart_btn_config, "text": "Replay"}
		self.restart_btn = Button(screen, self.restart_btn_pos-pygame.math.Vector2(0, 100), self.restart_btn_config)

		# Next_btn
		self.next_btn_config = {**self.restart_btn_config, "text": "Next Level"}
		self.next_btn = Button(screen, self.restart_btn_pos, self.next_btn_config)

		# Previous_btn
		self.prev_btn_config = {**self.restart_btn_config, "text": "Previous Level", "text_size": 40}
		self.prev_btn = Button(screen, self.restart_btn_pos+pygame.math.Vector2(0, 100), self.prev_btn_config)		
	
	def on_next_btn_clk(self):
		Global.cur_level += 1
		Global.level.change_level(Global.cur_level)
		Global.state = "playing"

	def on_prev_btn_clk(self):
		Global.cur_level -= 1
		Global.level.change_level(Global.cur_level)
		Global.state = "playing"

	def run(self):
		
		# Title
		self.display_surface.blit(self.title_surface, self.title_pos)

		# Restart_Btn
		self.restart_btn.active(self.on_restart_btn_clk)

		# Prev_Btn
		if not Global.cur_level <= 1 and not Global.cur_level >= Global.max_level:
			self.prev_btn.active(self.on_prev_btn_clk)

		# Next Btn
		if not Global.cur_level >= Global.max_level:
			self.next_btn.active(self.on_next_btn_clk)
		else:
			self.prev_btn.rect.center = self.next_btn.rect.center
			self.prev_btn.active(self.on_prev_btn_clk)