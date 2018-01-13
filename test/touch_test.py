#!/usr/bin/python

"""
Test for pygame mouse events.
Don't worry if the touch coordinates are the way off.
Using the pygamets.app and calibration tool will fix it.
Launch app_event_test.py to see the effect. 
"""

import sys
import pygame as pg

sys.path.append('..')
from pygamets import env

pg.display.init()
pg.display.set_mode()

while True:
	for e in pg.event.get():
		if e.type == pg.MOUSEBUTTONUP:
			print e.pos


