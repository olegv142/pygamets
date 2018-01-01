#!/usr/bin/python

import sys, time
sys.path.append('..')

import events

while True:
	time.sleep(.05)
	for e in events.read_events():
		print e

