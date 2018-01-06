"""
GUI micro-framework core classes
"""

import pygame as pg

class View(object):
	"""The base class for all GUI elements"""
	def __init__(self, w, h):
		# The view occupies a rectangle in the parent coordinate system
		self.w, self.h = w, h
		self.x, self.y = None, None
		# The screen coordinates are unknown at the time of instance creation
		self.screen_x, self.screen_y = None, None
		self.parent = None
		self.children = []
		self.surface = None
		self.interactive = False
		self.has_focus = False

	def cover_rect(self, (x, y, w, h)):
		"""
		Returns True if the view area has non-empty intersection with given rect.
		The rect coordinates are assumed to be in the parent coordinate system.
		"""
		return not (
			x + w <= self.x or self.x + self.w <= x or
			y + h <= self.y or self.y + self.h <= y
		)

	def cover_screen_pos(self, (x, y)):
		"""Returns True if the view contains given point in the screen coordinate system"""
		return not (
			x < self.screen_x or self.screen_x + self.w <= x or
			y < self.screen_y or self.screen_y + self.h <= y
		)

	def origin(self):
		"""Calculates coordinates of the top-left corner in the screen coordinates system"""
		assert self.parent is not None
		px, py = self.parent.origin()
		return px + self.x, py + self.y

	def frame(self):
		"""Returns the occupied rectangle coordinates in screen coordinate system"""
		return self.screen_x, self.screen_y, self.w, self.h

	def rect_to_screen(self, (x, y, w, h)):
		"""Translates rectangle coordinates to the screen coordinate system"""
		return self.screen_x + x, self.screen_y + y, w, h

	def add_child(self, v, x, y):
		"""Add child view"""
		assert v.parent is None
		v.x, v.y = x, y
		v.parent = self
		self.children.append(v)
		
	def apply_recursively(self, cb):
		"""Call callback with the view as arguments and do it with all children recursively"""
		cb(self)
		for c in self.children:
			c.apply_recursively(cb)	

	def init(self, surface):
		"""Initialization routine called on first showing on the screen"""
		self.surface = surface
		self.screen_x, self.screen_y = self.origin()

	def initialized(self):
		return self.surface is not None

	def fini(self):
		"""Finalization routine called on removing from the screen"""
		self.surface = None

	def get_window(self):
		"""Returns window object"""
		assert self.parent is not None
		return self.parent.get_window()

	def get_screen(self):
		"""Returns screen object"""
		return self.get_window().get_screen()

	def draw(self):
		"""Draw routine to be implemented in subclasses"""
		pass

	def redraw(self):
		"""Draw this view and all children recursively"""
		self.draw()
		self.redraw_children()

	def redraw_children(self, rect = None):
		"""Redraw children and returns their list"""
		updated = []
		for c in self.children:
			if rect is None or c.cover_rect(rect):
				c.redraw()
				updated.append(c)
		return updated

	def update(self):
		"""Redraw if visible on the screen"""
		if not self.initialized():
			return
		s = self.get_screen()
		if s.is_visible(self):
			self.redraw()
			s.set_updated([self.frame()])

	def updated(self, rect = None):
		"""Notify the area is updated"""
		s = self.get_screen()
		assert s.is_visible(self)
		updated_children = self.redraw_children(rect)
		if rect is None:
			s.set_updated([self.frame()])
		else:
			updated = [self.rect_to_screen(rect)] + [c.frame() for c in updated_children]
			s.set_updated(updated)

	def find_interactive(self, pos):
		"""Find interactive view at given screen position"""
		if not self.cover_screen_pos(pos):
			return None
		for c in self.children:
			v = c.find_interactive(pos)
			if v is not None:
				return v
		if self.interactive:
			return self
		return None

	def set_focus(self, in_focus):
		"""Set/clear input focus"""
		assert self.interactive
		assert self.has_focus != in_focus
		self.has_focus = in_focus

	def on_mouse_event(self, e):
		"""Mouse event handler"""
		if e.type == pg.MOUSEBUTTONDOWN:
			self.on_pressed(True)
		elif e.type == pg.MOUSEBUTTONUP:
			self.on_pressed(False)
			if self.has_focus:
				self.on_clicked()

	def on_pressed(self, pressed):
		"""Mouse pressed callback to be implemented in the subclasses"""
		pass

	def on_clicked(self):
		"""Mouse clicked callback to be implemented in subclasses"""
		pass

class Window(View):
	"""The window is the top level view. Only top level window may receive input focus."""
	def __init__(self, x, y, w, h):
		View.__init__(self, w, h)
		self.x, self.y = x, y
		self.in_focus = None
		self.screen = None

	def origin(self):
		"""Returns the top-left corner coordinates in the screen coordinate system"""
		return self.x, self.y

	def clear_focus(self):
		"""Clear input focus"""
		if self.in_focus is not None:
			self.in_focus.set_focus(False)
		self.in_focus = None

	def discard(self):
		"""Remove window from the screen"""
		self.get_screen().discard(self)

	def fini(self):
		"""Finalization routine called on removing window from the screen"""
		self.clear_focus()
		View.fini(self)

	def get_window(self):
		"""Get window object (self)"""
		return self

	def get_screen(self):
		"""Get screen object"""
		assert self.screen is not None
		return self.screen

	def deliver_mouse_event(self, e):
		"""Mouse events handler"""
		if e.type == pg.MOUSEBUTTONDOWN:
			if self.in_focus is not None:
				self.in_focus.set_focus(False)
			self.in_focus = self.find_interactive(e.pos)
			if self.in_focus is not None:
				self.in_focus.set_focus(True)
				self.in_focus.on_mouse_event(e)
		elif e.type == pg.MOUSEBUTTONUP:
			if self.in_focus is not None:
				in_focus = self.in_focus
				lost_focus = self.find_interactive(e.pos) != in_focus
				if lost_focus:
					in_focus.set_focus(False)
					self.in_focus = None
				in_focus.on_mouse_event(e)
		elif e.type == pg.MOUSEMOTION:
			if self.in_focus is not None:
				self.in_focus.on_mouse_event(e)

	def deliver_event(self, e):
		"""Non-mouse events handler to be implemented in subclasses if necessary"""
		return False

class Screen(object):
	"""The screen object implements the ordered list of windows and maintain the list of updated areas"""
	def __init__(self):
		self.surface = None
		self.windows = []
		self.updated = set()
		self.updated_all = False
		self.run_clock = None

	def init_mode(self, mode = None):
		"""Init display mode"""
		if mode is not None:
			self.surface = pg.display.set_mode(mode)
		else:
			self.surface = pg.display.set_mode()

	def size(self):
		"""Returns display size as (w, h) pair"""
		if self.surface is not None:
			return self.surface.get_size()
		else:
			return None

	def show(self, wnd):
		"""Show given window on the screen"""
		assert self.surface is not None
		if self.windows:
			self.windows[-1].clear_focus()
		wnd.screen = self
		self.windows.append(wnd)
		wnd.apply_recursively(lambda v: v.init(self.surface))
		wnd.redraw()
		self.set_updated([wnd.frame()])

	def discard(self, wnd):
		"""Remove given window from the screen"""
		wnd.apply_recursively(lambda v: v.fini())
		wnd.screen = None
		self.windows.remove(wnd)
		self.redraw()

	def is_visible(self, v):
		"""Returns True if given view is visible"""
		f, wnd = v.frame(), v.get_window()
		i = self.windows.index(wnd)
		for w in self.windows[i+1:]:
			if w.cover_rect(f):
				return False
		return True

	def redraw(self):
		"""Redraw all windows"""
		for w in self.windows:
			w.redraw()
		self.set_updated()

	def set_updated(self, rects = None):
		"""Notify the given area is updated"""
		if rects is None:
			self.updated_all = True
		else:
			self.updated.update(rects)

	def refresh(self):
		"""Update display for all updated areas"""
		if self.updated_all:
			pg.display.update()
		elif self.updated:
			pg.display.update([frame for frame in self.updated])
		self.updated = set()
		self.updated_all = False

	def deliver_mouse_event(self, e):
		"""Route mouse event to proper window"""
		self.windows[-1].deliver_mouse_event(e)

	def deliver_event(self, e):
		"""Route non-mouse event to proper window"""
		for w in reversed(self.windows):
			if w.deliver_event(e):
				break

	def handle_event(self, e):
		"""Event handler"""
		if e.type == pg.MOUSEBUTTONDOWN or e.type == pg.MOUSEBUTTONUP or e.type == pg.MOUSEMOTION:
			self.deliver_mouse_event(e)
		else:
			self.deliver_event(e)

	def run_event_loop(self, max_fps = 0):
		"""Run event loop optionally limiting fps rate"""
		self.run_clock = pg.time.Clock()
		try:
			while True:
				self.run_clock.tick(max_fps)
				for e in pg.event.get():
					self.handle_event(e)
					if e.type == pg.QUIT:
						return
				self.refresh()
		finally:
			self.run_clock = None

	def is_running(self):
		"""Returns True if event loop is running"""
		return self.run_clock is not None

	def get_fps(self):
		"""Get event loop execution count per second"""
		if self.is_running():
			return self.run_clock.get_fps()
		else:
			return None

class Signal(object):
	"""The signal is callable object with callback registry"""
	def __init__(self):
		self.targets = []

	def connect(self, cb):
		"""Register callback"""
		assert callable(cb)
		self.targets.append(cb)

	def __call__(self, *args, **kwargs):
		"""Call all registered callbacks with the same arguments"""
		for cb in self.targets:
			cb(*args, **kwargs)

class Button(View):
	"""The button is interactive view with several ready to use signals"""
	def __init__(self, w, h):
		View.__init__(self, w, h)
		self.interactive = True
		self.is_pressed = False
		self.clicked = Signal()
		self.pressed = Signal()
		self.focus_changed = Signal()

	def on_pressed(self, pressed):
		"""Mouse pressed handler"""
		self.is_pressed = pressed
		self.pressed(pressed)

	def on_clicked(self):
		"""Mouse clicked handler"""
		self.clicked()

	def set_focus(self, in_focus):
		"""Focus set/clear handler"""
		View.set_focus(self, in_focus)
		self.focus_changed(in_focus)

def quit():
	"""Quit event loop by posting QUIT event"""
	pg.event.post(pg.event.Event(pg.QUIT))
