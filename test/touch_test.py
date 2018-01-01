#!/usr/bin/python

import pygame as pg

pg.display.init()
pg.display.set_mode()

while True:
	for e in pg.event.get():
		if e.type == pg.MOUSEBUTTONUP:
			print e.pos


