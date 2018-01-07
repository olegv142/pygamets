"""
Label class
"""

import gui, style, utils
import pygame as pg
from localize import localize

class TextLabel(gui.View):
	"""The plain text label"""
	_required_attrs = ('font_face', 'font_size')

	def __init__(self, w, h, st = None):
		gui.View.__init__(self, w, h)
		self.style = style.bind(self, st)
		self.font  = None
		self.text  = None
		self.color = None
		self.label = None

	def init(self, surface):
		gui.View.init(self, surface)
		self.font = pg.font.SysFont(self.style.font_face, self.style.font_size)
		if not self.text:
			self.text = self.style.name
		if not self.color:
			self.color = self.style.t_color
		if self.text and self.color:
			self.label = self.font.render(localize(self.text), True, self.color)

	def set_text(self, text, color = None):
		if text == self.text and color == self.color:
			return
		self.text = text
		if color is not None:
			self.color = color
		if self.text and self.color and self.font:
			self.label = self.font.render(localize(self.text), True, self.color)
		else:
			self.label = None
		self.update()

	def draw(self):
		if self.style.f_color:
			pg.draw.rect(self.surface, self.style.f_color, self.frame())
		if self.label:
			utils.blit_centered(self.surface, self.label, self.frame())
