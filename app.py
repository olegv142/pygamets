import os
import pygame as pg
from events import read_events

os.putenv('SDL_MOUSEDEV', '/dev/null')

class Application(object):

	def __init__(self):
		self.mouse_pos = None
		self.mouse_down = False
		self._down = None
		inf = pg.display.Info()
		self.screen_w = inf.current_w
		self.screen_h = inf.current_h
		self.pygame_get_events = pg.event.get
		self.event_loop_callback = None
		pg.event.get = self.get_events
		pg.event.set_blocked((pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION))

	def set_event_loop_callback(self, cb):
		"""Set callback to be called on every event query. Returns previous callback."""
		old_cb = self.event_loop_callback
		self.event_loop_callback = cb
		return old_cb

	def raw_pos_to_screen(self, (x, y)):
		return self.screen_w * x // 4096, self.screen_h * y // 4096

	def get_events(self):
		"""Query events. This is the replacement for the pygame.event.get"""
		events = self.pygame_get_events()
		sys_events = read_events()

		for e in sys_events:
			if e.down is not None:
				self._down = e.down	
				if not self._down and self.mouse_down and self.mouse_pos:
					events.append(pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=self.mouse_pos))
					self.mouse_down = False
			if e.pos is not None:
				screen_pos = self.raw_pos_to_screen(e.pos)
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

		if self.event_loop_callback:
			self.event_loop_callback()

		return events
