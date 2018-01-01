"""
The module provides input events filter for pygame to ensure
correct handling of the touch-screen events. In addition it
provides several useful capabilities:
  - callbacks called in the context of the event loop
  - asynchronous jobs called once in the context of the event loop
    (for foreign threads safe interfacing)
  - timers called in the context of the event loop
Note that all above facilities are available regardless of the
particular event loop implementation. So this gives rather flexible
approach to extending existing code capabilities.
"""

import os
import threading
import pygame as pg
from events import read_events
import calibration

# Application instance
instance = None

def init():
	"""Create application instance singleton"""
	if instance is not None:
		return instance
	return Application()

class Timer(object):
	"""Timer object to be called in the context of the event loop"""
	def __init__(self, cb, interval, periodic):
		self.cb = cb
		self.interval = interval
		self.periodic = periodic

	def cancel(self):
		"""Cancel timer so it wont be fired anymore"""
		self.cb = None

class Application(object):

	def __init__(self):
		global instance
		assert instance is None
		self.pygame_init()
		inf = pg.display.Info()
		self.screen_w = inf.current_w
		self.screen_h = inf.current_h
		self.mouse_pos = None
		self.mouse_down = False
		self._down = None
		self.calib = calibration.load()
		self.event_loop_callbacks = []
		self.job_lock = threading.Lock()
		self.job_list = []
		self.timers = []
		instance = self

	def pygame_init(self):
		"""Proper initialize pygame module"""
		# stop reading events by pygame engine to avoid erratic mouse pointer behaviour
		os.putenv('SDL_MOUSEDEV', '/dev/null')
		pg.init()
		pg.display.init()
		pg.display.set_mode()
		pg.event.set_blocked((pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION))
		# install event filter
		self.pygame_get_events = pg.event.get
		pg.event.get = self.get_events

	def add_event_loop_callback(self, cb):
		"""Add callback to be called in event loop context"""
		self.event_loop_callbacks.append(cb)

	def run_callbacks(self):
		"""Execute registered callbacks"""
		for cb in self.event_loop_callbacks:
			cb()

	def add_job(self, job):
		"""Add job to be called once in event loop context"""
		with self.job_lock:
			self.job_list.append(job)

	def run_jobs(self):
		"""Execute registered jobs"""
		with self.job_lock:
			self.job_list, job_list = [], self.job_list
		for job in job_list:
			job()

	def add_timer(self, timer):
		"""Add timer object"""
		now = pg.time.get_ticks()
		self.timers.append((now + timer.interval, timer))
		self.timers.sort()

	def process_timers(self):
		"""Process registered timers"""
		now = pg.time.get_ticks()
		not_expired = len(self.timers)
		for i, (t, _) in enumerate(self.timers):
			if t > now:
				not_expired = i
				break
		if not not_expired:
			return
		expired, self.timers = self.timers[:not_expired], self.timers[not_expired:]
		rescheduled = False
		for due, timer in expired:
			if timer.cb:
				timer.cb()
			if timer.cb:
				if timer.periodic:
					self.timers.append((due + timer.interval, timer))
					rescheduled = True
				else:
					timer.cb = None
		if rescheduled:
			self.timers.sort()

	def get_events(self):
		"""Query events filter. This is the replacement for the pygame.event.get"""
		self.run_callbacks()
		self.run_jobs()
		self.process_timers()

		events = self.pygame_get_events()
		sys_events = read_events()

		for e in sys_events:
			if e.down is not None:
				self._down = e.down	
				if not self._down and self.mouse_down and self.mouse_pos:
					events.append(pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=self.mouse_pos))
					self.mouse_down = False
			if e.pos is not None:
				screen_pos = calibration.to_screen(e.pos, (self.screen_w, self.screen_h), self.calib)
				if self._down:
					if not self.mouse_down:
						events.append(pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=screen_pos))
						self.mouse_down = True
					elif self.mouse_pos and self.mouse_pos != screen_pos:
						events.append(pg.event.Event(
							pg.MOUSEMOTION, buttons=(1, 0, 0), pos=screen_pos, rel=(screen_pos[0]-self.mouse_pos[0], screen_pos[1]-self.mouse_pos[1])
						))
				self.mouse_pos = screen_pos
				pg.mouse.set_pos(*screen_pos)

		return events
