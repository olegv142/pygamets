"""
Battery charge indicator
"""

import app, gui, style
import pygame as pg

class BatteryIndicator(gui.View):
	"""
	Battery indicator widget
	"""
	def __init__(self, w, h, st = None):
		gui.View.__init__(self, w, h)
		self.style = style.bind(st, self)
		self.charge = 0
		self.font = None
		self.text = None

	def init(self, surface):
		gui.View.init(self, surface)
		ff = self.style.font_face
		if ff:
			self.font = pg.font.SysFont(ff, self.style.font_size)

	def set_charge(self, val):
		"""Set charge level as floating point in range 0..1"""
		self.charge = max(0., min(1., val))
		if self.font:
			self.text = self.font.render('%d%%' % int(100*val), True, self.style.t_color)
		self.update()

	def draw(self):
		"""Draw horizontal battery picture"""
		x, y, w, h = self.frame()
		r = max(1, int(h*self.style.roundness))
		t = max(r, int(w*self.style.tip_height))
		b = w - t # battery length without tip
		assert b >= 3*r
		d = int(h*self.style.tip_diameter)
		m = (h - d) // 2
		assert m >= r
		assert h - 2*m >= 2*r

		if self.charge >= self.style.alert_charge:
			charge_color = self.style.charge_color
		else:
			charge_color = self.style.alert_color
		batt_color = self.style.batt_color

		pg.draw.circle(self.surface, charge_color, (x + r, y + r), r)
		pg.draw.circle(self.surface, charge_color, (x + r, y + h - r), r)
		pg.draw.circle(self.surface, batt_color,   (x + b - r, y + r), r)
		pg.draw.circle(self.surface, batt_color,   (x + b - r, y + h - r), r)
		pg.draw.circle(self.surface, batt_color,   (x + w - r, y + m + r), r)
		pg.draw.circle(self.surface, batt_color,   (x + w - r, y + h - m - r), r)
		pg.draw.rect  (self.surface, charge_color, (x, y + r, r, h - 2*r))
		pg.draw.rect  (self.surface, batt_color,   (x + b - r, y + r, r, h - 2*r))
		pg.draw.rect  (self.surface, batt_color,   (x + b, y + m, t - r, h - 2*m))
		pg.draw.rect  (self.surface, batt_color,   (x + w - r, y + m + r, r, h - 2*(m + r)))

		l = b - 2*r
		c = int(l*self.charge)

		pg.draw.rect  (self.surface, charge_color, (x + r, y, c, h))
		pg.draw.rect  (self.surface, batt_color,   (x + r + c, y, l - c, h))

		if self.text:
			self.blit_centered(self.text, (x, y, b, h))

