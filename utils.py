import math
import pygame as pg

def apply_margins(rect, x_margin, y_margin):
		"""Apply margins to the rectangular area"""
		x, y, w, h = rect
		return x + x_margin, y + y_margin, w - 2*x_margin, h - 2*y_margin

def blit_centered(dst, surf, rect):
	"""Blit given image surface centred in the destination rectangular area"""
	x, y, w, h = rect
	sw, sh = surf.get_size()
	dst.blit(surf, (x + (w - sw) // 2, y + (h - sh) // 2))

def draw_sector(surface, color, center, radius, from_angle, to_angle):
	"""Draw filled sector as filled polygon"""
	x, y = center
	angle = to_angle - from_angle
	segments = 1 + int(angle * radius / 4)
	angles = [from_angle + (i*angle)/segments for i in range(segments+1)]
	pointlist = [(x + int(radius*math.sin(a)), y - int(radius*math.cos(a))) for a in angles]
	pointlist.append(center)
	pg.draw.polygon(surface, color, pointlist)

def merge_rgb(col0, col1, k):
	"""Merge 2 colours producing the linear combination col0 * (1 - k) + col1 * k"""
	r0, g0, b0 = col0
	r1, g1, b1 = col1
	r = max(0, min(255, int(r0*(1-k) + r1*k)))
	g = max(0, min(255, int(g0*(1-k) + g1*k)))
	b = max(0, min(255, int(b0*(1-k) + b1*k)))
	return r, g, b

def add_top_left(parent, v, xmargin = 0, ymargin = 0, next_to = None):
	"""Child view placement helper"""
	x, y, w, h = parent.int_frame()
	if next_to is not None:
		x = next_to.x + next_to.w
	parent.add_child(v, x + xmargin, y + ymargin)

def add_top_right(parent, v, xmargin = 0, ymargin = 0, next_to = None):
	"""Child view placement helper"""
	x, y, w, h = parent.int_frame()
	if next_to is not None:
		x = next_to.x
	else:
		x += w
	x -= v.w + 2 * xmargin
	parent.add_child(v, x + xmargin, y + ymargin)

def add_left_top(parent, v, xmargin = 0, ymargin = 0, next_to = None):
	"""Child view placement helper"""
	x, y, w, h = parent.int_frame()
	if next_to is not None:
		y = next_to.y + next_to.h
	parent.add_child(v, x + xmargin, y + ymargin)

def add_left_bottom(parent, v, xmargin = 0, ymargin = 0, next_to = None):
	"""Child view placement helper"""
	x, y, w, h = parent.int_frame()
	if next_to is not None:
		y = next_to.y
	else:
		y += h
	y -= v.h + 2 * ymargin
	parent.add_child(v, x + xmargin, y + ymargin)
