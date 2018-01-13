#!/usr/bin/python

"""
Test for pygame event loop with raw event
reader installed by app instance
"""

import sys, time
import pygame as pg

sys.path.append('..')
from pygamets import env
from pygamets import app

def print_event(e):
	def fn():
		print e
	return fn

cnt, last_cnt = 0, 0

def loop_counter():
	global cnt
	cnt += 1

def loop_timer():
	global last_cnt
	print cnt - last_cnt, 'loops per second'
	last_cnt = cnt

app.init()
app.instance.add_event_loop_callback(loop_counter)
app.instance.add_timer(app.Timer(loop_timer, 1000, periodic=True))
pg.display.set_mode()

while True:
	time.sleep(.01)
	for e in pg.event.get():
		app.instance.add_job(print_event(e))
