#!/usr/bin/python

import sys, os, time
import pygame as pg
import math

sys.path.append('..')
import events
import calibration
from events import read_events

XMARK_SZ = 10
XMARK_COLOR = (0, 255, 0)

def get_touched_point():
	"""Wait touch and returns its position in raw touch-screen coordinates"""
	down, pos = None, None
	while True:
		events = read_events()
		if events:
			for e in events:
				if e.pos:
					pos = e.pos
				if e.down is not None:
					down = e.down
		elif down == False and pos:
			return pos
		time.sleep(.2)

def draw_xmark(s, color, xp, yp):
	"""Draw cross mark"""
	pg.draw.line(s, color, (xp - XMARK_SZ, yp), (xp + XMARK_SZ, yp))
	pg.draw.line(s, color, (xp, yp - XMARK_SZ), (xp, yp + XMARK_SZ))
	pg.display.update()

def get_calib_point(s, (x, y)):
	"""
	Draw cross mark at given point in coordinates relative to screen size (in the range 0..1)
	and returns the touched point in raw touch-screen coordinates
	"""
	inf = pg.display.Info()
	xp = int(inf.current_w * x)
	yp = int(inf.current_h * y)
	draw_xmark(s, XMARK_COLOR, xp, yp)
	tx, ty = get_touched_point()
	draw_xmark(s, (0, 0, 0), xp, yp)
	return tx, ty

def calibrate():
	pg.display.init()
	pg.mouse.set_visible(False)
	pg.display.set_mode()
	s = pg.display.set_mode()
	screen_pts = [(.2, .2), (.8, .2), (.2, .8), (.8, .8), (.5, .5)]
	while True:
		touch_pts = [get_calib_point(s, pt) for pt in screen_pts]
		calib, dmax = calibration.build(screen_pts, touch_pts)
		print 'max deviation %.1g' % dmax
		if dmax > .02:
			print 'bad accuracy, please try again'
		else:
			break
	calibration.save(calib)
	print 'calibration saved to', calibration.config_path()


if __name__=='__main__':
	calibrate()


	

