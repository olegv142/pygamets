"""
Log window
"""

import button, utils, style
from window import FrameWindow
import logging
import pygame as pg

class LogWindow(FrameWindow, logging.Handler):
	"""This window serves as log handler and shows the last log records"""
	_required_attrs = (
			'font_face', 'font_size',
			'norm_color', 'warn_color', 'err_color',
			'x_btn_size', 'left_margin', 'top_margin'
		) + FrameWindow._required_attrs

	def __init__(self, x, y, w, h, st = None):
		FrameWindow.__init__(self, x, y, w, h)
		logging.Handler.__init__(self)
		self.style = style.bind(self, st)
		btn = button.XButton(self.style.x_btn_size, self.style.copy())
		btn.clicked.connect(self.close)
		utils.add_top_right(self, btn)
		self.font = pg.font.SysFont(self.style.font_face, self.style.font_size)
		_, ih = self.int_size()
		self.n = (ih - self.style.top_margin) // self.font.get_height()
		self.msgs = []

	def emit(self, record):
		"""logging.Handler method"""
		self.msgs.append([self.format(record), record.levelno, None])
		if len(self.msgs) > self.n:
			self.msgs = self.msgs[-self.n:]
		self.update()

	def msg_color(self, lvl):
		if lvl <= logging.INFO:
			return self.style.norm_color
		if lvl < logging.ERROR:
			return self.style.warn_color
		else:
			return self.style.err_color

	def draw(self):
		FrameWindow.draw(self)
		ix, iy, iw, ih = self.rect_to_screen(self.int_frame())
		ix += self.style.left_margin
		iy += self.style.top_margin
		fh = self.font.get_height()
		for i, m in enumerate(self.msgs):
			text, lvl, rendered = m
			if not rendered:
				m[2] = rendered = self.font.render(text, True, self.msg_color(lvl))
			self.surface.blit(rendered, (ix, iy + i * fh))
