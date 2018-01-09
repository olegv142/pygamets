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

def merge(surf0, surf1, k):
	"""Merge 2 surfaces of the same dimension producing the linear combination surf0 * (1 - k) + surf1 * k"""
	k = max(0, min(255, int(255*k)))
	s0, s1 = surf0.copy(), surf1.copy()
	s1.fill((k, k, k), None, pg.BLEND_RGB_MULT)
	s0.fill((255-k, 255-k, 255-k), None, pg.BLEND_RGB_MULT)
	s0.blit(s1, (0, 0), None, pg.BLEND_RGB_ADD)
	return s0
