#!/usr/bin/python

"""
Raw events reader test
"""

import sys, time
sys.path.append('..')
from pygamets import events

while True:
	time.sleep(.05)
	for e in events.read_events():
		print e

