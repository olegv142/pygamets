"""
Log window
"""

import button, utils, style
from frame import Frame
import logging
import pygame as pg

class ListView(Frame):
	"""The list of coloured strings"""
	_required_attrs = ('font_face', 'font_size', 'left_margin', 'top_margin', 'f_color')

	def __init__(self, w, h, st = None):
		Frame.__init__(self, w, h, st)
		self.font = pg.font.SysFont(self.style.font_face, self.style.font_size)
		_, ih = self.int_size()
		self.n = (ih - self.style.top_margin) // self.font.get_height()
		self.list = []

	def append(self, text, color):
		"""Append the line of text to the list"""
		self.list.append([text, color, None])
		if len(self.list) > self.n:
			self.list = self.list[-self.n:]
		self.update()

	def clear(self):
		"""Clear the list"""
		self.list = []

	def draw(self):
		Frame.draw(self)
		ix, iy, iw, ih = self.rect_to_screen(self.int_frame())
		ix += self.style.left_margin
		iy += self.style.top_margin
		fh = self.font.get_height()
		for i, m in enumerate(self.list):
			text, color, rendered = m
			if not rendered:
				m[2] = rendered = self.font.render(text, True, color)
			self.surface.blit(rendered, (ix, iy + i * fh))
