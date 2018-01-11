"""
Window classes
"""

import gui, style, utils
import pygame as pg

class FrameWindow(gui.Window):
	"""Fixed size window with optional border"""
	_required_attrs = ('f_color',)

	def __init__(self, x, y, w, h, st = None):
		gui.Window.__init__(self, x, y, w, h)
		self.style = style.bind(self, st)

	def int_frame(self):
		"""Take into account border if present"""
		iframe = gui.Window.int_frame(self)
		b = self.style.border
		if b:
			return utils.apply_margins(iframe, b + 1, b + 1)
		else:
			return iframe

	def draw(self):
		frame = self.frame()
		pg.draw.rect(self.surface, self.style.f_color, frame)
		if self.style.border:
			m = self.style.border // 2
			pg.draw.rect(self.surface, self.style.b_color, utils.apply_margins(frame, m, m), self.style.border)

