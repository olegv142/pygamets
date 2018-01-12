"""
X,Y curve plotting
"""

import utils, style
from frame import Frame
from button import Button
import pygame as pg
import math
from collections import namedtuple

TicksParams = namedtuple('TicksParams', ('digit', 'power', 'minor_ticks'))
Tick = namedtuple('Tick', ('val', 'vabel'))

def get_ticks_params(v, xmaj):
	"""Find ticks parameters for the given value range so that the number of major ticks does not exceed xmaj"""
	power = 0.
	if v <= 0:
		return TicksParams(1, 0, 2)
	a, b = xmaj / 2., xmaj * 5.
	while v < a:
		v *= 10.
		power -= 1
	while v > b:
		v /= 10.
		power += 1
	if v < a * 2:
		return TicksParams(1, power, 2)
	elif v < a * 4:
		return TicksParams(2, power, 2)
	else:
		return TicksParams(5, power, 5)

def get_ticks(l, r, xmaj, xrng):
	"""Get the set of ticks for the given range"""
	assert l <= r
	ticks = []
	d = float(r - l)
	p = get_ticks_params(d, xmaj)
	T = p.digit * 10. ** p.power
	t = T / p.minor_ticks
	off_mode = d / max(abs(l), abs(r)) < xrng
	V = v = math.floor(l/T) * T
	ticks.append(Tick(v, '%g' % V))
	if off_mode:
		V = 0.
	while True:
		for _ in range(p.minor_ticks-1):
			v += t
			ticks.append(Tick(v, None))
			if v > r:
				return ticks
		v += t
		V += T
		label = '%g' % V
		if off_mode:
			label = '+' + label
		ticks.append(Tick(v, label))
		if v > r:
			return ticks

class PlotView(Frame):
	"""X,Y curve plot"""
	_required_attrs = (
			'font_face', 'font_size', 'f_color',
			'label_color', 'axis_color', 'line_color',
			'margin', 'label_offset', 'maj_tick_len', 'min_tick_len',
			'maj_ticks', 'xrange'
		)

	def __init__(self, w, h, st = None):
		Frame.__init__(self, w, h, st)
		self.font = pg.font.SysFont(self.style.font_face, self.style.font_size)
		self.data = None

	def set_data(self, xy):
		"""
		Set data to plot as (X, Y) tuple or None.
		The ordering of the points along X axis does not matter.
		The drawing algorithm will sort them in proper order.
		"""
		self.data = xy
		self.update()

	def draw(self):
		Frame.draw(self)
		if self.data is None:
			return

		# X,Y data to plot
		X, Y = self.data
		# Screen area
		ix, iy, iw, ih = utils.apply_margins(self.rect_to_screen(self.int_frame()), self.style.margin, self.style.margin)

		# Calculate ticks
		xticks = get_ticks(min(X), max(X), self.style.maj_ticks, self.style.xrange)
		yticks = get_ticks(min(Y), max(Y), self.style.maj_ticks, self.style.xrange)

		# Render labels
		label_color = self.style.label_color
		xlabels = [self.font.render(t, True, label_color) if t is not None else None for _, t in xticks]
		ylabels = [self.font.render(t, True, label_color) if t is not None else None for _, t in yticks]
		ylabels_w = max(l.get_width() for l in ylabels if l is not None)

		# Plan plotting area
		label_off = self.style.label_offset
		off = label_off + self.style.maj_tick_len
		plot_w = iw - ylabels_w - off
		plot_h = ih - self.font.get_height() - off
		assert plot_w > 1 and plot_h > 1
		orig_x = ix + ylabels_w + off
		orig_y = iy + plot_h

		# So we need mapping from plot_rect to screen_rect
		plot_rect = (
				xticks[0].val, yticks[0].val,
				xticks[-1].val - xticks[0].val, yticks[-1].val - yticks[0].val
			)
		screen_rect = (orig_x, orig_y, plot_w, -plot_h)

		# Obtain coordinate transformation functions
		x2screan, y2screan = utils.map_to_screen(plot_rect, screen_rect)
	
		# Draw axis
		axis_color = self.style.axis_color
		pg.draw.line(self.surface, axis_color, (orig_x, orig_y), (orig_x + plot_w - 1, orig_y))
		pg.draw.line(self.surface, axis_color, (orig_x, orig_y), (orig_x, orig_y - plot_h + 1))
		maj_len, min_len = self.style.maj_tick_len, self.style.min_tick_len

		# Draw X ticks and labels
		for i, (v, t) in enumerate(xticks):
			x = x2screan(v)
			tick_len = maj_len if t is not None else min_len
			pg.draw.line(self.surface, axis_color, (x, orig_y), (x, orig_y + tick_len))
			if t is not None:
				l = xlabels[i]
				self.surface.blit(l, (x - l.get_width()/2, orig_y + off))

		# Draw Y ticks and labels
		for i, (v, t) in enumerate(yticks):
			y = y2screan(v)
			tick_len = maj_len if t is not None else min_len
			pg.draw.line(self.surface, axis_color, (orig_x, y), (orig_x - tick_len, y))
			if t is not None:
				l = ylabels[i]
				self.surface.blit(l, (orig_x - off - l.get_width(), y - l.get_height()/2))

		# Draw line through the sequence of points
		points = utils.xy_path(X, Y, plot_rect, screen_rect)
		if len(points) > 1:
			pg.draw.aalines(self.surface, self.style.line_color, False, points)

class PlotButton(Button):
	"""The button with X,Y curve plot"""
	_required_attrs = ('f_color', 'margin', 'line_color', 'linep_color')

	def __init__(self, w, h, st = None):
		Button.__init__(self, w, h, st)
		self.curve = None

	def on_clicked(self):
		"""Mouse clicked handler"""
		if self.curve is None:
			# Ignore if data is not set
			return
		Button.on_clicked(self)

	def set_data(self, xy):
		"""
		Set data to plot as (X, Y) tuple or None.
		The ordering of the points along X axis does not matter.
		The drawing algorithm will sort them in proper order.
		"""
		if xy is None:
			self.curve = None
		else:
			# X,Y data to plot
			X, Y = xy
			# Screen area
			ix, iy, iw, ih = utils.apply_margins(self.rect_to_screen(self.int_frame()), self.style.margin, self.style.margin)
			px, py = min(X), min(Y)
			pw, ph = max(X) - px, max(Y) - py
			if pw <= 0: pw = 1.
			if ph <= 0: ph = 1.
			self.curve = utils.xy_path(X, Y, (px, py, pw, ph), (ix, iy + ih, iw, -ih))
			if len(self.curve) < 2:
				self.curve = None
		self.update()

	def draw(self):
		Button.draw(self)
		if self.curve is not None:
			pg.draw.aalines(self.surface,
					self.style.line_color if not self.is_pressed else self.style.linep_color,
					False, self.curve
				)
