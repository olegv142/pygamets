"""
Progress indicator widget
"""

import pygame as pg
import app, gui, style, utils
import math

class PieProgressIndicator(gui.View):
	"""
	Pie-chart like progress indicator widget
	"""
	def __init__(self, w, st = None):
		gui.View.__init__(self, w, w)
		self.style = style.bind(st, self)
		self.progress = 0.
		self.rotating = False
		self.phase = 0

	def set_progress(self, val, rotating = False):
		"""
		Set progress value in the range 0..1.
		The rotating mode is used in situations when we are not going to
		keep progress constantly updating but have to demonstrate that 
		something is still happening.
		"""
		self.progress = val
		self.rotating = rotating
		self.update()

	def init(self, surface):
		gui.View.init(self, surface)
		self.timer = app.Timer(self.on_timer, self.style.interval, True)
		app.instance.add_timer(self.timer)

	def fini(self):
		gui.View.fini(self)
		self.timer.cancel()

	def on_timer(self):
		if self.rotating:
			self.phase += 1
		if self.phase >= self.style.period:
			self.phase = 0
		self.update()

	def draw(self):
		x, y, w, h = self.frame()
		r = (w - 1) // 2
		assert r > 0
		center = (x + r, y + r)
		pg.draw.rect(self.surface, self.style.f_color, (x, y, w, h))
		# handle degenerate cases first
		if self.progress >= 1:
			pg.draw.circle(self.surface, self.style.done_color, center, r)
			return
		pg.draw.circle(self.surface, self.style.todo_color, center, r)
		if self.progress <= 0:
			return
		progress_angle = self.progress * 2 * math.pi
		start_angle = (2 * math.pi * self.phase) / self.style.period
		utils.draw_sector(
				self.surface, self.style.done_color, center, r,
				start_angle, start_angle + progress_angle
			)
