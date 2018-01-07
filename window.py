"""
Window classes
"""

import gui, style, utils
import pygame as pg

class BckgWindow(gui.Window):
	"""Window filling entire screen"""
	def __init__(self, st = None):
		gui.Window.__init__(self, 0, 0, None, None)
		self.style = style.bind(self, st)

	def init(self, surface):
		self.w, self.h = surface.get_size()
		gui.Window.init(self, surface)

	def draw(self):
		pg.draw.rect(self.surface, self.style.f_color, self.frame())

class FrameWindow(gui.Window):
	"""Fixed size window with optional border"""
	def __init__(self, x, y, w, h, st = None):
		gui.Window.__init__(self, x, y, w, h)
		self.style = style.bind(self, st)

	def int_frame(self):
		"""Take into account border if present"""
		iframe = gui.Window.int_frame(self)
		b = self.style.border
		if b:
			return utils.apply_margins(iframe, b, b)
		else:
			return iframe

	def draw(self):
		frame = self.frame()
		pg.draw.rect(self.surface, self.style.f_color, frame)
		if self.style.border:
			pg.draw.rect(self.surface, self.style.b_color, frame, self.style.border)

