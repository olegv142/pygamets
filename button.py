"""
Button classes
"""

import app, gui, style
import pygame as pg
from localize import localize

class RectButton(gui.Button):
	"""Rectangular button with optional border"""
	def __init__(self, w, h, st = None):
		gui.Button.__init__(self, w, h)
		self.style = style.bind(st, self)
		if self.style.name:
			font = pg.font.SysFont(self.style.font_face, self.style.font_size)
			self.label = font.render(localize(self.style.name), True, self.style.t_color)
		else:
			self.label = None
		self.pressed.connect(self.pressed_cb)

	def draw(self):
		rect = self.frame()
		color = self.style.f_color if not self.is_pressed else self.style.p_color
		pg.draw.rect(self.surface, color, rect)
		if self.style.border:
			pg.draw.rect(self.surface, self.style.b_color, rect, self.style.border)
		if self.label is not None:
			self.blit_centered(self.label)

	def pressed_cb(self, pressed):
		self.update()

class TextButton(gui.Button):
	"""The Button with only text label drawn"""
	def __init__(self, w, h, st = None):
		gui.Button.__init__(self, w, h)
		self.style = style.bind(st, self)
		name = localize(self.style.name)
		assert name
		font = pg.font.SysFont(self.style.font_face, self.style.font_size)
		self.label   = font.render(name, True, self.style.t_color)
		self.p_label = font.render(name, True, self.style.tp_color)
		self.pressed.connect(self.pressed_cb)

	def draw(self):
		label = self.label if not self.is_pressed else self.p_label
		self.blit_centered(label)

	def pressed_cb(self, pressed):
		self.update()

class XButton(gui.Button):
	"""The X-mark button"""
	def __init__(self, w, st = None):
		gui.Button.__init__(self, w, w)
		self.style = style.bind(st, self)
		self.pressed.connect(self.pressed_cb)

	def draw(self):
		color = self.style.x_color if not self.is_pressed else self.style.xp_color
		x, y, w, h = self.frame_with_margin(int(self.style.x_margin * self.w), int(self.style.x_margin * self.h))
		pg.draw.line(self.surface, color, (x, y), (x + w, y + h), self.style.x_width)
		pg.draw.line(self.surface, color, (x + w, y), (x, y + h), self.style.x_width)

	def pressed_cb(self, pressed):
		self.update()

class PulseTextButton(gui.Button):
	"""The fancy pulsing text button"""
	def __init__(self, w, h, st = None):
		gui.Button.__init__(self, w, h)
		self.style = style.bind(st, self)
		name = localize(self.style.name)
		assert name
		assert self.style.decay > 0
		font = pg.font.SysFont(self.style.font_face, self.style.font_size)
		self.label0  = font.render(name, True, self.style.t0_color)
		self.label1  = font.render(name, True, self.style.t1_color)
		self.p_label = font.render(name, True, self.style.tp_color)
		self.pressed.connect(self.pressed_cb)
		self.timer = app.Timer(self.on_timer, self.style.interval, True)
		self.phase = 0

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

	def on_timer(self):
		self.phase += 1
		if self.phase >= self.style.period:
			self.phase = 0
		self.update()

	def init(self, surface):
		gui.Button.init(self, surface)
		app.instance.add_timer(self.timer)

	def fini(self):
		gui.Button.fini(self)
		self.timer.cancel()

	def pressed_cb(self, pressed):
		self.update()
