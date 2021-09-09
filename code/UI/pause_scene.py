from .victory_scene import Screen
from global_ import Global
from utils import Button

class Screen(Screen):
	def __init__(self, screen):
		super().__init__(screen)

		# Title
		self.title_surface = self.font_obj.render("Pause Menu", False, (0, 0, 0))
		self.title_pos = self.title_surface.get_rect(center=self.pos)

		# Resume Button
		self.resume_btn_pos = (self.restart_btn_pos[0], self.restart_btn_pos[1]-100)
		self.resume_btn_config = {**self.restart_btn_config, "text": "Resume"}
		self.resume_btn = Button(screen, self.resume_btn_pos, self.resume_btn_config)

		# Replay btn
		self.restart_btn_config = {**self.restart_btn_config, "text": "Restart"}
		self.restart_btn = Button(screen, self.restart_btn_pos ,self.restart_btn_config)

	def on_resume_btn_clk(self):
		Global.state = "playing"

	def run(self):

		# Title
		self.display_surface.blit(self.title_surface, self.title_pos)

		# Restart Button
		self.restart_btn.active(self.on_restart_btn_clk)

		# Resume Button
		self.resume_btn.active(self.on_resume_btn_clk)