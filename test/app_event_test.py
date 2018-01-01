#!/usr/bin/python

import sys, time
import pygame as pg

sys.path.append('..')
from app import Application

pg.display.init()
pg.display.set_mode()
app = Application()

while True:
	time.sleep(.05)
	for e in pg.event.get():
		print e

