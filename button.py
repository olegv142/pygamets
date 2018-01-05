"""
Button classes
"""

import app, gui, style
import pygame as pg
from localize import localize

class StyledButton(gui.Button):
	def __init__(self, w, h, st = None):
		gui.Button.__init__(self, w, h)
		self.style = style.bind(st, self)
		self.pressed.connect(self.pressed_cb)

	def pressed_cb(self, pressed):
		self.update()

class RectButton(StyledButton):
	"""Rectangular button with optional border"""
	def __init__(self, w, h, st = None):
		StyledButton.__init__(self, w, h, st)

	def init(self, surface):
		StyledButton.init(self, surface)
		if self.style.name:
			font = pg.font.SysFont(self.style.font_face, self.style.font_size)
			self.label = font.render(localize(self.style.name), True, self.style.t_color)
		else:
			self.label = None

	def draw(self):
		rect = self.frame()
		color = self.style.f_color if not self.is_pressed else self.style.p_color
		pg.draw.rect(self.surface, color, rect)
		if self.style.border:
			pg.draw.rect(self.surface, self.style.b_color, rect, self.style.border)
		if self.label is not None:
			self.blit_centered(self.label)

class TextButton(StyledButton):
	"""The Button with only text label drawn"""
	def __init__(self, w, h, st = None):
		StyledButton.__init__(self, w, h, st)

	def init(self, surface):
		StyledButton.init(self, surface)
		name = localize(self.style.name)
		assert name
		font = pg.font.SysFont(self.style.font_face, self.style.font_size)
		self.label   = font.render(name, True, self.style.t_color)
		self.p_label = font.render(name, True, self.style.tp_color)

	def draw(self):
		label = self.label if not self.is_pressed else self.p_label
		self.blit_centered(label)

class XButton(StyledButton):
	"""The X-mark button"""
	def __init__(self, w, st = None):
		StyledButton.__init__(self, w, w, st)

	def draw(self):
		color = self.style.x_color if not self.is_pressed else self.style.xp_color
		x, y, w, h = self.frame_with_margin(int(self.style.x_margin * self.w), int(self.style.x_margin * self.h))
		pg.draw.line(self.surface, color, (x, y), (x + w, y + h), self.style.x_width)
		pg.draw.line(self.surface, color, (x + w, y), (x, y + h), self.style.x_width)

class PulseTextButton(StyledButton):
	"""The fancy pulsing text button"""
	def __init__(self, w, h, st = None):
		StyledButton.__init__(self, w, h, st)

	def init(self, surface):
		StyledButton.init(self, surface)
		name = localize(self.style.name)
		assert name
		assert self.style.decay > 0
		font = pg.font.SysFont(self.style.font_face, self.style.font_size)
		self.label0  = font.render(name, True, self.style.t0_color)
		self.label1  = font.render(name, True, self.style.t1_color)
		self.p_label = font.render(name, True, self.style.tp_color)
		self.timer = app.Timer(self.on_timer, self.style.interval, True)
		app.instance.add_timer(self.timer)
		self.phase = 0

	def fini(self):
		StyledButton.fini(self)
		self.timer.cancel()

	def on_timer(self):
		self.phase += 1
		if self.phase >= self.style.period:
			self.phase = 0
		self.update()

	def draw(self):
		if self.is_pressed:
			label = self.p_label
		else:
			f = float(self.phase) / self.style.decay
			p = int(255/(1+f*f))
			l0, l1 = self.label0.copy(), self.label1.copy()
			l1.fill((p, p, p), None, pg.BLEND_RGB_MULT)
			l0.fill((255-p, 255-p, 255-p), None, pg.BLEND_RGB_MULT)
			l1.blit(l0, (0, 0), None, pg.BLEND_RGB_ADD)
			label = l1
		self.blit_centered(label)
