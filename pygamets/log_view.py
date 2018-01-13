"""
Log window
"""

import gui, button, utils, style
from list_view import ListView
import logging
import pygame as pg

class LogView(ListView, logging.Handler):
	"""This view serves as log handler and shows the last log records"""
	_required_attrs = ('norm_color', 'warn_color', 'err_color') + ListView._required_attrs

	def __init__(self, w, h, st = None):
		ListView.__init__(self, w, h, st)
		logging.Handler.__init__(self)

	def emit(self, rec):
		"""logging.Handler method"""
		self.append(self.format(rec), self.msg_color(rec.levelno))

	def msg_color(self, lvl):
		if lvl <= logging.INFO:
			return self.style.norm_color
		if lvl < logging.ERROR:
			return self.style.warn_color
		else:
			return self.style.err_color

class LogWindow(gui.Window):
	"""The window showing the last log records"""
	_required_attrs = ('x_btn_size',)

	def __init__(self, W, H, st = None):
		self.style = style.bind(self, st)
		gui.Window.__init__(self, 0, 0, LogView(W, H, self.style.copy()))
		btn = button.XButton(self.style.x_btn_size, self.style.copy())
		btn.clicked.connect(self.close)
		utils.add_top_right(self, btn)

	def handler(self):
		return self.view
