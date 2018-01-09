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
	_required_attrs = ('interval', 'period', 'f_color', 'done_color', 'todo_color')

	def __init__(self, w, st = None):
		gui.View.__init__(self, w, w)
		self.style = style.bind(self, st)
		self.progress = 0.
		self.rotating = False
		self.changed = False
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
		self.changed = True

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
			self.changed = True
		if self.changed:
			self.update()
			self.changed = False

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

class BallClockProgressIndicator(gui.View):
	"""
	Ball clock like progress indicator widget
	"""
	_required_attrs = ('interval', 'step', 'ball_sz', 'ball_cnt', 'done_color', 'todo_color')

	def __init__(self, w, st = None):
		gui.View.__init__(self, w, w)
		self.style = style.bind(self, st)
		self.progress = 0.
		self.rotating = False
		self.phase = 0
		self.step = 0

	def set_progress(self, val, rotating = False):
		"""
		Set progress value in the range 0..1.
		The rotating mode is used in situations when we are not going to
		keep progress constantly updating but have to demonstrate that 
		something is still happening.
		"""
		self.progress = val
		self.rotating = rotating

	def init(self, surface):
		gui.View.init(self, surface)
		self.timer = app.Timer(self.on_timer, self.style.interval, True)
		app.instance.add_timer(self.timer)
		cnt = self.style.ball_cnt
		assert cnt > 1
		d = 1 + 2*int(self.w*self.style.ball_sz/2)
		r = d // 2
		self.ball_r = r
		self.ball_states = [cnt-1]*cnt
		self.ball_imgs = [None]*cnt
		for i in range(cnt):
			s = pg.Surface((d, d), pg.SRCALPHA, 32)
			k = 1. / (1 + i*i)
			pg.draw.circle(s, utils.merge_rgb(self.style.todo_color, self.style.done_color, k), (r, r), r)
			self.ball_imgs[i] = s

	def fini(self):
		gui.View.fini(self)
		self.timer.cancel()

	def on_timer(self):
		states = self.ball_states[:]
		if self.rotating:
			self.step += 1
			if self.step >= self.style.step:
				self.step = 0;
				self.phase += 1
				if self.phase >= len(states):
					self.phase = 0

		cnt = len(states)
		active = max(0, min(cnt, int(self.progress*cnt)))
		decay = (1 + cnt) // (1 + cnt - active)
		for i in range(cnt):
			j = (i + self.phase) % cnt
			if i < active:
				self.ball_states[j] = 0
			else:
				self.ball_states[j] = min(cnt - 1, self.ball_states[j] + decay)

		if states != self.ball_states:
			self.update()

	def draw(self):
		x, y, w, h = self.frame()
		R = (w - 1) // 2
		da = 2 * math.pi / len(self.ball_states)
		for i, st in enumerate(self.ball_states):
			a = da * i
			self.surface.blit(self.ball_imgs[st], (
					x + (R - self.ball_r) * (1 + math.sin(a)),
					y + (R - self.ball_r) * (1 - math.cos(a))
				))
